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


class Seq2SeqDataReader(DatasetReader):

    COPY_TOKEN = '@copy@'

    def __init__(self, question_tokenizer, logical_form_tokenizer,
                 logical_form_preprocessor: Callable = None,
                 lazy: bool = False, is_parsing=False,
                 enable_copy: bool = False, maximum_target_length: int = 0,
                 entity_matcher = None,
                 exclude_target_words = None) -> None:
        super().__init__(lazy=lazy)
        self._question_tokenizer = question_tokenizer
        self._logical_form_tokenizer = logical_form_tokenizer
        self._is_parsing = is_parsing
        self._source_token_indexers = {
            "tokens": SingleIdTokenIndexer(namespace='source_tokens')}
        self._target_token_indexers = {
            "tokens": SingleIdTokenIndexer(namespace='target_tokens')}
        self._logical_form_preprocessor = logical_form_preprocessor
        self._maximum_target_length = maximum_target_length
        self._enable_copy = enable_copy
        self._entity_matcher = entity_matcher
        self._exclude_target_words = exclude_target_words

    @overrides
    def text_to_instance(self, logical_form: str, question: str = None) -> Instance:

        if self._logical_form_preprocessor:
            logical_form = self._logical_form_preprocessor(logical_form)
        logical_form = logical_form.lower()

        if self._is_parsing:
            tokenized_source = self._question_tokenizer.tokenize(question)
        else:
            tokenized_source = self._logical_form_tokenizer.tokenize(logical_form)
        tokenized_source.insert(0, Token(START_SYMBOL))
        tokenized_source.append(Token(END_SYMBOL))
        source_field = TextField(tokenized_source, self._source_token_indexers)
        fields_dict = {'source_tokens': source_field}
        if self._is_parsing:
            tokenized_target = self._logical_form_tokenizer.tokenize(
                logical_form)
        else:
            tokenized_target = self._question_tokenizer.tokenize(question)
        tokenized_target.insert(0, Token(START_SYMBOL))
        tokenized_target.append(Token(END_SYMBOL))

        if self._maximum_target_length > 0 and len(tokenized_target) > self._maximum_target_length:
            return None

        target_field = TextField(
            tokenized_target, self._target_token_indexers)
        fields_dict.update({
            "target_tokens": target_field
        })
        if self._enable_copy:
            if self._entity_matcher is None:
                source_tokens_to_copy = [t.text for t in tokenized_source]
            else:
                source_tokens_to_copy = [self.COPY_TOKEN if t is None else t for t in self._entity_matcher.match(tokenized_source)]
            # Prepare target_source_token_map
            map_ids = list()
            for target_token in tokenized_target:
                if target_token.text in [START_SYMBOL, END_SYMBOL]:
                    map_ids.append(np.zeros(len(tokenized_source)))
                elif self._exclude_target_words is not None and target_token.text.lower() in self._exclude_target_words:
                    map_ids.append(np.zeros(len(tokenized_source)))
                else:
                    map_result = list()
                    for st in source_tokens_to_copy:
                        if st in [START_SYMBOL, END_SYMBOL, self.COPY_TOKEN]:
                            map_result.append(0)
                        else:
                            if st == target_token.text:
                                map_result.append(1)
                            else:
                                map_result.append(0)
                    map_ids.append(np.array(map_result))
            meta_data = {
                'source_tokens_to_copy': source_tokens_to_copy
            }
            fields_dict.update({
                "target_source_token_map": ArrayField(np.array(map_ids, dtype=int), padding_value=0),
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
                inst = self.text_to_instance(line_parts[1], line_parts[0])
                if inst is not None:
                    yield inst
