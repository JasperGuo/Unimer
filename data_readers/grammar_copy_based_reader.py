# coding=utf-8

import numpy as np
from typing import Iterable, Callable
from overrides import overrides
from allennlp.data import Instance
from allennlp.data.fields import TextField, ArrayField, MetadataField
from allennlp.common.util import START_SYMBOL, END_SYMBOL
from allennlp.data.dataset_readers import DatasetReader
from allennlp.data.tokenizers import Token
from allennlp.data.token_indexers import SingleIdTokenIndexer


class GrammarCopyBasedDataReader(DatasetReader):
    def __init__(self, source_tokenizer, grammar, copy_link_finder, logical_form_preprocessor: Callable = None,
                 utterance_preprocessor: Callable = None,
                 maximum_target_length: int = 0, lazy: bool = False) -> None:
        super().__init__(lazy)
        self._source_tokenizer = source_tokenizer
        self._source_token_indexers = {
            'tokens': SingleIdTokenIndexer(namespace='source_tokens')}
        self._grammar = grammar
        assert self._grammar.copy_terminal_set is not None
        self._target_token_indexers = {
            'tokens': SingleIdTokenIndexer(namespace='target_tokens')}
        self.rule_pad_index = 0
        self.nonterminal_pad_index = self._grammar.num_non_terminals
        self.nonterminal_end_index = self._grammar.num_non_terminals + 1
        self._logical_form_preprocessor = logical_form_preprocessor
        self._utterance_preprocessor = utterance_preprocessor
        self._maximum_target_length = maximum_target_length
        self._copy_link_finder = copy_link_finder

    @property
    def grammar(self):
        return self._grammar

    @overrides
    def text_to_instance(self, question: str = None, logical_form: str = None) -> Instance:
        if self._utterance_preprocessor:
            question = self._utterance_preprocessor(question)
        tokenized_source = self._source_tokenizer.tokenize(question)
        tokenized_source.insert(0, Token(START_SYMBOL))
        tokenized_source.append(Token(END_SYMBOL))
        source_field = TextField(tokenized_source, self._source_token_indexers)
        fields_dict = {'source_tokens': source_field}
        meta_data = {
            'question': question
        }
        if self._logical_form_preprocessor:
            logical_form = self._logical_form_preprocessor(logical_form)
        # logical_form = logical_form.lower()
        applied_production_rules = self._grammar.parse(logical_form)
        rule_ids, nonterminal_ids = list(), list()
        # Allow copy mask
        allow_copy_mask = list()
        for rule in applied_production_rules:
            assert rule.rule_id > 0
            rule_ids.append(rule.rule_id)
            lhs = rule.lhs
            nonterminal_ids.append(self._grammar.get_non_terminal_id(lhs))
            if rule.lhs in self._grammar.copy_terminal_set:
                allow_copy_mask.append(1)
            else:
                allow_copy_mask.append(0)
        nonterminal_ids = nonterminal_ids[1:] + \
            [self.nonterminal_end_index]
        allow_copy_mask = allow_copy_mask[1:] + [0]
        assert len(rule_ids) == len(nonterminal_ids) and len(rule_ids) == len(allow_copy_mask)

        if self._maximum_target_length > 0 and len(rule_ids) > self._maximum_target_length:
            return None

        # Copy Mask
        copy_pad_index = self._grammar.root_rule_id
        token_copy_index = self._copy_link_finder.match(
            tokenized_source, self._grammar.production_rules, self._grammar.copy_terminal_set, copy_pad_index)
        assert len(token_copy_index) == len(tokenized_source)
        # Pad
        maximum_match = max([len(m) for m in token_copy_index])
        for idx, copy_index in enumerate(token_copy_index):
            token_copy_index[idx] = np.concatenate([copy_index, np.ones(
                maximum_match - len(copy_index), dtype=np.int) * copy_pad_index])
        token_copy_index = np.array(token_copy_index)

        fields_dict.update({
            "target_rules": ArrayField(np.array(rule_ids, dtype=int), padding_value=self.rule_pad_index),
            "target_nonterminals": ArrayField(np.array(nonterminal_ids, dtype=int), padding_value=self.nonterminal_pad_index),
            "target_mask": ArrayField(np.ones(len(rule_ids)), padding_value=0),
            "source_token_copy_indices": ArrayField(token_copy_index, padding_value=copy_pad_index, dtype=np.int),
            "target_allow_copy_mask": ArrayField(np.array(allow_copy_mask, dtype=int), padding_value=0)
        })
        meta_data.update({'logical_form': logical_form})
        fields_dict.update({
            "meta_field": MetadataField(meta_data)
        })
        return Instance(fields_dict)

    @overrides
    def _read(self, file_path: str) -> Iterable[Instance]:
        with open(file_path, 'r') as data_file:
            for line in data_file:
                line = line.strip()
                if not line:
                    continue
                line_parts = line.split('\t')
                assert len(line_parts) == 2
                inst = self.text_to_instance(line_parts[0], line_parts[1])
                if inst is not None:
                    yield self.text_to_instance(line_parts[0], line_parts[1])
