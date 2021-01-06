# coding=utf8

import numpy
import torch
from typing import Dict, Tuple, Union, List, Any
from allennlp.models import SimpleSeq2Seq
from allennlp.data.vocabulary import Vocabulary
from allennlp.modules import TextFieldEmbedder, Seq2SeqEncoder, Attention, SimilarityFunction
from allennlp.nn import util, InitializerApplicator
from allennlp.training.metrics import Metric
from overrides import overrides
from torch.nn import Linear, LSTMCell


class RecombinationSeq2Seq(SimpleSeq2Seq):
    """
    Neural Architecture taken from "Data Recombination for Neural Semantic Parsing"
    """
    def __init__(self,
                 vocab: Vocabulary,
                 source_embedder: TextFieldEmbedder,
                 encoder: Seq2SeqEncoder,
                 max_decoding_steps: int,
                 seq_metrics: Metric,
                 input_attention: Attention = None,
                 input_attention_function: SimilarityFunction = None,
                 beam_size: int = None,
                 target_namespace: str = "tokens",
                 target_embedding_dim: int = None,
                 scheduled_sampling_ratio: float = 0.,
                 use_bleu: bool = True,
                 encoder_input_dropout: int = 0.0,
                 encoder_output_dropout: int = 0.0,
                 dropout=0.0,
                 output_attention: Attention = None,
                 feed_output_attention_to_decoder: bool = False,
                 keep_decoder_output_dim_same_as_encoder: bool = True,
                 initializer: InitializerApplicator = InitializerApplicator()) -> None:

        super().__init__(vocab, source_embedder, encoder, max_decoding_steps, input_attention,
                         input_attention_function, beam_size, target_namespace, target_embedding_dim,
                         scheduled_sampling_ratio, use_bleu)
        self._seq_metric = seq_metrics
        self._pad_index = self.vocab.get_token_index(self.vocab._padding_token,
                                                     self._target_namespace)  # pylint: disable=protected-access
        self._output_attention = output_attention
        self._encoder_input_dropout = torch.nn.Dropout(p=encoder_input_dropout)
        self._encoder_output_dropout = torch.nn.Dropout(p=encoder_output_dropout)
        self._output_dropout = torch.nn.Dropout(p=dropout)
        self._embedded_dropout = torch.nn.Dropout(p=dropout)

        self._feed_output_attention_to_decoder = feed_output_attention_to_decoder
        self._keep_decoder_output_dim_same_as_encoder = keep_decoder_output_dim_same_as_encoder

        if not self._keep_decoder_output_dim_same_as_encoder:
            self._decoder_output_dim = int(self._encoder_output_dim / 2) if encoder.is_bidirectional() \
                else self._encoder_output_dim

        self._transform_decoder_init_state = torch.nn.Sequential(
            torch.nn.Tanh(),
            torch.nn.Linear(self._encoder_output_dim, self._decoder_output_dim)
        )

        if self._feed_output_attention_to_decoder:
            self._decoder_input_dim = target_embedding_dim + self._encoder_output_dim
            self._decoder_cell = LSTMCell(self._decoder_input_dim, self._decoder_output_dim)
        else:
            self._decoder_cell = LSTMCell(self._decoder_input_dim, self._decoder_output_dim)

        num_classes = self.vocab.get_vocab_size(self._target_namespace)
        if self._output_attention:
            # self._fuse_decoder_hidden_attention_layout = torch.nn.Sequential(torch.nn.Tanh(), Linear(
            #     self._decoder_output_dim * 2, self._decoder_output_dim
            # ))
            self._output_projection_layer = Linear(self._decoder_output_dim + self._encoder_output_dim, num_classes)
        else:
            self._output_projection_layer = Linear(self._decoder_output_dim, num_classes)

        initializer(self)

    def _prepare_output_attended_input(self,
                                       decoder_hidden_state: torch.LongTensor = None,
                                       encoder_outputs: torch.LongTensor = None,
                                       encoder_outputs_mask: torch.LongTensor = None) -> torch.Tensor:
        """Apply ouput attention over encoder outputs and decoder state."""
        # Ensure mask is also a FloatTensor. Or else the multiplication within
        # attention will complain.
        # shape: (batch_size, max_input_sequence_length)
        encoder_outputs_mask = encoder_outputs_mask.float()

        # shape: (batch_size, max_input_sequence_length)
        input_weights = self._output_attention(
            decoder_hidden_state, encoder_outputs, encoder_outputs_mask)

        # shape: (batch_size, encoder_output_dim)
        attended_input = util.weighted_sum(encoder_outputs, input_weights)

        return attended_input

    @overrides
    def _prepare_output_projections(self,
                                    last_predictions: torch.Tensor,
                                    state: Dict[str, torch.Tensor]) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        # pylint: disable=line-too-long
        """
        Decode current state and last prediction to produce produce projections
        into the target space, which can then be used to get probabilities of
        each target token for the next step.
        Add dropout before the softmax classifier (Following "Language to Logical Form with Neural Attention")
        Inputs are the same as for `take_step()`.
        """
        # shape: (group_size, max_input_sequence_length, encoder_output_dim)
        encoder_outputs = state["encoder_outputs"]

        # shape: (group_size, max_input_sequence_length)
        source_mask = state["source_mask"]

        # shape: (group_size, decoder_output_dim)
        decoder_hidden = state["decoder_hidden"]

        # shape: (group_size, decoder_output_dim)
        decoder_context = state["decoder_context"]

        # shape: (group_size, target_embedding_dim)
        embedded_input = self._target_embedder(last_predictions)
        embedded_input = self._embedded_dropout(embedded_input)

        if self._attention:
            # shape: (group_size, encoder_output_dim)
            attended_input = self._prepare_attended_input(decoder_hidden, encoder_outputs, source_mask)

            # shape: (group_size, decoder_output_dim + target_embedding_dim)
            decoder_input = torch.cat((attended_input, embedded_input), -1)
        else:
            # shape: (group_size, target_embedding_dim)
            decoder_input = embedded_input

        if self._feed_output_attention_to_decoder:
            decoder_input = torch.cat((decoder_input, state["attention_context"]), -1)

        # shape (decoder_hidden): (batch_size, decoder_output_dim)
        # shape (decoder_context): (batch_size, decoder_output_dim)
        decoder_hidden, decoder_context = self._decoder_cell(
            decoder_input,
            (decoder_hidden, decoder_context))

        state["decoder_hidden"] = decoder_hidden
        state["decoder_context"] = decoder_context

        if self._output_attention:
            # shape: (group_size, encoder_output_dim)
            output_attended_input = self._prepare_output_attended_input(decoder_hidden, encoder_outputs, source_mask)
            if self._feed_output_attention_to_decoder:
                state["attention_context"] = output_attended_input
            # output_projection_input = self._fuse_decoder_hidden_attention_layout(torch.cat((decoder_hidden,
            #                                                                                 output_attended_input), -1))
            output_projection_input = torch.cat((decoder_hidden, output_attended_input), -1)
        else:
            output_projection_input = decoder_hidden

        # dropped_output_projection_input = self._input_dropout(output_projection_input)
        dropped_output_projection_input = self._output_dropout(output_projection_input)

        # shape: (group_size, num_classes)
        output_projections = self._output_projection_layer(dropped_output_projection_input)

        return output_projections, state

    def _encode(self, source_tokens: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
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
    def _init_decoder_state(self, state: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        batch_size = state["source_mask"].size(0)
        # shape: (batch_size, encoder_output_dim)
        final_encoder_output = util.get_final_encoder_states(
            state["encoder_outputs"],
            state["source_mask"],
            self._encoder.is_bidirectional())
        # Initialize the decoder hidden state with the final output of the encoder.
        # shape: (batch_size, decoder_output_dim)
        state["decoder_hidden"] = self._transform_decoder_init_state(final_encoder_output)
        # shape: (batch_size, decoder_output_dim)
        state["decoder_context"] = state["encoder_outputs"].new_zeros(batch_size, self._decoder_output_dim)
        if self._feed_output_attention_to_decoder:
            state["attention_context"] = state["encoder_outputs"].new_zeros(batch_size, self._encoder_output_dim)
        return state

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
