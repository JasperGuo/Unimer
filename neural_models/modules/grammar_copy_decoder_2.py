# coding=utf-8

import torch
import copy
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
from overrides import overrides
from allennlp.modules import Embedding
from typing import Tuple, List, Dict
from .. import utils as nn_utils


class LSTMGrammarCopyDecoder(nn.Module):

    def __init__(self,
        grammar,
        ast_class,
        lstm_hidden_dim: int,
        num_lstm_layers: int,
        rule_pad_index: int,
        rule_embedding_dim: int,
        nonterminal_pad_index: int,
        nonterminal_end_index: int,
        nonterminal_embedding_dim: int,
        source_encoding_dim: int,
        dropout: float,
        max_target_length: int,
    ):
        super().__init__()
        self._grammar = grammar
        self._root_rule = grammar.get_production_rule_by_id(grammar.root_rule_id)
        self._ast_class = ast_class
        self._lstm_hidden_dim = lstm_hidden_dim
        self._num_lstm_layers = num_lstm_layers
        
        # Production Rules + PAD Rule
        self._rule_pad_index = rule_pad_index
        self._num_rules = grammar.num_rules + 1
        self._rule_embedding_dim = rule_embedding_dim
        print("Rule Pad Index: ", self._rule_pad_index)

        # Non-Terminals + PAD Node
        self._nonterminal_end_index = nonterminal_end_index
        self._nonterminal_pad_index = nonterminal_pad_index
        self._num_nonterminals = grammar.num_non_terminals + 2
        self._nonterminal_embedding_dim = nonterminal_embedding_dim
        print("Non-Terminal Pad Index: ", self._nonterminal_pad_index)
        print("Non-Terminal End Index: ", self._nonterminal_end_index)

        self._source_encoding_dim = source_encoding_dim
        self._max_target_length = max_target_length
        
        self._transform_encodings_key = nn.Linear(source_encoding_dim, self._lstm_hidden_dim)
        self._transform_encodings_value = nn.Linear(source_encoding_dim, self._lstm_hidden_dim)

        # Input: (Attention Context + Previous Rule Embedding + Current Nonterminal Embedding)
        decode_lstm_input_dim = lstm_hidden_dim + rule_embedding_dim + nonterminal_embedding_dim
        
        self._decoder_lstm = nn.LSTM(
            input_size=decode_lstm_input_dim,
            hidden_size=lstm_hidden_dim,
            num_layers=num_lstm_layers,
            batch_first=False
        )
        self._attn_dropout = nn.Dropout(p=dropout)
        self._decode_dropout = nn.Dropout(p=dropout)
        self._rule_embedder = Embedding(self._num_rules, rule_embedding_dim)
        self._nonterminal_embedder = Embedding(self._num_nonterminals, nonterminal_embedding_dim)
        self._attention_hidden_layer = nn.Sequential(
            nn.Linear(lstm_hidden_dim + lstm_hidden_dim, lstm_hidden_dim),
            nn.Tanh(),
        )
        # Rule Predictions
        self._rule_prediction_layer = nn.Sequential(
            nn.Linear(lstm_hidden_dim, rule_embedding_dim),
            # nn.Tanh()
        )
        self._rule_prediction_bias = nn.Parameter(
            torch.FloatTensor(self._num_rules).zero_())
        self._copy_gate_layer = nn.Sequential(
            nn.Linear(lstm_hidden_dim, 1),
            nn.Sigmoid()
        )
        self._transform_for_copy_layer = nn.Sequential(
            nn.Linear(lstm_hidden_dim, source_encoding_dim)
        )

    @overrides
    def forward(self, 
        encodings: torch.Tensor,
        source_mask: torch.Tensor,
        source_token_copy_indices: torch.Tensor,
        target_rules: torch.Tensor,
        target_nonterminals: torch.Tensor,
        target_mask: torch.Tensor,
        target_allow_copy_mask: torch.Tensor,
        meta_field: List[Dict] = None,
    ):
        """
        :param encodings:              (batch_size, length, hidden_dim)
        :param source_mask:            (batch_size, length)
        :param source_token_copy_indices: (batch_size, length, max_linked_rule_num)
        :param target_rules:           (batch_size, target_length)
        :param target_nonterminals:    (batch_size, target_length)
        :param target_mask:            (batch_size, target_length)
        :param target_allow_copy_mask: (batch_size, target_length)
        """
        if self.training:
            output_dict = self.train_decode(encodings, source_mask, source_token_copy_indices,
                                            target_rules, target_nonterminals, target_mask, target_allow_copy_mask)
        else:
            output_dict = self.eval_decode(
                encodings, source_mask, source_token_copy_indices)
        return output_dict

    def compute_copy_probs(self, encodings, source_mask, attention_vector):
        """
        :param encodings:        (length, hidden_dim)
        :param source_mask:      (length,)
        :param attention_vector: (hidden_dim)
        """
        # Attention
        # (1, hidden_dim)
        unsqueezed_attention_vector = self._transform_for_copy_layer(attention_vector).unsqueeze(0)
        weights = unsqueezed_attention_vector.mm(encodings.permute(1, 0)).squeeze(0)
        weights = weights.masked_fill((1 - source_mask).bool(), float('-inf'))
        weights = F.softmax(weights, dim=-1)
        return weights

    def train_decode(self, encodings, source_mask, source_token_copy_indices, target_rules, target_nonterminals, target_mask, target_allow_copy_mask):
        source_length = encodings.size(1)
        batch_size, target_length = target_rules.size()
        prev_attention_context = encodings.new_zeros((batch_size, 1, self._lstm_hidden_dim))
        source_encoding_key, source_encoding_value = self._transform_encodings_key(encodings), self._transform_encodings_value(encodings)

        h = encodings.new_zeros([self._num_lstm_layers, batch_size, self._lstm_hidden_dim])
        c = encodings.new_zeros([self._num_lstm_layers, batch_size, self._lstm_hidden_dim])
        decoder_hidden_state = (h, c)

        rule_probs = list()

        for ts in range(target_length - 1):
            # Input
            # (batch_size, 1, rule_embedding_size)
            prev_rule_embedded = self._rule_embedder(target_rules[:, ts].unsqueeze(1).long())
            prev_embedded = prev_rule_embedded

            # (batch_size, 1, nonterminal_embedding_size)
            curr_nonterminal_embedded = self._nonterminal_embedder(target_nonterminals[:, ts].unsqueeze(1).long())
            decoder_inputs = torch.cat([prev_embedded, curr_nonterminal_embedded, prev_attention_context], dim=-1)

            # Step
            decoder_outputs, context, attention_vector, decoder_hidden_state, attention_weights = self.take_decode_step(
                source_encoding_key, 
                source_encoding_value, 
                source_mask,
                decoder_inputs,
                decoder_hidden_state
            )
            # (batch_size, ts + 1, length)
            prev_attention_context = attention_vector

            # Production Rules
            # (batch_size, num_rules)
            rule_scores = F.linear(
                self._rule_prediction_layer(attention_vector.squeeze(1)), 
                weight=self._rule_embedder.weight,
                bias=self._rule_prediction_bias
            )
            # Copy Gate
            # (batch_size, 1)
            copy_gate = self._copy_gate_layer(attention_vector.squeeze(1))
            curr_rule_probs = list()
            for bidx in range(batch_size):
                # Keep Valid Rule
                nonterminal_id = int(target_nonterminals[bidx, ts])
                if nonterminal_id == self._nonterminal_pad_index or nonterminal_id == self._nonterminal_end_index:
                    active_rule_ids = [0]
                else:
                    active_rule_ids = self._grammar.get_production_rule_ids_by_nonterminal_id(nonterminal_id)
                # (num_rules)
                active_rule_mask = nn_utils.get_one_hot_mask(self._num_rules, active_rule_ids).to(rule_scores.device)
                probs = F.softmax(rule_scores[bidx, :].masked_fill(
                    (1 - active_rule_mask).bool(), float('-inf')), dim=-1)

                if target_allow_copy_mask[bidx, ts] == 1:
                    # (source_length, max_linked_rule_num)
                    token_copy_indices = source_token_copy_indices[bidx]
                    # (source_length, num_rules)
                    one_hot_token_copy_indices = (torch.sum(
                        torch.nn.functional.one_hot(token_copy_indices, self._num_rules), dim=1) > 0).float()

                    if torch.sum((torch.sum(one_hot_token_copy_indices, dim=0) > 0).float() * active_rule_mask.float()) > 0:
                        # allow soft copy
                        copy_score_gate = copy_gate.squeeze(-1)[bidx]
                        # (source_length)
                        copy_scores = attention_weights[bidx, 0, :]
                        # copy_scores = self.compute_copy_probs(
                        #     encodings[bidx, :, :], source_mask[bidx, :], attention_vector.squeeze(1)[bidx, :])
                        # There is a chance that we can copy from source
                        # num_rules
                        copy_scores = torch.sum(
                            copy_scores.unsqueeze(-1) * one_hot_token_copy_indices.float(),
                            dim=0
                        )
                        copy_scores.masked_fill_(
                            (1 - active_rule_mask).bool(), float('-inf'))
                        normalized_copy_scores = F.softmax(copy_scores, dim=-1)
                        # Score
                        probs = copy_score_gate * normalized_copy_scores + \
                            (1 - copy_score_gate) * probs
                curr_rule_probs.append(probs)
            curr_rule_probs = torch.stack(curr_rule_probs, dim=0)
            rule_probs.append(curr_rule_probs)

        rule_probs = torch.stack(rule_probs, dim=0).permute(1, 0, 2)

        # Loss
        loss = self.get_loss(rule_probs=rule_probs, target_rules=target_rules[:, 1:].long(), target_mask=target_mask[:, 1:].float())

        # Predicted Labels
        _, predicted_rules = rule_probs.max(dim=-1)
        output_dict = {"loss": loss, "predicted_rules": predicted_rules}
        return output_dict

    def eval_decode(self, encodings, source_mask, source_token_copy_indices):
        batch_size, source_length, _ = encodings.size()
        prev_attention_context = encodings.new_zeros((batch_size, 1, self._lstm_hidden_dim))
        source_encoding_key, source_encoding_value = self._transform_encodings_key(encodings), self._transform_encodings_value(encodings)

        h = encodings.new_zeros([self._num_lstm_layers, batch_size, self._lstm_hidden_dim])
        c = encodings.new_zeros([self._num_lstm_layers, batch_size, self._lstm_hidden_dim])
        decoder_hidden_state = (h, c)

        rule_pad_index_tensor = torch.Tensor([self._rule_pad_index]).long().to(encodings.device)
        nonterminal_pad_index_tensor = torch.Tensor([self._nonterminal_pad_index]).long().to(encodings.device)

        ast_results, is_complete, recorded_copy_gates, recorded_copy_weights = list(), list(), list(), list()
        for i in range(batch_size):
            ast_results.append(self._ast_class(root_rule=self._root_rule))
            is_complete.append(False)

        for ts in range(self._max_target_length):
            prev_embedded = list()
            curr_nonterminal_embedded = list()

            for bidx, ast in enumerate(ast_results):
                if is_complete[bidx]:
                    # PAD
                    prev_embedded.append(self._rule_embedder(rule_pad_index_tensor))
                    curr_nonterminal_embedded.append(self._nonterminal_embedder(nonterminal_pad_index_tensor))
                else:
                    last_production_rule = ast.get_last_production_rule()
                    # Rule
                    rule_index_tensor = torch.Tensor([last_production_rule.rule_id]).long().to(encodings.device)
                    prev_embedded.append(self._rule_embedder(rule_index_tensor))
                    # Curr Non-Terminal
                    curr_non_terminal_id = self._grammar.get_non_terminal_id(ast.get_curr_non_terminal())
                    nonterminal_index_tensor = torch.Tensor([curr_non_terminal_id]).long().to(encodings.device)
                    curr_nonterminal_embedded.append(
                        self._nonterminal_embedder(nonterminal_index_tensor)
                    )

            # (batch_size, 1, rule_embedding_size)
            prev_embedded = torch.stack(prev_embedded, dim=0)
            # (batch_size, 1, type_embedding_size)
            curr_nonterminal_embedded = torch.stack(curr_nonterminal_embedded, dim=0)
            decoder_inputs = torch.cat([prev_embedded, curr_nonterminal_embedded, prev_attention_context], dim=-1)

            # Step
            decoder_outputs, context, attention_vector, decoder_hidden_state, attention_weights = self.take_decode_step(
                source_encoding_key,
                source_encoding_value,
                source_mask,
                decoder_inputs,
                decoder_hidden_state
            )
            prev_attention_context = attention_vector

            # Production Rules
            # (batch_size, num_rules)
            rule_scores = F.linear(
                self._rule_prediction_layer(attention_vector.squeeze(1)), 
                weight=self._rule_embedder.weight,
                bias=self._rule_prediction_bias
            )
            # Copy Gate
            # (batch_size, 1)
            copy_gate = self._copy_gate_layer(attention_vector.squeeze(1))
            recorded_copy_gates.append(copy_gate.squeeze(1))

            # (batch_size, source_length)
            batch_copy_scores = attention_weights.squeeze(dim=1)
            recorded_copy_weights.append(batch_copy_scores)

            is_finish = True
            for bidx, ast in enumerate(ast_results):
                if not is_complete[bidx]:
                    curr_non_terminal = ast.get_curr_non_terminal()
                    # Rule
                    active_rule_ids = self._grammar.get_production_rule_ids_by_nonterminal(curr_non_terminal)
                    active_rule_mask = nn_utils.get_one_hot_mask(self._num_rules, active_rule_ids).to(rule_scores.device)
                    brule_scores = rule_scores[bidx, :].masked_fill((1 - active_rule_mask).bool(), float('-inf'))
                    curr_rule_probs = F.softmax(brule_scores, dim=-1)

                    if curr_non_terminal in self._grammar.copy_terminal_set:
                        # TODO examinze
                        # Copy
                        # (source_length, max_linked_rule_num)
                        token_copy_indices = source_token_copy_indices[bidx]
                        # (source_length, num_rules)
                        one_hot_token_copy_indices = (torch.sum(
                            torch.nn.functional.one_hot(token_copy_indices, self._num_rules), dim=1) > 0).float()

                        if torch.sum((torch.sum(one_hot_token_copy_indices, dim=0) > 0).float() * active_rule_mask.float()) > 0:
                            # allow soft copy
                            copy_score_gate = copy_gate.squeeze(-1)[bidx]
                            # (source_length)
                            copy_scores = attention_weights[bidx, 0, :]
                            # copy_scores = self.compute_copy_probs(
                            #     encodings[bidx, :, :], source_mask[bidx, :], attention_vector.squeeze(1)[bidx, :])

                            # There is a chance that we can copy from source
                            # (num_rules)
                            copy_scores = torch.sum(
                                copy_scores.unsqueeze(-1) *
                                one_hot_token_copy_indices.float(),
                                dim=0
                            )
                            copy_scores.masked_fill_(
                                (1 - active_rule_mask).bool(), float('-inf'))
                            normalized_copy_scores = F.softmax(copy_scores, dim=-1)
                            # Score
                            curr_rule_probs = copy_score_gate * normalized_copy_scores + \
                                (1 - copy_score_gate) * curr_rule_probs

                    rule_id = int(torch.argmax(curr_rule_probs))
                    production_rule = self._grammar.get_production_rule_by_id(rule_id)
                    ast.add_rule(production_rule)

                    if ast.is_complete:
                        is_complete[bidx] = True
                    else:
                        is_finish = False
            if is_finish:
                break

        # Pad For evaluation
        predicted_rules = list()
        max_length = 0
        for ast in ast_results:
            rules = ast.get_production_rules()
            rule_ids = [rule.rule_id for rule in rules]
            predicted_rules.append(np.array(rule_ids, dtype=int))
            if len(rules) > max_length:
                max_length = len(rules)
        # Pad
        for i in range(batch_size):
            if len(predicted_rules[i]) < max_length:
                predicted_rules[i] = np.concatenate(
                    [predicted_rules[i], np.ones(max_length - len(predicted_rules[i])) * self._rule_pad_index],
                    axis=0
                )
        predicted_rules = torch.from_numpy(np.array(predicted_rules, dtype=int)).to(encodings.device)

        recorded_copy_gates = torch.stack(recorded_copy_gates, dim=0).transpose(dim0=1, dim1=0)
        recorded_copy_weights = torch.stack(recorded_copy_weights, dim=0).permute(1, 0, 2)

        output_dict = {
            "loss": torch.Tensor([0.0]).to(encodings.device),
            "predicted_rules": predicted_rules.long(),
            "recorded_copy_gates": recorded_copy_gates,
            "recorded_copy_weights": recorded_copy_weights
        }
        return output_dict

    def take_decode_step(self,
        source_encoding_key: torch.Tensor,
        source_encoding_value: torch.Tensor,
        source_mask: torch.Tensor,
        decoder_inputs: torch.Tensor,
        decoder_hidden_state: Tuple[torch.Tensor, torch.Tensor],
    ):
        """
        :param source_encoding_key:   (batch_size, length, hidden_dim)
        :param source_encoding_value: (batch_size, length, hidden_dim)
        :param source_mask:           (batch_size, length)
        :decoder_inputs:              (batch_size, 1, lstm_hidden_dim + rule_embedding_dim + nonterminal_embedding_dim)
        :decoder_hidden_state:        (h, c)
        :return
            decoder_outputs:  (batch_size, 1, lstm_hidden_dim)
            context:          (batch_size, 1, hidden_dim)
            att:              (batch_size, 1, lstm_hidden_dim)
            decoder_hidden_state: (h, c)
        """
        decoder_outputs, (h, c) = self._decoder_lstm(decoder_inputs.permute(1, 0, 2), decoder_hidden_state)
        decoder_hidden_state = (h, c)
        # (batch_size, 1, lstm_hidden_dim)
        decoder_outputs = decoder_outputs.permute(1, 0, 2)

        # Attention
        # (batch_size, 1, length)
        raw_weights = decoder_outputs.bmm(source_encoding_key.permute(0, 2, 1))
        weights = raw_weights.masked_fill((1 - source_mask.unsqueeze(1)).bool(), float('-inf'))
        weights = F.softmax(weights, dim=-1)
        # (batch_size, 1, hidden_dim)
        context = weights.bmm(source_encoding_value)

        att = self._attention_hidden_layer(torch.cat([decoder_outputs, context], dim=-1))
        att = self._attn_dropout(att)

        return decoder_outputs, context, att, decoder_hidden_state, raw_weights

    def get_loss(self,
        rule_probs: torch.FloatTensor,
        target_rules: torch.LongTensor,
        target_mask: torch.FloatTensor,
    ):
        """
        :param rule_probs   (batch_size, target_length, num_rules)
        :param target_mask  (batch_size, target_length)
        """
        batch_size, target_length = target_rules.size()
        rule_probs = torch.gather(
            rule_probs.reshape(-1, self._num_rules), 
            dim=1, 
            index=target_rules.reshape(-1).unsqueeze(-1).long()
        )
        rule_probs = rule_probs.reshape(batch_size, target_length)
        rule_log_probs = (rule_probs + 1e-10).log()
        rule_log_probs *= target_mask.float()
        rule_normalize_factor = target_mask.sum(-1)
        rule_normalize_factor[rule_normalize_factor == 0] = 1
        rule_loss = rule_log_probs.sum(-1) / rule_normalize_factor.float()
        rule_loss = -1 * (rule_loss.sum() / batch_size)
        return rule_loss
