# coding=utf8

import numpy
import torch
import torch.nn as nn
from allennlp.models.model import Model
from allennlp.data.tokenizers import Token
from allennlp.common.util import START_SYMBOL, END_SYMBOL
from allennlp.data.vocabulary import Vocabulary
from allennlp.modules import Embedding
from allennlp.modules.text_field_embedders import BasicTextFieldEmbedder
from allennlp.training.metrics import Metric
from allennlp.nn import util
from overrides import overrides
from typing import Dict, List, Union, Tuple
import torch.nn.functional as F
from torch.nn.init import xavier_uniform_
from . import utils as nn_utils
from .modules.gnn_encoder import GNNTransformerEncoderLayer, GNNTransformerEncoder, \
    GNNTransformerDecoderLayer, GNNTransformerDecoder, get_decode_edge_mask


class GNNCopyTransformer(Model):
    """
    Transformer-based Seq2Seq Model
    """

    def __init__(self, vocab: Vocabulary,
                 source_namespace: str,
                 target_namespace: str,
                 segment_namespace: str,
                 max_decoding_step: int,
                 token_based_metric: Metric,
                 source_embedding_dim: int = 256,
                 target_embedding_dim: int = 256,
                 encoder_d_model: int = 512,
                 decoder_d_model: int = 512,
                 encoder_nhead: int = 8,
                 decoder_nhead: int = 8,
                 num_encoder_layers: int = 6,
                 num_decoder_layers: int = 6,
                 encoder_dim_feedforward: int = 2048,
                 decoder_dim_feedforward: int = 2048,
                 dropout: float = 0.1,
                 beam_size: int = 1,
                 token_symbol: str = '@token@',
                 non_func_symbol: str = "@nonfunc@",
                 nlabels: int = 0,
                 max_decode_clip_range: int = 0,
                 encode_edge_label_with_matrix: bool = True,
                 is_test: bool = False,
                 ):
        super().__init__(vocab)
        self._source_namespace = source_namespace
        self._target_namespace = target_namespace
        self._segment_namespace = segment_namespace
        self._src_start_index = self.vocab.get_token_index(START_SYMBOL, self._source_namespace)
        self._src_end_index = self.vocab.get_token_index(END_SYMBOL, self._source_namespace)
        self._start_index = self.vocab.get_token_index(START_SYMBOL, self._target_namespace)
        self._end_index = self.vocab.get_token_index(END_SYMBOL, self._target_namespace)
        self._oov_index = self.vocab.get_token_index(self.vocab._oov_token,
                                                     self._target_namespace)  # pylint: disable=protected-access
        self._pad_index = self.vocab.get_token_index(self.vocab._padding_token,
                                                     self._target_namespace)
        self._token_index = self.vocab.get_token_index(token_symbol, self._segment_namespace)
        self._non_func_symbol_index = self.vocab.get_token_index(non_func_symbol, self._segment_namespace)
        self._segment_pad_index = self.vocab.get_token_index(self.vocab._padding_token, self._segment_namespace)

        # Source Embedding
        num_source_words = self.vocab.get_vocab_size(self._source_namespace)
        self._use_glove = False
        self._source_embedding = Embedding(num_source_words, source_embedding_dim)

        # Segments
        num_segment_types = self.vocab.get_vocab_size(self._segment_namespace)
        segment_embedding = Embedding(num_segment_types, source_embedding_dim)
        self._segment_embedder = BasicTextFieldEmbedder({'tokens': segment_embedding})

        num_classes = self.vocab.get_vocab_size(self._target_namespace)
        self._num_classes = num_classes
        self._target_embedder = Embedding(num_classes, target_embedding_dim)

        # Encoder
        self._nlabels = nlabels  # number of edge labels
        if self._nlabels == 0:
            self._use_gnn_encoder = False
            encoder_layer = nn.TransformerEncoderLayer(encoder_d_model, encoder_nhead, encoder_dim_feedforward, dropout)
            encoder_norm = nn.LayerNorm(encoder_d_model)
            self._encoder = nn.TransformerEncoder(encoder_layer, num_encoder_layers, encoder_norm)
        else:
            self._use_gnn_encoder = True
            print("Use GNN Encoder")
            encoder_layer = GNNTransformerEncoderLayer(d_model=encoder_d_model, nhead=encoder_nhead,
                                                       dim_feedforward=encoder_dim_feedforward,
                                                       dropout=dropout, nlabels=self._nlabels,
                                                       is_matrix=encode_edge_label_with_matrix)
            encoder_norm = nn.LayerNorm(encoder_d_model)
            self._encoder = GNNTransformerEncoder(encoder_layer, num_encoder_layers, encoder_norm)

        # Decoder
        self._max_decode_clip_range = max_decode_clip_range
        if max_decode_clip_range == 0:
            self._decode_nlabels = 0
            self._decode_use_relative_position = False
            decoder_layer = nn.TransformerDecoderLayer(decoder_d_model, decoder_nhead, decoder_dim_feedforward, dropout)
            decoder_norm = nn.LayerNorm(decoder_d_model)
            self._decoder = nn.TransformerDecoder(decoder_layer, num_decoder_layers, decoder_norm)
        else:
            print("Use GNN Decoder")
            self._decode_nlabels = self._max_decode_clip_range + 1
            self._decode_use_relative_position = True
            decoder_layer = GNNTransformerDecoderLayer(d_model=decoder_d_model, nhead=decoder_nhead,
                                                       dim_feedforward=decoder_dim_feedforward,
                                                       dropout=dropout, nlabels=self._decode_nlabels,
                                                       is_matrix=encode_edge_label_with_matrix)
            decoder_norm = nn.LayerNorm(decoder_d_model)
            self._decoder = GNNTransformerDecoder(decoder_layer, num_decoder_layers, decoder_norm)

        # Decode Gate
        self.gate_linear = nn.Linear(decoder_d_model, 1)

        self.copy_word_prj = nn.Linear(decoder_d_model, encoder_d_model, bias=False)

        self._source_embedding_dim = source_embedding_dim
        self._target_embedding_dim = target_embedding_dim
        self._encoder_d_model = encoder_d_model
        self._decoder_d_model = decoder_d_model
        self._encoder_nhead = encoder_nhead
        self._decoder_nhead = decoder_nhead
        self._max_decoding_step = max_decoding_step
        self._token_based_metric = token_based_metric
        self._beam_size = beam_size
        self._is_test = is_test

        self._reset_parameters()

    def _reset_parameters(self):
        r"""Initiate parameters in the transformer model."""
        for p in self.parameters():
            if p.dim() > 1:
                xavier_uniform_(p)

    @overrides
    def forward(self,
                source_tokens: Dict[str, torch.LongTensor],
                segments: Dict[str, torch.LongTensor],
                source_entity_length: torch.LongTensor,
                edge_mask: torch.Tensor,
                copy_targets: torch.Tensor = None,
                generate_targets: torch.Tensor = None,
                target_tokens: Dict[str, torch.LongTensor] = None,
                meta_field: Dict = None,
                ) -> Dict[str, torch.Tensor]:
        assert self._nlabels == edge_mask.size(1)
        state = self._encode(source_tokens, segments, source_entity_length, edge_mask)

        if self.training:
            state = self._train_decode(state, target_tokens, generate_targets)
            # shape: (batch_size, decode_length, d_model)
            generate_mask = state["generate_mask"]
            decoder_outputs = state["decoder_outputs"]
            decode_length = decoder_outputs.size(1)

            # Generate scores
            # shape: (batch_size, decode_length, num_classes)
            generate_scores = self.get_generate_scores(decoder_outputs)

            # shape: (batch_size, encode_length)
            entity_mask = 1 - ((segments['tokens'] == self._token_index) |
                               (segments['tokens'] == self._non_func_symbol_index) |
                               (segments['tokens'] == self._segment_pad_index)).float()
            entity_mask = entity_mask.unsqueeze(1).repeat(1, decode_length, 1)
            # shape: (batch_size, decode_length, encode_length)
            copy_scores = self.get_copy_scores(state, decoder_outputs)

            # shape: (batch_size, decode_length, 1)
            # generate_gate = F.sigmoid(self.gate_linear(decoder_outputs))
            # copy_gate = 1 - generate_gate

            scores = torch.cat((generate_scores, copy_scores), dim=-1)
            # scores = torch.cat((generate_scores, copy_scores), dim=-1)

            # shape: (batch_size, decode_length, num_classes + encode_length)
            score_mask = torch.cat((entity_mask.new_ones((copy_scores.size(0), decode_length, self._num_classes)),
                                    entity_mask), dim=-1)

            class_probabilities = util.masked_softmax(scores, mask=score_mask, dim=-1)

            _, predicted_classes = torch.max(class_probabilities, dim=-1, keepdim=False)

            targets = target_tokens["tokens"]
            target_mask = state["target_mask"]
            # shape: (batch_size, max_target_sequence_length)

            loss = self._get_loss(class_probabilities, targets, generate_mask, copy_targets, target_mask)
            output_dict = {"predictions": predicted_classes, "loss": loss}

            predictions = output_dict["predictions"]
            pmask = (predictions < self._num_classes).long()
            _predictions = predictions * pmask + (predictions - self._num_classes) * (1 - pmask)
            target_labels = self._get_target_labels(target_tokens["tokens"], generate_targets)
            target_mask = util.get_text_field_mask(target_tokens)
            self._token_based_metric(_predictions, gold_labels=target_labels[:, 1:], mask=target_mask[:, 1:])

        else:

            output_dict = self._eval_decode(state, segments)

            if target_tokens:
                predictions = output_dict["predictions"]
                pmask = (predictions < self._num_classes).long()
                _predictions = predictions * pmask + (predictions - self._num_classes) * (1 - pmask)
                target_labels = self._get_target_labels(target_tokens["tokens"], generate_targets)
                target_mask = util.get_text_field_mask(target_tokens)
                self._token_based_metric(_predictions[:, 1:], gold_labels=target_labels[:, 1:], mask=target_mask[:, 1:])

        return output_dict

    @overrides
    def decode(self, output_dict: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """
        Finalize predictions.

        This method overrides ``Model.decode``, which gets called after ``Model.forward``, at test
        time, to finalize predictions. The logic for the decoder part of the encoder-decoder lives
        within the ``forward`` method.

        This method trims the output predictions to the first end symbol, replaces indices with
        corresponding tokens, and adds a field called ``predicted_tokens`` to the ``output_dict``.
        """
        predicted_indices = output_dict["predictions"]
        if not isinstance(predicted_indices, numpy.ndarray):
            predicted_indices = predicted_indices.detach().cpu().numpy()
        all_predicted_tokens = []
        for indices in predicted_indices:
            # Beam search gives us the top k results for each source sentence in the batch
            # but we just want the single best.
            if len(indices.shape) > 1:
                indices = indices[0]
            indices = list(indices)

            if self._end_index in indices:
                indices = indices[:indices.index(self._end_index)]
            predicted_tokens = list()
            for x in indices:
                if x in [self._end_index, self._start_index, self._pad_index]:
                    continue
                if x >= self._num_classes:
                    index = x - self._num_classes
                    predicted_tokens.append(Token("@entity_%d" % index))
                else:
                    w = self.vocab.get_token_from_index(x, namespace=self._target_namespace)
                    predicted_tokens.append(w)
            all_predicted_tokens.append(predicted_tokens)
        output_dict["predicted_tokens"] = all_predicted_tokens
        return output_dict

    def _embed_source(self, source_tokens: Dict[str, torch.Tensor], source_entity_length: torch.LongTensor):
        """
        :param source_tokens
        :param source_entity_length: (batch_size, max_token_num)
        :return
            (batch_size, max_token_num, embedding_dim)
        """
        token_ids = source_tokens['tokens']
        embedded = self._source_embedding(token_ids)

        batched_embedded = list()
        embedding_dim = embedded.size(-1)
        batch_size, max_token_num = source_entity_length.size()

        for _embedded, _length in zip(embedded, source_entity_length.long()):
            merged_embedded_input = list()
            idx = 0
            for length in _length:
                if length > 0:
                    embedding = torch.mean(_embedded[idx:idx + length, :], dim=0)
                    merged_embedded_input.append(embedding)
                    idx += length
                else:
                    break
            merged_embedded_input = torch.stack(merged_embedded_input, dim=0)
            pad_num = max_token_num - merged_embedded_input.size(0)
            if pad_num > 0:
                merged_embedded_input = torch.cat((merged_embedded_input,
                                                   merged_embedded_input.new_zeros([pad_num, embedding_dim])), dim=0)
            batched_embedded.append(merged_embedded_input)

        # shape: (batch_size, max_token_num, embedding_dim)
        batched_embedded = torch.stack(batched_embedded, dim=0)
        assert batched_embedded.size(0) == embedded.size(0) and batched_embedded.size(1) == source_entity_length.size(1)
        # TODO: Dropout
        return batched_embedded

    def _encode(self, source_tokens: Dict[str, torch.Tensor], segments: Dict[str, torch.Tensor],
                source_entity_length: torch.Tensor, edge_mask: torch.Tensor, ) -> Dict[str, torch.Tensor]:
        """
        :param source_tokens:
        :param segments:
        :param merge_indicators:
        :return:
        """
        # shape: (batch_size, encode_length, embedding_dim)
        source_embedded_input = self._embed_source(source_tokens, source_entity_length)

        # shape: (batch_size, encode_length, embedding_dim)
        segments_embedded_input = self._segment_embedder(segments)
        encode_length = segments_embedded_input.size(1)

        assert source_embedded_input.size(1) == segments_embedded_input.size(1)

        # token_mask = (segments['tokens'] == self._token_index).unsqueeze(-1).float()
        # valid_token_embedded_input = batched_embedded_input * token_mask
        # valid_token_embedded_input = util.add_positional_features(valid_token_embedded_input)
        # valid_token_embedded_input = batched_embedded_input * (1 - token_mask) + valid_token_embedded_input * token_mask

        if self._source_embedding_dim == self._encoder_d_model:
            batched_embedded_input = segments_embedded_input + source_embedded_input
            final_embedded_input = util.add_positional_features(batched_embedded_input)
        else:
            batched_embedded_input = torch.cat([source_embedded_input, segments_embedded_input], dim=-1)
            final_embedded_input = util.add_positional_features(batched_embedded_input)

        # shape: (encode_length, batch_size, d_model)
        final_embedded_input = final_embedded_input.permute(1, 0, 2)

        # shape: (batch_size, encode_length)
        source_mask = util.get_text_field_mask(segments)
        source_key_padding_mask = (1 - source_mask.byte()).bool()

        if not self._use_gnn_encoder:
            # shape: (encode_length, batch_size, d_model)
            encoder_outputs = self._encoder(final_embedded_input, src_key_padding_mask=source_key_padding_mask)
        else:
            # GNN encoders
            encoder_outputs = self._encoder(src=final_embedded_input, edge_mask=edge_mask.permute(0, 2, 3, 1),
                                            padding_mask=source_key_padding_mask)

        source_token_mask = (segments['tokens'] == self._token_index).float()

        return {
            "source_mask": source_mask,
            "source_key_padding_mask": source_key_padding_mask,
            "source_token_mask": source_token_mask,
            "encoder_outputs": encoder_outputs,
            "source_embedded": batched_embedded_input,
            "source_raw_embedded": source_embedded_input,
        }

    def _train_decode(self, state: Dict[str, torch.Tensor],
                      target_tokens: [str, torch.Tensor],
                      generate_targets: torch.Tensor) -> Dict[str, torch.Tensor]:
        encoder_outputs = state["encoder_outputs"]
        source_key_padding_mask = state["source_key_padding_mask"]

        # shape: (batch_size, encode_length, d_model)
        source_embedded = state["source_raw_embedded"]
        batch_size, _, _ = source_embedded.size()
        basic_index = torch.arange(batch_size).to(source_embedded.device).long()
        generate_targets = generate_targets.long()
        retrieved_target_embedded_input = source_embedded[basic_index.unsqueeze(1), generate_targets][:, :-1, :]
        target_embedded_input = self._target_embedder(target_tokens['tokens'])[:, :-1, :]

        # shape: (batch_size, max_decode_length)
        # where 1 indicates that the target token is generated rather than copied
        generate_mask = (generate_targets == 0).float()
        target_embedded_input = target_embedded_input * generate_mask[:, :-1].unsqueeze(-1) \
                                + retrieved_target_embedded_input * (1 - generate_mask)[:, :-1].unsqueeze(-1)
        target_embedded_input = util.add_positional_features(target_embedded_input)

        # shape: (max_target_sequence_length - 1, batch_size, d_model)
        target_embedded_input = target_embedded_input.permute(1, 0, 2)

        # shape: (batch_size, max_target_sequence_length - 1)
        """
        key_padding_mask should be a ByteTensor where True values are positions
            that should be masked with float('-inf') and False values will be unchanged.
        """
        target_mask = util.get_text_field_mask(target_tokens)[:, 1:]
        target_key_padding_mask = (1 - target_mask.byte()).bool()

        assert target_key_padding_mask.size(1) == target_embedded_input.size(0) and \
               target_embedded_input.size(1) == target_key_padding_mask.size(0)

        max_target_seq_length = target_key_padding_mask.size(1)
        target_additive_mask = (torch.triu(
            target_mask.new_ones(max_target_seq_length, max_target_seq_length)) == 1).transpose(0, 1)
        target_additive_mask = target_additive_mask.float().masked_fill(target_additive_mask == 0, float('-inf'))
        target_additive_mask = target_additive_mask.masked_fill(target_additive_mask == 1, float(0.0))

        assert target_embedded_input.size(1) == encoder_outputs.size(1)

        source_token_mask = state["source_token_mask"]
        memory_key_padding_mask = (1 - source_token_mask).bool()
        # memory_key_padding_mask = source_key_padding_mask
        if not self._decode_use_relative_position:
            # shape: (max_target_sequence_length, batch_size, d_model)
            decoder_outputs = self._decoder(target_embedded_input, memory=encoder_outputs,
                                            tgt_mask=target_additive_mask, tgt_key_padding_mask=None,
                                            memory_key_padding_mask=memory_key_padding_mask)
        else:
            # gnn decoder
            edge_mask = get_decode_edge_mask(target_embedded_input,
                                             max_decode_clip_range=self._max_decode_clip_range)
            batch_size = edge_mask.size(0)
            tgt_padding_mask = torch.tril(edge_mask.new_ones([max_target_seq_length, max_target_seq_length]),
                                          diagonal=0)
            tgt_padding_mask = (1 - (tgt_padding_mask.unsqueeze(0).repeat(batch_size, 1, 1))).float()
            decoder_outputs = self._decoder(target_embedded_input, edge_mask=edge_mask.permute(0, 2, 3, 1),
                                            memory=encoder_outputs, tgt_padding_mask=tgt_padding_mask,
                                            memory_key_padding_mask=memory_key_padding_mask)
        # shape: (batch_size, max_target_sequence_length, d_model)
        decoder_outputs = decoder_outputs.permute(1, 0, 2)

        state.update({
            "decoder_outputs": decoder_outputs,
            "target_key_padding_mask": target_key_padding_mask,
            "target_mask": target_mask,
            "generate_mask": generate_mask
        })
        return state

    def _eval_decode(self, state: Dict[str, torch.Tensor],
                     segments: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        encoder_outputs = state["encoder_outputs"]
        source_key_padding_mask = state["source_key_padding_mask"]
        source_embedded = state["source_raw_embedded"]

        source_token_mask = state["source_token_mask"]
        memory_key_padding_mask = (1 - source_token_mask).bool()
        # memory_key_padding_mask = source_key_padding_mask

        batch_size = source_key_padding_mask.size(0)
        encode_length = source_key_padding_mask.size(1)
        log_probs_after_end = encoder_outputs.new_full((batch_size, self._num_classes + encode_length),
                                                       fill_value=float("-inf"))
        log_probs_after_end[:, self._end_index] = 0.

        start_predictions = state["source_mask"].new_full((batch_size, 1), fill_value=self._start_index)
        partial_generate_predictions = start_predictions
        partial_copy_predictions = state["source_mask"].new_zeros((batch_size, 1))
        basic_index = torch.arange(batch_size).to(source_embedded.device).unsqueeze(1).long()
        generate_mask = state["source_mask"].new_ones((batch_size, 1)).float()
        # shape: (batch_size)
        last_prediction = start_predictions.squeeze(1)
        for _ in range(self._max_decoding_step):
            # shape: (batch_size, partial_len, d_model)
            partial_source_embedded_input = source_embedded[basic_index, partial_copy_predictions]
            partial_target_embedded_input = self._target_embedder(partial_generate_predictions)
            partial_embedded_input = partial_target_embedded_input * generate_mask.unsqueeze(-1) \
                                     + partial_source_embedded_input * (1 - generate_mask).unsqueeze(-1)

            partial_embedded_input = util.add_positional_features(partial_embedded_input)
            partial_len = partial_embedded_input.size(1)

            partial_embedded_input = partial_embedded_input.permute(1, 0, 2)

            mask = (torch.triu(state["source_mask"].new_ones(partial_len, partial_len)) == 1).transpose(0, 1)
            mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))

            if not self._decode_use_relative_position:
                # shape: (partial_len, batch_size, d_model)
                outputs = self._decoder(partial_embedded_input, memory=encoder_outputs,
                                        tgt_mask=mask, memory_key_padding_mask=memory_key_padding_mask)
            else:
                # gnn decoder
                edge_mask = get_decode_edge_mask(partial_embedded_input,
                                                 max_decode_clip_range=self._max_decode_clip_range)
                tgt_padding_mask = torch.tril(edge_mask.new_ones([partial_len, partial_len]), diagonal=0)
                tgt_padding_mask = (1 - tgt_padding_mask.unsqueeze(0).repeat(batch_size, 1, 1)).float()
                # shape: (partial_len, batch_size, d_model)
                outputs = self._decoder(partial_embedded_input, edge_mask=edge_mask.permute(0, 2, 3, 1),
                                        memory=encoder_outputs, tgt_padding_mask=tgt_padding_mask,
                                        memory_key_padding_mask=memory_key_padding_mask)

            outputs = outputs.permute(1, 0, 2)

            # shape: (batch_size, d_model)
            curr_outputs = outputs[:, -1, :]

            # shape: (batch_size, num_classes)
            generate_scores = self.get_generate_scores(curr_outputs)
            # shape: (batch_size, encode_length)
            copy_scores = self.get_copy_scores(state, curr_outputs.unsqueeze(1)).squeeze(1)

            # Gate
            # shape: (batch_size, 1)
            # generate_gate = F.sigmoid(self.gate_linear(curr_outputs))
            # copy_gate = 1 - generate_gate
            scores = torch.cat((generate_scores, copy_scores), dim=-1)
            # scores = torch.cat((generate_scores, copy_scores), dim=-1)

            # shape: (batch_size, encode_length)
            entity_mask = 1 - ((segments['tokens'] == self._token_index) |
                               (segments['tokens'] == self._non_func_symbol_index) |
                               (segments['tokens'] == self._segment_pad_index)).float()
            # shape: (batch_size, num_classes + encode_length)
            score_mask = torch.cat((entity_mask.new_ones((batch_size, self._num_classes)), entity_mask), dim=-1)

            # shape: (batch_size, num_classes + encode_length)
            normalized_scores = util.masked_softmax(scores, mask=score_mask, dim=-1)

            last_prediction_expanded = last_prediction.unsqueeze(-1).expand(
                batch_size, self._num_classes + encode_length
            )

            # shape: (batch_size, num_classes + encode_length)
            cleaned_logits = torch.where(
                last_prediction_expanded == self._end_index,
                log_probs_after_end,
                normalized_scores
            )

            # shape: (batch_size)
            _, predicted = torch.max(input=cleaned_logits, dim=1, keepdim=False)

            copy_mask = (predicted >= self._num_classes).long()
            generate_predicted = predicted * (1 - copy_mask)
            copy_predicted = (predicted - self._num_classes) * copy_mask
            partial_copy_predictions = torch.cat((partial_copy_predictions, copy_predicted.unsqueeze(1)), dim=1)
            partial_generate_predictions = torch.cat((partial_generate_predictions, generate_predicted.unsqueeze(1)),
                                                     dim=1)
            generate_mask = torch.cat((generate_mask, (1 - copy_mask).unsqueeze(1).float()), dim=1)

            last_prediction = predicted

            if (last_prediction == self._end_index).sum() == batch_size:
                break

        predictions = partial_generate_predictions * generate_mask.long() + \
                      (1 - generate_mask).long() * (partial_copy_predictions + self._num_classes)

        # shape: (batch_size, partial_len)
        output_dict = {
            "predictions": predictions
        }
        return output_dict

    def get_copy_scores(self, state: Dict[str, torch.Tensor],
                        query: torch.Tensor) -> torch.Tensor:
        """
        :param state:
        :param query: (batch_size, length, d_model)
        :return:
        """
        # shape: (batch_size, encode_length, d_model)
        encoder_outputs = state["encoder_outputs"].permute(1, 0, 2)
        return self.copy_word_prj(query).bmm(encoder_outputs.permute(0, 2, 1))

    def get_generate_scores(self, query: torch.Tensor) -> torch.Tensor:
        """
        :param query: (batch_size, length, d_model)
        :return:
        """
        return F.linear(query, self._target_embedder.weight)

    def _get_loss(self, scores: torch.Tensor,
                  targets: torch.LongTensor,
                  generate_mask: torch.LongTensor,
                  copy_mask: torch.LongTensor,
                  target_mask: torch.LongTensor) -> torch.Tensor:
        """
        :param scores:  (batch_size, decode_length, num_class + encode_length)
        :param targets: (batch_size, decode_length + 1)
        :param generate_mask: (batch_size, decode_length + 1), where 1.0 indicates the target word is selected from target
                              vocabulary, 0.0 indicates the target is copied from entity candidates
        :param copy_mask:     (batch_size, decode_length + 1, encode_length), where 1.0 indicates that the target word
                              is copied from this source word
        :param target_mask:   (batch_size, decode_length)
        :return:
        """
        batch_size, decode_length, _ = scores.size()
        # (batch_size, decode_length, num_class)
        generate_scores = scores[:, :, :self._num_classes]
        # (batch_size, decode_length, encode_length)
        copy_scores = scores[:, :, self._num_classes:]

        # shape: (batch_size * decode_length, 1)
        relevant_targets = targets[:, 1:].contiguous().view(-1, 1)
        target_generate_scores = torch.gather(
            generate_scores.view(-1, self._num_classes), dim=1, index=relevant_targets)
        target_scores = target_generate_scores.view(batch_size, decode_length)

        target_scores = target_scores * generate_mask[:, 1:]

        target_scores += (copy_scores * copy_mask[:, 1:, :].float()).sum(dim=-1)

        # shape: (batch_size, decode_length)
        relevant_mask = target_mask.contiguous().float()
        loss = - target_scores.log() * relevant_mask
        loss = loss.sum(dim=-1) / relevant_mask.sum(dim=-1)
        loss = loss.sum() / batch_size
        return loss

    def _get_target_labels(self, target_token_ids: torch.Tensor, generate_targets: torch.Tensor):
        """
        :param target_token_ids: [batch_size, decode_length]
        :param generate_targets: [batch_size, decode_length]
        :return:
            [batch_size, decode_length]
        """
        generate_mask = (generate_targets == 0.0).long()
        labels = target_token_ids * generate_mask + generate_targets.long() * (1 - generate_mask)
        return labels

    @overrides
    def get_metrics(self, reset: bool = False) -> Dict[str, float]:
        return self._token_based_metric.get_metric(reset)

    def _get_predicted_tokens(self,
                              source_tokens: Dict[str, torch.LongTensor],
                              predicted_indices: Union[torch.Tensor, numpy.ndarray],
                              meta_field: List[Dict]):
        """
        Convert predicted indices into tokens.
        If `n_best = 1`, the result type will be `List[List[str]]`. Otherwise the result
        type will be `List[List[List[str]]]`.
        """
        # shape: (batch_size, encode_length)
        source_token_ids = source_tokens['tokens']
        if not isinstance(predicted_indices, numpy.ndarray):
            predicted_indices = predicted_indices.detach().cpu().numpy()
        predicted_tokens: List[Union[List[List[str]], List[str]]] = []
        predicted_abstract_tokens: List[Union[List[List[str]], List[str]]] = []
        for bidx, top_k_predictions in enumerate(predicted_indices):
            batch_predicted_tokens: List[List[str]] = []
            batch_predicted_abstract_tokens: List[List[str]] = []
            pseudo_tokens = meta_field[bidx]['pseudo_tokens']
            for indices in top_k_predictions:
                indices = list(indices)
                if self._end_index in indices:
                    indices = indices[:indices.index(self._end_index)]
                tokens = list()
                abstract_tokens = list()
                for x in indices:
                    if x in [self._end_index, self._start_index, self._pad_index]:
                        continue
                    if x >= self._num_classes:
                        index = x - self._num_classes
                        # source_word = "@entity_%d" % index
                        source_word = pseudo_tokens[index]
                        tokens.append(source_word)
                        abstract_tokens.append("@entity_%d" % index)
                    else:
                        w = self.vocab.get_token_from_index(x, namespace=self._target_namespace)
                        tokens.append(w)
                        abstract_tokens.append(w)
                batch_predicted_tokens.append(tokens)
                batch_predicted_abstract_tokens.append(abstract_tokens)
            predicted_tokens.append(batch_predicted_tokens)
            predicted_abstract_tokens.append(batch_predicted_abstract_tokens)
        return predicted_tokens, predicted_abstract_tokens

    def _get_target_tokens(self, target_token_ids: Union[torch.Tensor, numpy.ndarray]) -> List[List[str]]:
        if not isinstance(target_token_ids, numpy.ndarray):
            _target_token_ids = target_token_ids.detach().cpu().numpy()
        else:
            _target_token_ids = target_token_ids
        tokens = list()
        for ids in _target_token_ids:
            _tokens = [self.vocab.get_token_from_index(x, namespace=self._target_namespace) for x in ids
                       if x not in [self._end_index, self._start_index, self._pad_index]]
            tokens.append(_tokens)
        return tokens
