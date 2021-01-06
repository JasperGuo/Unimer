# coding=utf8

import re
import copy
import numpy as np
from typing import Iterable, Callable, List, Dict
from overrides import overrides
from allennlp.data import Instance, Tokenizer
from allennlp.data.fields import TextField, ArrayField, MetadataField
from allennlp.common.util import START_SYMBOL, END_SYMBOL
from allennlp.data.dataset_readers import DatasetReader
from allennlp.data.tokenizers import Token
from allennlp.data.token_indexers import SingleIdTokenIndexer


class GNNCopyTransformerDataReader(DatasetReader):

    SEP_SYMBOL = "@sep@"
    TOKEN_SYMBOL = "@token@"
    ENTITY_SYMBOL = "@entity@"
    NON_FUNC_SYMBOL = "@nonfunc@"
    TARGET_SYMBOL = "@target@"

    def __init__(self,
                 entity_matcher,
                 entity_replacer,
                 target_grammar,
                 source_tokenizer: Tokenizer,
                 target_tokenizer: Tokenizer,
                 logical_form_preprocessor: Callable = None,
                 lazy: bool = False,
                 nlabels: int = 4,
                 relative_position_clipped_range: int = 8,
                 allow_drop: bool = False) -> None:
        super().__init__(lazy=lazy)

        self._entity_matcher = entity_matcher
        self._entity_replacer = entity_replacer
        self._target_grammar = target_grammar
        self._source_namespace = 'source_tokens'
        self._target_namespace = 'target_tokens'
        self._segment_namespace = 'segment_tokens'
        self._source_tokenizer = source_tokenizer
        self._target_tokenizer = target_tokenizer
        self._source_token_indexers = {'tokens': SingleIdTokenIndexer(namespace='source_tokens')}
        self._target_token_indexers = {
            "tokens": SingleIdTokenIndexer(namespace=self._target_namespace)
        }
        self._segment_token_indexers = {
            "tokens": SingleIdTokenIndexer(namespace=self._segment_namespace)
        }
        self._nlabels = nlabels
        self._relative_position_clipped_range = relative_position_clipped_range
        self._logical_form_preprocessor = logical_form_preprocessor
        self._allow_drop = allow_drop

    @overrides
    def text_to_instance(self, source_string: str, target_string: str = None) -> Instance:
        """
        Turn raw source string and target string into an ``Instance``.
        Parameters
        ----------
        source_string : ``str``, required
        target_string : ``str``, optional (default = None)
        Returns
        -------
        Instance
            See the above for a description of the fields that the instance will contain.
        """
        tokenized_source = self._source_tokenizer.tokenize(source_string)
        tokenized_source.insert(0, Token(START_SYMBOL))
        tokenized_source.append(Token(END_SYMBOL))
        segments = [Token(self.TOKEN_SYMBOL) for i in range(len(tokenized_source))]

        source_entity_length = [1 for i in range(len(tokenized_source))]
        token_length = len(segments)

        pseudo_tokens = [t.text for t in tokenized_source]

        candidates = self._entity_matcher.match(tokenized_source)

        diff = 0
        if len(candidates) > 0:
            for entity in candidates:
                value = entity['value'].replace('_', ' ')
                words = value.split()
                for v in words:
                    tokenized_source.append(Token(v))
                segments.append(Token(entity['type']))
                diff += 0 if len(words) == 1 else len(words) - 1
                entity['index'] = len(pseudo_tokens)
                source_entity_length.append(len(words))
                pseudo_tokens.append(value)

            tokenized_source.append(Token(self.SEP_SYMBOL))
            source_entity_length.append(1)
            segments.append(Token(self.NON_FUNC_SYMBOL))

            pseudo_tokens.append(self.SEP_SYMBOL)
        else:
            tokenized_source.append(Token(self.SEP_SYMBOL))
            source_entity_length.append(1)
            segments.append(Token(self.NON_FUNC_SYMBOL))

            pseudo_tokens.append(self.SEP_SYMBOL)

        assert len(tokenized_source) == len(segments) + diff and sum(source_entity_length) == len(tokenized_source) \
               and len(pseudo_tokens) == len(segments) and len(pseudo_tokens) == len(source_entity_length)

        source_field = TextField(tokenized_source, self._source_token_indexers)
        fields_dict = {'source_tokens': source_field,
                       'source_entity_length': ArrayField(np.array(source_entity_length, dtype=np.int),padding_value=0),
                       'segments': TextField(segments, self._segment_token_indexers)}

        # TODO: fix edge mask
        edge_mask = self.get_edge_mask(tokenized_source, token_length, len(segments), pseudo_tokens, candidates)
        fields_dict['edge_mask'] = ArrayField(edge_mask)

        preprocessed_target_string = self._logical_form_preprocessor(target_string)
        meta_field = {
            'target': target_string,
            'pseudo_tokens': pseudo_tokens,
            'entity_candidates': candidates,
            'token_length': token_length
        }
        tokenized_target = self._target_tokenizer.tokenize(preprocessed_target_string)
        tokenized_target.insert(0, Token(START_SYMBOL))
        tokenized_target.append(Token(END_SYMBOL))

        is_valid, replaced_target_tokens = self._entity_replacer(self._target_grammar,
                                                                 preprocessed_target_string,
                                                                 tokenized_target, candidates)
        if not is_valid and self._allow_drop:
            return None

        target_field = TextField(replaced_target_tokens, self._target_token_indexers)
        fields_dict['target_tokens'] = target_field

        target_action_sequence = np.zeros(len(replaced_target_tokens), dtype=np.int)
        copy_targets = list()
        train_entity_appear_indicator = np.zeros(len(pseudo_tokens))
        for tidx, token in enumerate(replaced_target_tokens):
            ct = np.zeros(len(segments))
            match = re.match('^@entity_(\d+)', token.text)
            if match:
                index = int(match.group(1))
                target_action_sequence[tidx] = index
                ct[index] = 1
            copy_targets.append(ct)

        fields_dict['copy_targets'] = ArrayField(np.array(copy_targets))
        fields_dict['generate_targets'] = ArrayField(target_action_sequence)
        fields_dict['meta_field'] = MetadataField(meta_field)

        return Instance(fields_dict)

    def get_edge_mask(self, tokenized_source: List[Token], token_length: int, segment_length: int,
                      pseudo_tokens: List[str], candidates: List[Dict]):
        entity_length = segment_length - token_length

        # Edge Labels
        token_edges = np.zeros((2 * self._relative_position_clipped_range + 1, segment_length, segment_length))
        for st_i_idx, st_i in enumerate(tokenized_source[:token_length]):
            for st_j_idx, st_j in enumerate(tokenized_source[:token_length]):
                distance = st_j_idx - st_i_idx
                if distance > self._relative_position_clipped_range:
                    distance = self._relative_position_clipped_range
                elif distance < - self._relative_position_clipped_range:
                    distance = - self._relative_position_clipped_range
                token_edges[distance, st_i_idx, st_j_idx] = 1

        entity_edges = np.pad(np.ones((entity_length, entity_length), dtype=np.int),
                              ((token_length, 0), (token_length, 0)), mode='constant', constant_values=0)

        token_in_entity_edges = np.zeros((segment_length, segment_length), dtype=np.int)
        token_not_in_entity_edges = np.zeros((segment_length, segment_length), dtype=np.int)
        if len(candidates) > 0 and 'indices' in candidates[0]:
            # Use indices
            for candidate in candidates:
                for tidx in range(token_length):
                    if tidx in candidate['indices']:
                        token_in_entity_edges[tidx, candidate['index']] = 1
                        token_in_entity_edges[candidate['index'], tidx] = 1
                    else:
                        token_not_in_entity_edges[tidx, candidate['index']] = 1
                        token_not_in_entity_edges[candidate['index'], tidx] = 1
        else:
            for st_idx, st in enumerate(pseudo_tokens[:token_length]):
                for e_idx, e in enumerate(pseudo_tokens[token_length:]):
                    # if st == e:
                    if st in e.split():
                        # print(st, " in ", e)
                        token_in_entity_edges[st_idx, token_length + e_idx] = 1
                        token_in_entity_edges[token_length + e_idx, st_idx] = 1
                    else:
                        token_not_in_entity_edges[st_idx, token_length + e_idx] = 1
                        token_not_in_entity_edges[token_length + e_idx, st_idx] = 1

        edge_masks = np.stack((entity_edges, token_in_entity_edges, token_not_in_entity_edges),
                              axis=0)
        # shape: (2k + 1 + 3, source_length, source_length)
        edge_masks = np.concatenate((token_edges, edge_masks), axis=0)
        return edge_masks

    @overrides
    def _read(self, file_path: str) -> Iterable[Instance]:
        with open(file_path, 'r') as data_file:
            for line in data_file:
                line = line.strip()
                if not line:
                    continue
                line_parts = line.split('\t')
                assert len(line_parts) == 2
                instance = self.text_to_instance(line_parts[0], line_parts[1])
                if instance is None:
                    continue
                else:
                    yield instance
