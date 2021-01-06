# coding=utf8

import math
import torch
import numpy as np
import torch.nn as nn
from allennlp.nn import util
from torch.nn import Parameter
import torch.nn.functional as F
from torch.nn.init import xavier_uniform_


class GNNMatrixMultiHeadAttention(nn.Module):

    def __init__(self, d_model: int, nhead: int, nlabels: int,
                 dropout: float = 0.1):
        super().__init__()
        assert d_model % nhead == 0
        self._d_model = d_model
        self._nhead = nhead
        self._nlabels = nlabels

        self._d_q = int(d_model / nhead)
        self._w_q = nn.Linear(d_model, d_model)
        self._attention_temperature = np.power(self._d_q, 0.5)
        self._w_ks = Parameter(torch.Tensor(nlabels, d_model, d_model))
        self._w_h = nn.Linear(d_model, d_model)

        self._dropout = nn.Dropout(dropout)
        self._attn_dropout = nn.Dropout(dropout)
        self._reset_parameters()

    def _reset_parameters(self):
        xavier_uniform_(self._w_q.weight)
        xavier_uniform_(self._w_h.weight)
        xavier_uniform_(self._w_ks)

    def forward(self, q: torch.Tensor, k: torch.Tensor, edge_mask: torch.Tensor,
                padding_mask: torch.Tensor):
        """
        q and k must have the same dimension
        :param q: (batch_size, len_q, d_model)
        :param k: (batch_size, len_k, d_model)
        :param edge_mask: (batch_size, len_q, len_k, nlabels)
        :param padding_mask: (batch_size, len_q, len_k)
        :return:
            shape: (batch_size, len_q, d_model)
        """
        sz_b, len_q, _ = q.size()
        sz_b, len_k, _ = k.size()

        # shape: (nlabels, batch_size, len_q, len_k)
        mask = edge_mask.permute(3, 0, 1, 2)

        query = self._w_q(q).view(sz_b, len_q, self._nhead, self._d_q)
        # shape: (nhead * sz_b, len_q, d_q)
        query = query.permute(2, 0, 1, 3).contiguous().view(-1, len_q, self._d_q)

        # shape: (nhead * sz_b, len_k, d_q)
        edge_values = list()
        attention_weights = list()
        for i in range(self._nlabels):
            w = self._w_ks[i]
            ek = F.linear(k, w).view(sz_b, len_k, self._nhead, self._d_q)
            # shape: (nhead * sz_b, len_k, d_q)
            ek = ek.permute(2, 0, 1, 3).contiguous().view(-1, len_k, self._d_q)
            edge_values.append(ek)

            aw = query.bmm(ek.permute(0, 2, 1))
            attention_weights.append(aw / self._attention_temperature)

        # (nlabels, sz_b * nhead, len_q, len_k)
        attention_weights = torch.stack(attention_weights, dim=0)
        # (nlabels, sz_b * nhead, len_q, len_k)
        attention_weights = attention_weights * mask.repeat(1, self._nhead, 1, 1)
        attention_weights = attention_weights.sum(dim=0)

        # shape: (nhead * sz_b, len_q, len_k)
        attention_weights = attention_weights.masked_fill(
            padding_mask.repeat(self._nhead, 1, 1).bool(),
            float('-inf'),
        )
        attention_weights = F.softmax(attention_weights, dim=-1)
        attention_weights = self._attn_dropout(attention_weights)

        output = attention_weights.new_zeros((self._nhead * sz_b, len_q, self._d_q))
        for i in range(self._nlabels):
            v, m = edge_values[i], mask[i]
            _m = m.repeat(self._nhead, 1, 1)
            output += (attention_weights * _m).bmm(v)

        output = output.view(self._nhead, sz_b, len_q, self._d_q)
        output = output.permute(1, 2, 0, 3).contiguous().view(sz_b, len_q, -1)
        output = self._w_h(output)

        return output


