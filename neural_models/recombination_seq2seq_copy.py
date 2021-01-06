# coding=utf8

from typing import Dict, List, Tuple

import numpy
from overrides import overrides
import torch
import torch.nn.functional as F
from torch.nn.modules.linear import Linear
from torch.nn.modules.rnn import LSTMCell

from allennlp.common.util import START_SYMBOL, END_SYMBOL
from allennlp.data.vocabulary import Vocabulary
from allennlp.data.tokenizers import Token
from allennlp.modules import Attention, TextFieldEmbedder, Seq2SeqEncoder
from allennlp.models.model import Model
from allennlp.modules.token_embedders import Embedding
from allennlp.training.metrics import Metric
from allennlp.nn.beam_search import BeamSearch
from allennlp.training.metrics import BLEU
from allennlp.nn import util, InitializerApplicator


class RecombinationSeq2SeqWithCopy(Model):
    def __init__(self,
                 vocab: Vocabulary,
                 source_embedder: TextFieldEmbedder,
                 encoder: Seq2SeqEncoder,
                 max_decoding_steps: int,
                 seq_metrics: Metric,
                 attention: Attention,
                 beam_size: int = None,
                 source_namespace: str = 'source_tokens',
                 target_namespace: str = "tokens",
                 target_embedding_dim: int = None,
                 scheduled_sampling_ratio: float = 0.,
                 use_bleu: bool = False,
                 encoder_input_dropout: int = 0.0,
                 encoder_output_dropout: int = 0.0,
                 dropout=0.0,
                 feed_output_attention_to_decoder: bool = False,
                 keep_decoder_output_dim_same_as_encoder: bool = True,
                 initializer: InitializerApplicator = InitializerApplicator()) -> None:

        super(RecombinationSeq2SeqWithCopy, self).__init__(vocab)
        self._source_namespace = source_namespace
        self._target_namespace = target_namespace
        self._scheduled_sampling_ratio = scheduled_sampling_ratio

        # We need the start symbol to provide as the input at the first timestep of decoding, and
        # end symbol as a way to indicate the end of the decoded sequence.
        self._start_index = self.vocab.get_token_index(START_SYMBOL, self._target_namespace)
        self._end_index = self.vocab.get_token_index(END_SYMBOL, self._target_namespace)
        self._pad_index = self.vocab.get_token_index(self.vocab._padding_token,
                                                     self._target_namespace)  # pylint: disable=protected-access

        # Evaluation Metrics
        if use_bleu:
            pad_index = self.vocab.get_token_index(self.vocab._padding_token, self._target_namespace)  # pylint: disable=protected-access
            self._bleu = BLEU(exclude_indices={pad_index, self._end_index, self._start_index})
        else:
            self._bleu = None
        self._seq_metric = seq_metrics

        # At prediction time, we use a beam search to find the most likely sequence of target tokens.
        beam_size = beam_size or 1
        self._max_decoding_steps = max_decoding_steps
        self._beam_search = BeamSearch(self._end_index, max_steps=max_decoding_steps, beam_size=beam_size)

        # Dense embedding of source vocab tokens.
        self._source_embedder = source_embedder

        # Encoder

        # Encodes the sequence of source embeddings into a sequence of hidden states.
        self._encoder = encoder
        self._encoder_output_dim = self._encoder.get_output_dim()

        # Attention mechanism applied to the encoder output for each step.
        self._attention = attention
        self._feed_output_attention_to_decoder = feed_output_attention_to_decoder
        if self._feed_output_attention_to_decoder:
            # If using attention, a weighted average over encoder outputs will be concatenated
            # to the previous target embedding to form the input to the decoder at each
            # time step.
            self._decoder_input_dim = self._encoder_output_dim + target_embedding_dim
        else:
            # Otherwise, the input to the decoder is just the previous target embedding.
            self._decoder_input_dim = target_embedding_dim

        # Decoder

        # Dense embedding of vocab words in the target space.
        num_classes = self.vocab.get_vocab_size(self._target_namespace)
        self._num_classes = num_classes
        target_embedding_dim = target_embedding_dim or source_embedder.get_output_dim()
        self._target_embedder = Embedding(num_classes, target_embedding_dim)

        # TODO: relax this assumption
        # Decoder output dim needs to be the same as the encoder output dim since we initialize the
        # hidden state of the decoder with the final hidden state of the encoder.
        self._keep_decoder_output_dim_same_as_encoder = keep_decoder_output_dim_same_as_encoder
        if not self._keep_decoder_output_dim_same_as_encoder:
            self._decoder_output_dim = int(self._encoder_output_dim / 2) if encoder.is_bidirectional() \
                else self._encoder_output_dim
        else:
            self._decoder_output_dim = self._encoder_output_dim

        self._decoder_cell = LSTMCell(self._decoder_input_dim, self._decoder_output_dim)

        self._transform_decoder_init_state = torch.nn.Sequential(
            torch.nn.Linear(self._encoder_output_dim, self._decoder_output_dim),
            torch.nn.Tanh()
        )

        # Generate Score
        self._output_projection_layer = Linear(self._decoder_output_dim + self._encoder_output_dim, num_classes)

        # Dropout Layers
        self._encoder_input_dropout = torch.nn.Dropout(p=encoder_input_dropout)
        self._encoder_output_dropout = torch.nn.Dropout(p=encoder_output_dropout)
        self._output_dropout = torch.nn.Dropout(p=dropout)
        self._embedded_dropout = torch.nn.Dropout(p=dropout)

        initializer(self)

    def _prepare_output_projections(self,
                                    last_predictions: torch.Tensor,
                                    state: Dict[str, torch.Tensor])\
            -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        # pylint: disable=line-too-long
        """
        Decode current state and last prediction to produce produce projections
        into the target space, which can then be used to get probabilities of
        each target token for the next step.
        Add dropout before the softmax classifier (Following "Language to Logical Form with Neural Attention")
        Inputs are the same as for `take_step()`.

        last_predictions: (group_size,)

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
        copy_mask = (last_predictions < self._num_classes).long()
        embedded_input = self._target_embedder(last_predictions * copy_mask)

        if not self.training and copy_mask.sum() < copy_mask.size(0):
            # Copy, Retrieve target token
            mapped_indices = list()
            source_token_ids = state['source_token_ids']
            for gidx, idx in enumerate(last_predictions):
                if idx >= self._num_classes:
                    source_idx = idx - self._num_classes
                    source_token_id = int(source_token_ids[gidx,source_idx])
                    token = self.vocab.get_token_from_index(source_token_id, self._source_namespace)
                    tid = self.vocab.get_token_index(token, self._target_namespace)
                    mapped_indices.append(tid)
                else:
                    mapped_indices.append(self._pad_index)
            # mapped_indices to tensor
            mapped_indices = torch.from_numpy(numpy.array(mapped_indices))
            mapped_indices = mapped_indices.to(last_predictions.device)

            copyed_embedded_input =  self._target_embedder(mapped_indices)
            unsqueezed_copy_mask = copy_mask.unsqueeze(dim=1).float()
            embedded_input = embedded_input * unsqueezed_copy_mask + copyed_embedded_input * (1 - unsqueezed_copy_mask)

        embedded_input = self._embedded_dropout(embedded_input)

        if self._feed_output_attention_to_decoder:
            # shape: (group_size, decoder_output_dim + target_embedding_dim)
            decoder_input = torch.cat((embedded_input, state["attention_context"]), -1)
        else:
            # shape: (group_size, target_embedding_dim)
            decoder_input = embedded_input

        # shape (decoder_hidden): (group_size, decoder_output_dim)
        # shape (decoder_context): (group_size, decoder_output_dim)
        decoder_hidden, decoder_context = self._decoder_cell(
            decoder_input,
            (decoder_hidden, decoder_context))

        state["decoder_hidden"] = decoder_hidden
        state["decoder_context"] = decoder_context

        # output_attended_input: shape: (group_size, encoder_output_dim)
        # attention_weights shape: (group_size, max_input_sequence_length)
        output_attended_input, attention_weights = self._prepare_output_attended_input(
            decoder_hidden,
            encoder_outputs,
            source_mask
        )
        if self._feed_output_attention_to_decoder:
            state["attention_context"] = output_attended_input

        output_projection_input = torch.cat((decoder_hidden, output_attended_input), -1)
        dropped_output_projection_input = self._output_dropout(output_projection_input)

        # shape: (group_size, num_classes)
        output_projections = self._output_projection_layer(dropped_output_projection_input)
        # shape: (group_size, num_classes + max_input_sequence_length)
        output_projections = torch.cat((output_projections, attention_weights), -1)

        return output_projections, state

    def take_step(self,
                  last_predictions: torch.Tensor,
                  state: Dict[str, torch.Tensor]) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Take a decoding step. This is called by the beam search class.

        Parameters
        ----------
        last_predictions : ``torch.Tensor``
            A tensor of shape ``(group_size,)``, which gives the indices of the predictions
            during the last time step.
        state : ``Dict[str, torch.Tensor]``
            A dictionary of tensors that contain the current state information
            needed to predict the next step, which includes the encoder outputs,
            the source mask, and the decoder hidden state and context. Each of these
            tensors has shape ``(group_size, *)``, where ``*`` can be any other number
            of dimensions.

        Returns
        -------
        Tuple[torch.Tensor, Dict[str, torch.Tensor]]
            A tuple of ``(log_probabilities, updated_state)``, where ``log_probabilities``
            is a tensor of shape ``(group_size, num_classes)`` containing the predicted
            log probability of each class for the next step, for each item in the group,
            while ``updated_state`` is a dictionary of tensors containing the encoder outputs,
            source mask, and updated decoder hidden state and context.

        Notes
        -----
            We treat the inputs as a batch, even though ``group_size`` is not necessarily
            equal to ``batch_size``, since the group may contain multiple states
            for each source sentence in the batch.
        """
        # shape: (group_size, num_classes + max_input_sequence_length)
        output_projections, state = self._prepare_output_projections(last_predictions, state)

        source_mask = state['source_mask']
        group_size = source_mask.size(0)

        # (batch_size, num_classes + max_input_sequence_length)
        normalization_mask = torch.cat([source_mask.new_ones((group_size, self._num_classes)),
                                        source_mask], dim=-1)

        # shape: (group_size, num_classes + max_input_sequence_length)
        class_log_probabilities = util.masked_log_softmax(output_projections, normalization_mask, dim=-1)

        return class_log_probabilities, state

    @overrides
    def forward(self,  # type: ignore
                source_tokens: Dict[str, torch.LongTensor],
                target_tokens: Dict[str, torch.LongTensor] = None,
                target_source_token_map: torch.Tensor = None,
                meta_field: List[Dict] = None,
                ) -> Dict[str, torch.Tensor]:
        # pylint: disable=arguments-differ
        """
        Make foward pass with decoder logic for producing the entire target sequence.
        Parameters
        ----------
        source_tokens : ``Dict[str, torch.LongTensor]``
           The output of `TextField.as_array()` applied on the source `TextField`. This will be
           passed through a `TextFieldEmbedder` and then through an encoder.
        target_tokens : ``Dict[str, torch.LongTensor]``, optional (default = None)
           Output of `Textfield.as_array()` applied on target `TextField`. We assume that the
           target tokens are also represented as a `TextField`.
        target_source_token_map: (batch_size, target_length, source_length)
        Returns
        -------
        Dict[str, torch.Tensor]
        """
        state = self._encode(source_tokens)

        if target_tokens:
            state = self._init_decoder_state(state)
            # The `_forward_loop` decodes the input sequence and computes the loss during training
            # and validation.
            output_dict = self._forward_loop(state, target_tokens, target_source_token_map)
        else:
            output_dict = {}

        if not self.training:
            state = self._init_decoder_state(state)
            predictions = self._forward_beam_search(state)
            output_dict.update(predictions)
            output_dict.update({"source_token_ids": source_tokens['tokens']})
            if target_tokens:
                # shape: (batch_size, beam_size, max_sequence_length)
                top_k_predictions = output_dict["predictions"]
                # shape: (batch_size, max_predicted_sequence_length)
                best_predictions = self.map_predictions(top_k_predictions[:, 0, :], source_tokens['tokens'], meta_field)
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
            # Collect indices till the first end_symbol
            if self._end_index in indices:
                indices = indices[:indices.index(self._end_index)]

            predicted_tokens = list()
            for x in indices:
                if x < self._num_classes:
                    predicted_tokens.append(self.vocab.get_token_from_index(x, namespace=self._target_namespace))
                else:
                    source_idx = x - self._num_classes
                    text = "@@copy@@%d" % int(source_idx)
                    token = Token(text)
                    # source_token_id = int(output_dict['source_token_ids'][0][source_idx])
                    # token = self.vocab.get_token_from_index(source_token_id, self._source_namespace)
                    predicted_tokens.append(token)
            all_predicted_tokens.append(predicted_tokens)
        output_dict["predicted_tokens"] = all_predicted_tokens
        return output_dict

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
            "source_token_ids": source_tokens['tokens'],
            "source_mask": source_mask,
            "encoder_outputs": encoder_outputs,
        }

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

    def _forward_loop(self,
                      state: Dict[str, torch.Tensor],
                      target_tokens: Dict[str, torch.LongTensor] = None,
                      target_source_token_map: torch.Tensor = None
                      ) -> Dict[str, torch.Tensor]:
        """
        Make forward pass during training or do greedy search during prediction.

        Notes
        -----
        We really only use the predictions from the method to test that beam search
        with a beam size of 1 gives the same results.
        """
        # shape: (batch_size, max_input_sequence_length)
        source_mask = state["source_mask"]

        batch_size = source_mask.size()[0]

        if target_tokens:
            # shape: (batch_size, max_target_sequence_length)
            targets = target_tokens["tokens"]

            _, target_sequence_length = targets.size()

            # The last input from the target is either padding or the end symbol.
            # Either way, we don't have to process it.
            num_decoding_steps = target_sequence_length - 1
        else:
            num_decoding_steps = self._max_decoding_steps

        # Initialize target predictions with the start index.
        # shape: (batch_size,)
        last_predictions = source_mask.new_full((batch_size,), fill_value=self._start_index)

        step_logits: List[torch.Tensor] = []
        step_predictions: List[torch.Tensor] = []
        for timestep in range(num_decoding_steps):
            if self.training and torch.rand(1).item() < self._scheduled_sampling_ratio:
                # Use gold tokens at test time and at a rate of 1 - _scheduled_sampling_ratio
                # during training.
                # shape: (batch_size,)
                input_choices = last_predictions
            elif not target_tokens:
                # shape: (batch_size,)
                input_choices = last_predictions
            else:
                # shape: (batch_size,)
                input_choices = targets[:, timestep]

            # shape: (batch_size, num_classes + max_input_sequence_length)
            output_projections, state = self._prepare_output_projections(input_choices, state)

            # list of tensors, shape: (batch_size, 1, num_classes + max_input_sequence_length)
            step_logits.append(output_projections.unsqueeze(1))

            # (batch_size, num_classes + max_input_sequence_length)
            normalization_mask = torch.cat([source_mask.new_ones((batch_size, self._num_classes)),
                                            source_mask], dim=-1)

            class_probabilities = util.masked_softmax(output_projections, normalization_mask, dim=-1)

            # shape (predicted_classes): (batch_size,)
            _, predicted_classes = torch.max(class_probabilities, 1)

            # shape (predicted_classes): (batch_size,)
            last_predictions = predicted_classes

            step_predictions.append(last_predictions.unsqueeze(1))

        # shape: (batch_size, num_decoding_steps)
        predictions = torch.cat(step_predictions, 1)

        output_dict = {"predictions": predictions}

        if target_tokens:
            # shape: (batch_size, num_decoding_steps, num_classes + max_input_sequence_length)
            logits = torch.cat(step_logits, 1)

            # Compute loss.
            target_mask = util.get_text_field_mask(target_tokens)
            loss = self._get_loss(logits, targets, target_mask, target_source_token_map)
            output_dict["loss"] = loss

        return output_dict

    def _forward_beam_search(self, state: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """Make forward pass during prediction using a beam search."""
        batch_size = state["source_mask"].size()[0]
        start_predictions = state["source_mask"].new_full((batch_size,), fill_value=self._start_index)

        # shape (all_top_k_predictions): (batch_size, beam_size, num_decoding_steps)
        # shape (log_probabilities): (batch_size, beam_size)
        all_top_k_predictions, log_probabilities = self._beam_search.search(
                start_predictions, state, self.take_step)

        output_dict = {
            "class_log_probabilities": log_probabilities,
            "predictions": all_top_k_predictions,
        }
        return output_dict

    def _prepare_output_attended_input(self,
                                       decoder_hidden_state: torch.Tensor = None,
                                       encoder_outputs: torch.Tensor = None,
                                       encoder_outputs_mask: torch.LongTensor = None) \
            -> Tuple[torch.Tensor, torch.Tensor]:
        """Apply ouput attention over encoder outputs and decoder state."""
        # Ensure mask is also a FloatTensor. Or else the multiplication within
        # attention will complain.
        # shape: (batch_size, max_input_sequence_length)
        encoder_outputs_mask = encoder_outputs_mask.float()

        # shape: (batch_size, max_input_sequence_length)
        input_weights = self._attention(
            decoder_hidden_state, encoder_outputs, encoder_outputs_mask)

        normalized_weights = util.masked_softmax(input_weights, encoder_outputs_mask)

        # shape: (batch_size, encoder_output_dim)
        attended_input = util.weighted_sum(encoder_outputs, normalized_weights)

        return attended_input, input_weights

    def _get_loss(self,
                  logits: torch.FloatTensor,
                  targets: torch.LongTensor,
                  target_mask: torch.LongTensor,
                  target_source_token_map: torch.Tensor) -> torch.Tensor:
        """
        Compute loss.
        Takes logits (unnormalized outputs from the decoder) of size (batch_size,
        num_decoding_steps, num_classes), target indices of size (batch_size, num_decoding_steps+1)
        and corresponding masks of size (batch_size, num_decoding_steps+1) steps and computes cross
        entropy loss while taking the mask into account.

        The length of ``targets`` is expected to be greater than that of ``logits`` because the
        decoder does not need to compute the output corresponding to the last timestep of
        ``targets``. This method aligns the inputs appropriately to compute the loss.
        ``target_source_token_map``: (batch_size, target_length, source_length)

        During training, we want the logit corresponding to timestep i to be similar to the target
        token from timestep i + 1. That is, the targets should be shifted by one timestep for
        appropriate comparison.  Consider a single example where the target has 3 words, and
        padding is to 7 tokens.
           The complete sequence would correspond to <S> w1  w2  w3  <E> <P> <P>
           and the mask would be                     1   1   1   1   1   0   0
           and let the logits be                     l1  l2  l3  l4  l5  l6
        We actually need to compare:
           the sequence           w1  w2  w3  <E> <P> <P>
           with masks             1   1   1   1   0   0
           against                l1  l2  l3  l4  l5  l6
           (where the input was)  <S> w1  w2  w3  <E> <P>
        """
        # shape: (batch_size, num_decoding_steps)
        relevant_targets = targets[:, 1:].contiguous()
        batch_size, num_decoding_steps = relevant_targets.size()

        # shape: (batch_size, num_decoding_steps)
        relevant_mask = target_mask[:, 1:].contiguous()

        # shape: (batch_size, num_decoding_steps, source_length)
        target_source_token_map = target_source_token_map[:, 1:, :]

        probs = F.softmax(logits, dim=-1)
        # (batch_size * num_decoding_steps, num_classes)
        generate_probs_flat = probs[:, :, :self._num_classes].view(-1, self._num_classes)
        relevant_targets_flat = relevant_targets.view(-1, 1).long()
        # (batch_size, num_decoding_steps)
        generate_probs = torch.gather(generate_probs_flat, dim=1, index=relevant_targets_flat).reshape(batch_size,
                                                                                                       num_decoding_steps)
        # (batch_size, num_decoding_steps)
        copy_probs = (probs[:, :, self._num_classes:] * target_source_token_map).sum(dim=-1)

        target_log_probs = torch.log(generate_probs + copy_probs + 1e-13)
        target_log_probs *= relevant_mask.float()
        negative_log_likelihood = -1 * target_log_probs
        weights_batch_sum = relevant_mask.sum(-1).float()

        per_batch_loss = negative_log_likelihood.sum(dim=1) / (weights_batch_sum + 1e-13)
        num_non_empty_sequences = ((weights_batch_sum > 0).float().sum() + 1e-13)
        return per_batch_loss.sum() / num_non_empty_sequences

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

    def map_predictions(self, predictions: torch.LongTensor,
                        source_token_ids: torch.LongTensor,
                        meta_field: List[Dict]) -> torch.LongTensor:
        """
        Map those copy indices to target idx
        :return:
        """
        batch_size, max_length = predictions.size()
        mapped_predictions = predictions.new_full((batch_size,max_length), fill_value=self._pad_index)
        for i in range(batch_size):
            source_tokens_to_copy = meta_field[i]['source_tokens_to_copy']
            for j in range(max_length):
                idx = predictions[i, j]
                if idx < self._num_classes:
                    mapped_predictions[i, j] = idx
                else:
                    # Copy
                    source_idx = idx - self._num_classes
                    if source_idx > len(source_tokens_to_copy):
                        tid = self._pad_index
                    else:
                        token = source_tokens_to_copy[source_idx]
                        # source_token_id = int(source_token_ids[i, source_idx])
                        # token = self.vocab.get_token_from_index(source_token_id, self._source_namespace)
                        tid = self.vocab.get_token_index(token, self._target_namespace)
                    mapped_predictions[i, j] = tid
        return mapped_predictions.long()
