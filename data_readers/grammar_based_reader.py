# coding=utf-8

import re
import os
import json
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Iterator, List, Dict, Iterable, Tuple, Callable
from overrides import overrides
from allennlp.data import Instance
from allennlp.data.fields import TextField, ArrayField, NamespaceSwappingField, MetadataField
from allennlp.common.util import START_SYMBOL, END_SYMBOL
from allennlp.data.dataset_readers import DatasetReader
from allennlp.data.tokenizers import Token, Tokenizer, WordTokenizer
from allennlp.data.token_indexers import TokenIndexer, SingleIdTokenIndexer
from allennlp.data.vocabulary import Vocabulary


class GrammarBasedDataReader(DatasetReader):
    def __init__(self, source_tokenizer, grammar, logical_form_preprocessor: Callable = None, maximum_target_length: int = 0, lazy: bool = False) -> None:
        super().__init__(lazy)
        self._source_tokenizer = source_tokenizer
        self._source_token_indexers = {
            'tokens': SingleIdTokenIndexer(namespace='source_tokens')}
        self._grammar = grammar
        self._target_token_indexers = {
            'tokens': SingleIdTokenIndexer(namespace='target_tokens')}
        self.rule_pad_index = 0
        self.nonterminal_pad_index = self._grammar.num_non_terminals
        self.nonterminal_end_index = self._grammar.num_non_terminals + 1
        self._logical_form_preprocessor = logical_form_preprocessor
        self._maximum_target_length = maximum_target_length

    @property
    def grammar(self):
        return self._grammar

    @overrides
    def text_to_instance(self, question: str = None, logical_form: str = None) -> Instance:
        tokenized_source = self._source_tokenizer.tokenize(question)
        tokenized_source.insert(0, Token(START_SYMBOL))
        tokenized_source.append(Token(END_SYMBOL))
        source_field = TextField(tokenized_source, self._source_token_indexers)
        fields_dict = {'source_tokens': source_field}
        meta_data = {
            'question': question
        }
        if logical_form is not None:
            if self._logical_form_preprocessor:
                logical_form = self._logical_form_preprocessor(logical_form)
            # else:
                # logical_form = logical_form.replace(' ', '').replace("'", "").lower()
            # TODO: this can be a potential threat to remove lower
            # logical_form = logical_form.lower()
            applied_production_rules = self._grammar.parse(logical_form)
            rule_ids, nonterminal_ids = list(), list()
            for rule in applied_production_rules:
                assert rule.rule_id > 0
                rule_ids.append(rule.rule_id)
                lhs = rule.lhs
                nonterminal_ids.append(self._grammar.get_non_terminal_id(lhs))
            nonterminal_ids = nonterminal_ids[1:] + \
                [self.nonterminal_end_index]
            assert len(rule_ids) == len(nonterminal_ids)

            if self._maximum_target_length > 0 and len(rule_ids) > self._maximum_target_length:
                return None

            fields_dict.update({
                "target_rules": ArrayField(np.array(rule_ids, dtype=int), padding_value=self.rule_pad_index),
                "target_nonterminals": ArrayField(np.array(nonterminal_ids, dtype=int), padding_value=self.nonterminal_pad_index),
                "target_mask": ArrayField(np.ones(len(rule_ids)), padding_value=0),
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