class GNNVectorMultiHeadAttention(nn.Module):

    def __init__(self, d_model: int, nhead: int, nlabels: int,
                 dropout: float = 0.1):
        super().__init__()
        assert d_model % nhead == 0
        self._d_model = d_model
        self._nhead = nhead
        self._nlabels = nlabels

        self._d_q = int(d_model / nhead)
        self._w_q = nn.Linear(d_model, d_model)
        self._attention_temperature = np.power(self._d_q, 0.5)
        self._w_k = Parameter(torch.Tensor(d_model, d_model))
        self._w_v = Parameter(torch.Tensor(d_model, d_model))
        self._b_ks = Parameter(torch.Tensor(self._nlabels, d_model))
        self._b_vs = Parameter(torch.Tensor(self._nlabels, d_model))
        self._w_h = nn.Linear(d_model, d_model)

        self._dropout = nn.Dropout(dropout)
        self._attn_dropout = nn.Dropout(dropout)
        self._reset_parameters()

    def _reset_parameters(self):
        xavier_uniform_(self._w_q.weight)
        xavier_uniform_(self._w_h.weight)
        xavier_uniform_(self._w_k)
        xavier_uniform_(self._w_v)
        xavier_uniform_(self._b_ks)
        xavier_uniform_(self._b_vs)

    def forward(self, q: torch.Tensor, k: torch.Tensor, edge_mask: torch.Tensor,
                padding_mask: torch.Tensor):
        """
        q and k must have the same dimension
        :param q: (batch_size, len_q, d_model)
        :param k: (batch_size, len_k, d_model)
        :param edge_mask: (batch_size, len_q, len_k, nlabels)
        :param padding_mask: (batch_size, len_q, len_k), where True values are positions that should be masked
                            with float('-inf') and False values will be unchanged.
        :return:
            shape: (batch_size, len_q, d_model)
        """
        sz_b, len_q, _ = q.size()
        sz_b, len_k, _ = k.size()

        self._w_k.to(k.device)

        query = self._w_q(q).view(sz_b, len_q, self._nhead, self._d_q)
        # shape: (nhead * sz_b, len_q, d_q)
        query = query.permute(2, 0, 1, 3).contiguous().view(-1, len_q, self._d_q)

        # key
        edge_vectors = torch.mm(edge_mask.reshape(-1, self._nlabels), self._b_ks).reshape(sz_b, len_q, len_k,
                                                                                          self._d_model)
        # shape: (sz_b, len_k, d_model)
        key = F.linear(k, self._w_k)
        # shape: (sz_b, len_q, len_k, d_model)
        key = key.unsqueeze(1).repeat(1, len_q, 1, 1)
        key = edge_vectors + key
        key = key.view(sz_b, len_q, len_k, self._nhead, self._d_q).permute(3, 0, 1, 2, 4)
        # shape: (nhead * sz_b, len_q, len_k, d_q)
        key = key.contiguous().view(-1, len_q, len_k, self._d_q)

        mask = (edge_mask.sum(-1) > 0).float().repeat(self._nhead, 1, 1)

        # shape: (nhead * sz_b, len_q, len_k)
        attention_weights = torch.mul(query.unsqueeze(2).repeat(1, 1, len_k, 1), key).sum(-1)
        attention_weights = attention_weights / self._attention_temperature
        attention_weights = attention_weights * mask
        attention_weights = attention_weights.masked_fill(
            padding_mask.repeat(self._nhead, 1, 1).bool(),
            float('-inf'),
        )
        attention_weights = F.softmax(attention_weights, dim=-1)
        attention_weights = self._attn_dropout(attention_weights)

        # value
        # shape: (sz_b, len_k, d_model)
        # value = F.linear(k, self._w_v)
        # # shape: (sz_b, len_q, len_k, d_model)
        # value = value.unsqueeze(1).repeat(1, len_q, 1, 1)
        # value = edge_vectors + value
        # value = value.view(sz_b, len_q, len_k, self._nhead, self._d_q).permute(3, 0, 1, 2, 4)
        # # shape: (nhead * sz_b, len_q, len_k, d_q)
        # value = value.contiguous().view(-1, len_q, len_k, self._d_q)
        value = key

        output = ((attention_weights * mask).unsqueeze(-1) * value).sum(2)
        output = output.view(self._nhead, sz_b, len_q, self._d_q)
        output = output.permute(1, 2, 0, 3).contiguous().view(sz_b, len_q, -1)
        output = self._w_h(output)

        return output


