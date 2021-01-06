# coding=utf8

import numpy
import torch
import torch.nn as nn
from typing import Dict, List
from overrides import overrides
from allennlp.training.metrics import Metric
from allennlp.models.model import Model
from allennlp.data.vocabulary import Vocabulary
from allennlp.nn import util
from allennlp.modules.text_field_embedders import BasicTextFieldEmbedder
from .modules.grammar_copy_decoder import LSTMGrammarCopyDecoder
from .modules.grammar_copy_decoder_2 import LSTMGrammarCopyDecoder as LSTMGrammarCopyDecoder2


class GrammarModel(Model):
    def __init__(self, vocab: Vocabulary, source_embedder: BasicTextFieldEmbedder, encoder, decoder, metric, flags, regularizer=None):
        super().__init__(vocab, regularizer=regularizer)
        self._source_embedder = source_embedder
        self._encoder = encoder
        self._encoder_input_dropout = nn.Dropout(p=flags.encoder_input_dropout)
        self._encoder_output_dropout = nn.Dropout(
            p=flags.encoder_output_dropout)
        self._decoder = decoder
        self._metric = metric

    @overrides
    def forward(self,
                source_tokens: Dict[str, torch.LongTensor],
                source_token_copy_indices: torch.Tensor = None,
                target_rules: torch.LongTensor = None,
                target_nonterminals: torch.LongTensor = None,
                target_mask: torch.LongTensor=None,
                target_allow_copy_mask: torch.Tensor = None,
                meta_field: List[Dict] = None,):
        state = self.encode(source_tokens)
        if isinstance(self._decoder, LSTMGrammarCopyDecoder) or isinstance(self._decoder, LSTMGrammarCopyDecoder2):
            output_dict = self._decoder(
                encodings=state['encoder_outputs'],
                source_mask=state['source_mask'],
                source_token_copy_indices=source_token_copy_indices,
                target_rules=target_rules,
                target_nonterminals=target_nonterminals,
                target_mask=target_mask,
                target_allow_copy_mask=target_allow_copy_mask,
                meta_field=meta_field
            )
        else:
            output_dict = self._decoder(
                encodings=state['encoder_outputs'],
                source_mask=state['source_mask'],
                target_rules=target_rules,
                target_nonterminals=target_nonterminals,
                target_mask=target_mask,
                meta_field=meta_field
            )
        if self.training:
            self._metric(output_dict['predicted_rules'].float(
            ), gold_labels=target_rules[:, 1:].float(), mask=target_mask[:, 1:].float())
        else:
            self._metric(output_dict['predicted_rules'].float(
            ), gold_labels=target_rules.float(), mask=target_mask.float())
        return output_dict

    def encode(self, source_tokens: Dict[str, torch.LongTensor]):
        # shape: (batch_size, max_input_sequence_length, encoder_input_dim)
        embedded_input = self._source_embedder(source_tokens)
        # shape: (batch_size, max_input_sequence_length)
        source_mask = util.get_text_field_mask(source_tokens)
        # shape: (batch_size, max_input_sequence_length, encoder_output_dim)
        embedded_input = self._encoder_input_dropout(embedded_input)
        encoder_outputs = self._encoder(embedded_input, source_mask)

        encoder_outputs = self._encoder_output_dropout(encoder_outputs)

        return {
            "source_mask": source_mask,
            "encoder_outputs": encoder_outputs,
        }

    @overrides
    def get_metrics(self, reset: bool = False) -> Dict[str, float]:
        accuracy = self._metric.get_metric(reset)['accuracy']
        return {"accuracy": accuracy}
