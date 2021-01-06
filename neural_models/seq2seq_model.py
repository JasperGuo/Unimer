# coding=utf8

import torch
from overrides import overrides
from typing import Dict, List, Tuple
from allennlp.training.metrics import Metric
from allennlp.models.model import Model
from allennlp.data.vocabulary import Vocabulary
from allennlp.nn import util
from allennlp.modules import Attention, TextFieldEmbedder, Seq2SeqEncoder
from allennlp.models.encoder_decoders.simple_seq2seq import SimpleSeq2Seq
from allennlp.modules.similarity_functions import SimilarityFunction


class Seq2SeqModel(SimpleSeq2Seq):

    def __init__(self,
                 vocab: Vocabulary,
                 source_embedder: TextFieldEmbedder,
                 encoder: Seq2SeqEncoder,
                 max_decoding_steps: int,
                 attention: Attention = None,
                 attention_function: SimilarityFunction = None,
                 beam_size: int = None,
                 target_namespace: str = "tokens",
                 target_embedding_dim: int = None,
                 scheduled_sampling_ratio: float = 0.,
                 use_bleu: bool = True,
                 seq_metrics=None) -> None:

        self._seq_metric = seq_metrics
        super(Seq2SeqModel, self).__init__(
            vocab,
            source_embedder,
            encoder,
            max_decoding_steps,
            attention,
            attention_function,
            beam_size,
            target_namespace,
            target_embedding_dim,
            scheduled_sampling_ratio,
            use_bleu)

    @overrides
    def forward(self,  # type: ignore
                source_tokens: Dict[str, torch.LongTensor],
                target_tokens: Dict[str, torch.LongTensor] = None) -> Dict[str, torch.Tensor]:
        state = self._encode(source_tokens)

        if target_tokens:
            state = self._init_decoder_state(state)
            # The `_forward_loop` decodes the input sequence and computes the loss during training
            # and validation.
            output_dict = self._forward_loop(state, target_tokens)
        else:
            output_dict = {}

        if not self.training:
            state = self._init_decoder_state(state)
            predictions = self._forward_beam_search(state)
            output_dict.update(predictions)
            if target_tokens:
                # shape: (batch_size, beam_size, max_sequence_length)
                top_k_predictions = output_dict["predictions"]
                # shape: (batch_size, max_predicted_sequence_length)
                best_predictions = top_k_predictions[:, 0, :]
                if self._bleu:
                    self._bleu(best_predictions, target_tokens["tokens"])
                if self._seq_metric:
                    self._seq_metric(
                        best_predictions.float(),
                        gold_labels=target_tokens["tokens"][:, 1:].float(),
                        mask=util.get_text_field_mask(
                            target_tokens).float()[:, 1:]
                    )

        return output_dict

    @overrides
    def get_metrics(self, reset: bool = False) -> Dict[str, float]:
        all_metrics: Dict[str, float] = {}
        if not self.training:
            if self._bleu:
                all_metrics.update(self._bleu.get_metric(reset=reset))
            if self._seq_metric:
                all_metrics.update(
                    {"accuracy": self._seq_metric.get_metric(reset)['accuracy']})
        return all_metrics