class GNNVectorMultiHeadAttention2(nn.Module):
    """
    Implementation based on "Self-Attention with Relative Position Representations"
    According to Tensor2Tensor
    https://github.com/tensorflow/tensor2tensor/blob/ab918e0d9592394614aa2e10cfc8f23e8cb24dfc/tensor2tensor/layers/common_attention.py
    """

    def __init__(self, d_model: int, nhead: int, nlabels: int,
                 dropout: float = 0.1):
        super().__init__()
        assert d_model % nhead == 0
        self._d_model = d_model
        self._nhead = nhead
        self._nlabels = nlabels

        self._d_q = int(d_model / nhead)
        self._attention_temperature = np.power(self._d_q, 0.5)

        self._w_q = nn.Linear(d_model, d_model)
        self._w_k = Parameter(torch.Tensor(d_model, d_model))
        self._w_v = Parameter(torch.Tensor(d_model, d_model))
        self._w_h = nn.Linear(d_model, d_model)

        self._b_ks = Parameter(torch.Tensor(self._nlabels, self._d_q))
        self._b_vs = Parameter(torch.Tensor(self._nlabels, self._d_q))

        self._dropout = nn.Dropout(dropout)
        self._attn_dropout = nn.Dropout(dropout)
        self._reset_parameters()

    def _reset_parameters(self):
        xavier_uniform_(self._w_q.weight)
        xavier_uniform_(self._w_h.weight)
        xavier_uniform_(self._w_k)
        xavier_uniform_(self._w_v)
        xavier_uniform_(self._b_ks)
        xavier_uniform_(self._b_vs)

    def forward(self, q: torch.Tensor, k: torch.Tensor, edge_mask: torch.Tensor,
                padding_mask: torch.Tensor):
        """
        q and k must have the same dimension
        :param q: (batch_size, len_q, d_model)
        :param k: (batch_size, len_k, d_model)
        :param edge_mask: (batch_size, len_q, len_k, nlabels)
        :param padding_mask:(batch_size, len_q, len_k), where True values are positions that should be masked
                            with float('-inf') and False values will be unchanged.
        :return:
            shape: (batch_size, len_q, d_model)
        """
        sz_b, len_q, _ = q.size()
        sz_b, len_k, _ = k.size()

        self._w_k.to(k.device)

        query = self._w_q(q).view(sz_b, len_q, self._nhead, self._d_q)
        # shape: (nhead * sz_b, len_q, d_q)
        query = query.permute(2, 0, 1, 3).contiguous().view(-1, len_q, self._d_q)
        # shape: (nhead * sz_b, len_q, len_k, d_q)
        expanded_query = query.unsqueeze(2).repeat(1, 1, len_k, 1)

        # Relation Embeddings
        # shape: (sz_b, len_q, len_k, d_q)
        key_relation_embeded = torch.mm(edge_mask.reshape(-1, self._nlabels), self._b_ks).reshape(sz_b, len_q, len_k,
                                                                                                  self._d_q)
        # shape: (nhead * sz_b, len_q, len_k, d_q)
        key_relation_embeded = key_relation_embeded.repeat(self._nhead, 1, 1, 1)

        # shape: (sz_b, len_k, d_model)
        key = F.linear(k, self._w_k)
        # shape: (nhead * sz_b, len_k, d_q)
        key = key.view(sz_b, len_k, self._nhead, self._d_q).permute(2, 0, 1, 3).contiguous().view(-1, len_k, self._d_q)

        # shape: (nhead * sz_b, len_q, len_k)
        qk_weights = query.bmm(key.permute(0, 2, 1))
        # shape: (nhead * sz_b, len_q, len_k)
        qkr_weights = torch.mul(expanded_query, key_relation_embeded).sum(-1)

        attention_weights = qk_weights + qkr_weights
        output_attention_weights = attention_weights / self._attention_temperature
        # attention_weights = attention_weights.masked_fill(
        #     padding_mask.repeat(self._nhead, 1, 1).bool(),
        #     float('-inf'),
        # )
        # relation mask
        # shape: (nhead * sz_b, len_q, len_k)
        # Note that we need ensure that there are at least one relations for each position

        # eye_mask = torch.eye(len_q).unsqueeze(0).repeat(sz_b, 1, 1).to(edge_mask.device)
        # relation_mask = ((edge_mask.sum(-1) + eye_mask + (1 - padding_mask)) == 0).repeat(self._nhead, 1, 1)
        relation_mask = ((edge_mask.sum(-1) + (1 - padding_mask)) == 0).repeat(self._nhead, 1, 1)
        attention_weights = output_attention_weights.masked_fill(
            relation_mask.bool(),
            float('-inf'),
        )
        attention_weights = F.softmax(attention_weights, dim=-1)
        attention_weights = attention_weights.masked_fill(
            relation_mask.bool(),
            0.0
        )
        # Remove nan
        # attention_weights[attention_weights != attention_weights] = 0
        attention_weights = self._attn_dropout(attention_weights)

        # Value Relation Embeddings
        # shape: (sz_b, len_q, len_k, d_q)
        value_relation_embeded = torch.mm(edge_mask.reshape(-1, self._nlabels), self._b_vs).reshape(sz_b, len_q, len_k,
                                                                                                    self._d_q)
        # shape: (nhead * sz_b, len_q, len_k, d_q)
        value_relation_embeded = value_relation_embeded.repeat(self._nhead, 1, 1, 1)

        # shape: (sz_b, len_k, d_model)
        value = F.linear(k, self._w_v)
        # shape: (nhead * sz_b, len_k, d_q)
        value = value.view(sz_b, len_k, self._nhead, self._d_q).permute(2, 0, 1, 3).contiguous().view(-1, len_k,
                                                                                                      self._d_q)

        # shape: (nhead * sz_b, len_q, d_q)
        qv_output = attention_weights.bmm(value)
        # shape: (nhead * sz_b, len_q, d_q)
        qvr_output = torch.mul(attention_weights.unsqueeze(-1), value_relation_embeded).sum(2)
        output = qv_output + qvr_output

        output = output.view(self._nhead, sz_b, len_q, self._d_q)
        output = output.permute(1, 2, 0, 3).contiguous().view(sz_b, len_q, -1)

        output = self._w_h(output)

        return output, output_attention_weights


class GNNVectorContinuousMultiHeadAttention(nn.Module):

    def __init__(self, d_model: int, nhead: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % nhead == 0
        self._d_model = d_model
        self._nhead = nhead

        self._d_q = int(d_model / nhead)
        self._w_q = nn.Linear(d_model, d_model)
        self._attention_temperature = np.power(self._d_q, 0.5)
        self._w_k = Parameter(torch.Tensor(d_model, d_model))
        self._w_v = Parameter(torch.Tensor(d_model, d_model))
        self._w_h = nn.Linear(d_model, d_model)

        self._dropout = nn.Dropout(dropout)
        self._attn_dropout = nn.Dropout(dropout)
        self._reset_parameters()

    def _reset_parameters(self):
        xavier_uniform_(self._w_q.weight)
        xavier_uniform_(self._w_h.weight)
        xavier_uniform_(self._w_k)
        xavier_uniform_(self._w_v)

    def forward(self, q: torch.Tensor, k: torch.Tensor, edge_mask: torch.Tensor,
                padding_mask: torch.Tensor):
        """
        q and k must have the same dimension
        :param q: (batch_size, len_q, d_model)
        :param k: (batch_size, len_k, d_model)
        :param edge_mask: (batch_size, len_q, len_k, d_model)
        :param padding_mask: (batch_size, len_q, len_k), where True values are positions that should be masked
                            with float('-inf') and False values will be unchanged.
        :return:
            shape: (batch_size, len_q, d_model)
        """
        sz_b, len_q, _ = q.size()
        sz_b, len_k, _ = k.size()

        # query
        query = self._w_q(q).view(sz_b, len_q, self._nhead, self._d_q)
        # shape: (nhead * sz_b, len_q, d_q)
        query = query.permute(2, 0, 1, 3).contiguous().view(-1, len_q, self._d_q)

        # key
        # shape: (sz_b, len_k, d_model)
        key = F.linear(k, self._w_k)
        # shape: (sz_b, len_q, len_k, d_model)
        key = key.unsqueeze(1).repeat(1, len_q, 1, 1)
        key = edge_mask + key
        key = key.view(sz_b, len_q, len_k, self._nhead, self._d_q).permute(3, 0, 1, 2, 4)
        # shape: (nhead * sz_b, len_q, len_k, d_q)
        key = key.contiguous().view(-1, len_q, len_k, self._d_q)

        # shape: (nhead * sz_b, len_q, len_k)
        attention_weights = torch.mul(query.unsqueeze(2).repeat(1, 1, len_k, 1), key).sum(-1)
        attention_weights = attention_weights / self._attention_temperature
        attention_weights = attention_weights.masked_fill(
            padding_mask.repeat(self._nhead, 1, 1).bool(),
            float('-inf'),
        )
        attention_weights = F.softmax(attention_weights, dim=-1)
        attention_weights = self._attn_dropout(attention_weights)

        # value
        # shape: (sz_b, len_k, d_model)
        value = F.linear(k, self._w_v)
        # shape: (sz_b, len_q, len_k, d_model)
        value = value.unsqueeze(1).repeat(1, len_q, 1, 1)
        value = edge_mask + value
        value = value.view(sz_b, len_q, len_k, self._nhead, self._d_q).permute(3, 0, 1, 2, 4)
        # shape: (nhead * sz_b, len_q, len_k, d_q)
        value = value.contiguous().view(-1, len_q, len_k, self._d_q)

        # shape: (nhead * sz_b, len_q, d_p)
        output = (attention_weights.unsqueeze(-1) * value).sum(2)
        output = output.view(self._nhead, sz_b, len_q, self._d_q)
        output = output.permute(1, 2, 0, 3).contiguous().view(sz_b, len_q, -1)
        output = self._w_h(output)

        return output
