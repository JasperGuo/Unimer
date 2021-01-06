# coding=utf8

import copy
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import MultiheadAttention
from .gnn_multi_head_attention import GNNMatrixMultiHeadAttention, GNNVectorMultiHeadAttention, \
    GNNVectorContinuousMultiHeadAttention, GNNVectorMultiHeadAttention2


def _get_clones(module, N):
    return nn.ModuleList([copy.deepcopy(module) for i in range(N)])


def get_decode_edge_mask(tgt, max_decode_clip_range):
    """
    :param max_decode_clip_range:
    :param tgt: (tgt_length, batch_size, d_model)
    :return:
        (batch_size, max_decode_clip_range, tgt_length, tgt_length)
    """
    tgt_length, batch_size, _ = tgt.size()
    edge_mask = list()
    i = 0
    while i < tgt_length and i < max_decode_clip_range + 1:
        mask = torch.diag(tgt.new_ones(tgt_length - i))
        if mask.size(0) == tgt_length:
            edge_mask.append(mask)
        else:
            mask = F.pad(mask, [0, i, i, 0], mode='constant', value=0)
            edge_mask.append(mask)
        i += 1
    if i < max_decode_clip_range + 1:
        edge_mask = torch.stack(edge_mask, dim=0)
        # shape: (tgt_length, tgt_length, tgt_length)
        edge_mask = torch.cat((edge_mask, tgt.new_zeros([max_decode_clip_range - i + 1,
                                                         tgt_length, tgt_length])), dim=0)
    else:
        # i == max_decode_clip_range
        if i < tgt_length:
            edge_mask[-1] = torch.tril(tgt.new_ones([tgt_length, tgt_length]),
                                       diagonal=-1 * max_decode_clip_range)
        edge_mask = torch.stack(edge_mask, dim=0)
    edge_mask = edge_mask.unsqueeze(0).repeat(batch_size, 1, 1, 1)
    return edge_mask


class GNNTransformerEncoderLayer(nn.Module):

    def __init__(self, d_model: int, nhead: int, dim_feedforward: int, nlabels: int,
                 dropout=0.1, is_matrix=True, is_discrete: bool = True):
        super(GNNTransformerEncoderLayer, self).__init__()
        if is_matrix:
            self.self_attn = GNNMatrixMultiHeadAttention(d_model, nhead, nlabels, dropout)
        else:
            print("GNN Vector Multi Head Attention")
            if is_discrete:
                # self.self_attn = GNNVectorMultiHeadAttention(d_model, nhead, nlabels, dropout)
                self.self_attn = GNNVectorMultiHeadAttention2(d_model, nhead, nlabels, dropout)
            else:
                self.self_attn = GNNVectorContinuousMultiHeadAttention(d_model, nhead, dropout)
        # Implementation of Feedforward model
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(dim_feedforward, d_model)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

    def forward(self, src, edge_mask, padding_mask):
        """
        Each sub-layer is followed by a residual connection and layer normalization
        :param src:          (batch_size, src_length, d_model)
        :param edge_mask:    (batch_size, nlabels, src_length, src_length)
        :param padding_mask: (batch_size, src_length, src_length), where True values are positions that should be masked
                            with float('-inf') and False values will be unchanged.
        :return:
        """
        src2, attention_weights = self.self_attn.forward(q=src, k=src, edge_mask=edge_mask, padding_mask=padding_mask)

        src = src + self.dropout1(src2)
        src = self.norm1(src)

        src2 = self.linear2(self.dropout(F.relu(self.linear1(src))))
        src = src + self.dropout2(src2)
        src = self.norm2(src)
        return src, attention_weights


class GNNTransformerEncoderWithMemoryLayer(nn.Module):

    def __init__(self, d_model: int, nhead: int, dim_feedforward: int, memory_nlabels: int, self_nlabels: int,
                 dropout: float = 0.1, is_matrix: bool = True, kdim: int = None, vdim: int = None):
        super(GNNTransformerEncoderWithMemoryLayer, self).__init__()
        if is_matrix:
            self.attn = GNNMatrixMultiHeadAttention(d_model, nhead, memory_nlabels + self_nlabels, dropout)
        else:
            print("GNN Vector Multi Head Attention")
            self.attn = GNNVectorMultiHeadAttention2(d_model, nhead, memory_nlabels + self_nlabels, dropout)
        self._memory_nlabels = memory_nlabels
        self._self_nlabels = self_nlabels

        # Implementation of Feedforward model
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(dim_feedforward, d_model)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.dropout3 = nn.Dropout(dropout)

    def forward(self, memory, memory_edge_mask, memory_padding_mask, src, src_edge_mask, src_padding_mask):
        r"""Pass the inputs (and mask) through the decoder layer.
        Args:
            tgt: the sequence to the decoder layer (required).
            memory: the sequnce from the last layer of the encoder (required).
            tgt_mask: the mask for the tgt sequence (optional).
            memory_mask: the mask for the memory sequence (optional).
            tgt_key_padding_mask: the mask for the tgt keys per batch (optional).
            memory_key_padding_mask: the mask for the memory keys per batch (optional).
        Shape:
            :param memory:               (batch_size, memory_length, d_model)
            :param memory_edge_mask:     (batch_size, src_length, memory_length, memory_nlabels)
            :param memory_padding_mask:  (batch_size, src_length, memory_length), where True values are positions that should be masked
                                          with float('-inf') and False values will be unchanged.
            :param src:                  (batch_size, src_length, d_model)
            :param src_edge_mask:        (batch_size, src_length, src_length, nlabels,)
            :param src_padding_mask:     (batch_size, src_length, src_length), where True values are positions that should be masked
                                          with float('-inf') and False values will be unchanged.
        """
        # shape: (batch_size, memory_length + src_length, d_model)
        key = torch.cat([memory, src], dim=1)
        batch_size, src_length, memory_length, memory_nlabels = memory_edge_mask.size()
        self_nlabels = src_edge_mask.size(-1)

        # shape: (batch_size, src_length, memory_length, memory_nlabels + self_nlabels, )
        extended_memory_edge_mask = torch.cat([memory_edge_mask, memory_edge_mask.new_zeros((batch_size, src_length, memory_length, self_nlabels,))], dim=-1)
        # shape: (batch_size, src_length, src_length, memory_nlabels + self_nlabels)
        extended_src_edge_mask = torch.cat([src_edge_mask.new_zeros((batch_size, src_length, src_length, memory_nlabels)), src_edge_mask], dim=-1)

        # shape: (batch_size, src_length, memory_length + src_length, memory_nlabels + self_nlabels)
        edge_mask = torch.cat([extended_memory_edge_mask, extended_src_edge_mask], dim=2)

        # shape: (batch_size, src_length, memory_length + src_length)
        padding_mask = torch.cat([memory_padding_mask, src_padding_mask], dim=-1)

        src2 = self.attn.forward(q=src, k=key, edge_mask=edge_mask, padding_mask=padding_mask)
        src = src + self.dropout1(src2)
        src = self.norm1(src)

        src2 = self.linear2(self.dropout(F.relu(self.linear1(src))))
        src = src + self.dropout2(src2)
        src = self.norm2(src)
        return src


class GNNTransformerDecoderLayer(nn.Module):

    def __init__(self, d_model: int, nhead: int, dim_feedforward: int, nlabels: int,
                 dropout: float = 0.1, is_matrix: bool = True, kdim: int = None, vdim: int = None):
        super(GNNTransformerDecoderLayer, self).__init__()
        if is_matrix:
            self.self_attn = GNNMatrixMultiHeadAttention(d_model, nhead, nlabels, dropout)
        else:
            print("GNN Vector Multi Head Attention")
            self.self_attn = GNNVectorMultiHeadAttention2(d_model, nhead, nlabels, dropout)
        self.multihead_attn = nn.MultiheadAttention(d_model, nhead, dropout=dropout, kdim=kdim, vdim=vdim)
        # Implementation of Feedforward model
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(dim_feedforward, d_model)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.dropout3 = nn.Dropout(dropout)

    def forward(self, tgt, edge_mask, tgt_padding_mask, memory, memory_mask=None, memory_key_padding_mask=None):
        r"""Pass the inputs (and mask) through the decoder layer.
        Args:
            tgt: the sequence to the decoder layer (required).
            memory: the sequnce from the last layer of the encoder (required).
            tgt_mask: the mask for the tgt sequence (optional).
            memory_mask: the mask for the memory sequence (optional).
            tgt_key_padding_mask: the mask for the tgt keys per batch (optional).
            memory_key_padding_mask: the mask for the memory keys per batch (optional).
        Shape:
            :param tgt:         (tgt_length, batch_size, d_model)
            :param edge_mask:   (batch_size, nlabels, tgt_length, decode_length)
            :param tgt_padding_mask: (batch_size, tgt_length, tgt_length)
            :param memory:      (src_length, batch_size, d_model)
            :param memory_mask: (src_length, src_length)
            :param memory_key_padding_mask: (batch_size, src_length)
        """
        # shape: (batch_size, tgt_length, d_model)
        permuted_tgt = tgt.permute(1, 0, 2)
        tgt2, _ = self.self_attn(q=permuted_tgt, k=permuted_tgt, edge_mask=edge_mask, padding_mask=tgt_padding_mask)
        tgt2 = tgt2.permute(1, 0, 2)
        tgt = tgt + self.dropout1(tgt2)
        tgt = self.norm1(tgt)

        tgt2 = self.multihead_attn(tgt, memory, memory, attn_mask=memory_mask,
                                   key_padding_mask=memory_key_padding_mask)[0]
        tgt = tgt + self.dropout2(tgt2)
        tgt = self.norm2(tgt)

        tgt2 = self.linear2(self.dropout(F.relu(self.linear1(tgt))))
        tgt = tgt + self.dropout3(tgt2)
        tgt = self.norm3(tgt)
        return tgt


class GNNTransformerEncoder(nn.Module):

    def __init__(self, encoder_layer: GNNTransformerEncoderLayer,
                 num_layers: int, norm=None, output_weights: bool = False):
        super(GNNTransformerEncoder, self).__init__()
        self.layers = _get_clones(encoder_layer, num_layers)
        self.num_layers = num_layers
        self.norm = norm
        self._output_weights = output_weights

    def forward(self, src, edge_mask, padding_mask=None):
        """
        :param src:          (src_length, batch_size, encoder_d_model)
        :param edge_mask:    (batch_size, src_length, src_length, nlabels,) | (batch_size, num_layers, src_length, src_length, nlabels)
        :param padding_mask: (batch_size, src_length)
        where True values are positions that should be masked with float('-inf') and False values will be unchanged.
        :return:
            (src_length, batch_size, d_model)
        """
        # shape: (batch_size, src_length, d_model)
        length, batch_size, _ = src.size()
        if padding_mask is None:
            padding_mask = edge_mask.new_ones((batch_size, length, length)).float()
        else:
            padding_mask = padding_mask.unsqueeze(1).expand(batch_size, length, length).float()

        # shape: (batch_size, src_length, d_model)
        output = src.permute(1, 0, 2)
        layer_weights = list()
        for i in range(self.num_layers):
            if len(edge_mask.size()) == 4:
                # (nhead * batch_size, src_length, src_length)
                output, attention_weights = self.layers[i](output, edge_mask=edge_mask, padding_mask=padding_mask)
                layer_weights.append(attention_weights)
            else:
                # (nhead * batch_size, src_length, src_length)
                output, attention_weights = self.layers[i](output, edge_mask=edge_mask[:, i, :, :, :], padding_mask=padding_mask)
                layer_weights.append(attention_weights)
        if self.norm:
            output = self.norm(output)
        output = output.permute(1, 0, 2)
        if self._output_weights:
            # (num_layers, nhead * batch_size, src_length, src_length)
            layer_weights = torch.stack(layer_weights, dim=0)
            # (nhead, batch_size, num_layers, src_length, src_length)
            layer_weights = layer_weights.permute(1, 0, 2, 3).contiguous().reshape(-1, batch_size, self.num_layers, length, length)
            # (batch_size, num_layers, nhead, src_length, src_length)
            layer_weights = layer_weights.permute(1, 2, 0, 3, 4)
            return output, layer_weights
        return output


class GNNTransformerEncoderWithMemory(nn.Module):

    def __init__(self, encoder_layer: GNNTransformerEncoderWithMemoryLayer,
                 num_layers: int, norm=None):
        super(GNNTransformerEncoderWithMemory, self).__init__()
        self.layers = _get_clones(encoder_layer, num_layers)
        self.num_layers = num_layers
        self.norm = norm

    def forward(self, memory, memory_edge_mask, memory_padding_mask, src, src_edge_mask, src_padding_mask):
        """
        :param memory:               (memory_length, batch_size, d_model)
        :param memory_edge_mask:     (batch_size, src_length, memory_length, memory_nlabels)
        :param memory_padding_mask:  (batch_size, src_length, memory_length), where True values are positions that should be masked
                                        with float('-inf') and False values will be unchanged.
        :param src:                  (src_length, batch_size,  d_model)
        :param src_edge_mask:        (batch_size, src_length, src_length, nlabels,)
        :param src_padding_mask:     (batch_size, src_length, src_length), where True values are positions that should be masked
                                        with float('-inf') and False values will be unchanged.
        :return:
            (src_length, batch_size, d_model)
        """
        # shape: (batch_size, src_length, d_model)
        output = src.permute(1, 0, 2)
        permuted_memory = memory.permute(1, 0, 2)
        for i in range(self.num_layers):
            output = self.layers[i](permuted_memory, memory_edge_mask, memory_padding_mask, output, src_edge_mask, src_padding_mask)
        if self.norm:
            output = self.norm(output)
        output = output.permute(1, 0, 2)
        return output


class GNNTransformerDecoder(nn.Module):
    r"""TransformerDecoder is a stack of N decoder layers

    Args:
        decoder_layer: an instance of the TransformerDecoderLayer() class (required).
        num_layers: the number of sub-decoder-layers in the decoder (required).
        norm: the layer normalization component (optional).
    """

    def __init__(self, decoder_layer, num_layers, norm=None):
        super(GNNTransformerDecoder, self).__init__()
        self.layers = _get_clones(decoder_layer, num_layers)
        self.num_layers = num_layers
        self.norm = norm

    def forward(self, tgt, edge_mask, memory, tgt_padding_mask=None,
                memory_mask=None,
                memory_key_padding_mask=None):
        r"""Pass the inputs (and mask) through the decoder layer in turn.
        :param memory_key_padding_mask: (batch_size, src_length)
        :param memory_mask:  (src_length, src_length)
        :param memory:       (src_length, batch_size, d_model)
        :param tgt:          (tgt_length, batch_size, d_model)
        :param edge_mask:    (batch_size, nlabels, tgt_length, tgt_length)
        :param tgt_padding_mask: (batch_size, tgt_length, tgt_length), where True values are positions that should be masked with float('-inf') and False values will be unchanged.
        :return:
            (src_length, batch_size, d_model)
        """
        output = tgt
        tgt_length, batch_size, _ = tgt.size()
        if tgt_padding_mask is None:
            _tgt_padding_mask = tgt.new_ones((batch_size, tgt_length, tgt_length))
        else:
            _tgt_padding_mask = tgt_padding_mask
        for i in range(self.num_layers):
            output = self.layers[i](output, memory=memory, tgt_padding_mask=_tgt_padding_mask,
                                    edge_mask=edge_mask, memory_mask=memory_mask,
                                    memory_key_padding_mask=memory_key_padding_mask)

        if self.norm:
            output = self.norm(output)

        return output


class TransformerDecoderLayer(nn.Module):
    r"""TransformerDecoderLayer is made up of self-attn, multi-head-attn and feedforward network.
    This standard decoder layer is based on the paper "Attention Is All You Need".
    Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N Gomez,
    Lukasz Kaiser, and Illia Polosukhin. 2017. Attention is all you need. In Advances in
    Neural Information Processing Systems, pages 6000-6010. Users may modify or implement
    in a different way during application.

    Args:
        d_model: the number of expected features in the input (required).
        nhead: the number of heads in the multiheadattention models (required).
        dim_feedforward: the dimension of the feedforward network model (default=2048).
        dropout: the dropout value (default=0.1).
    """

    def __init__(self, d_model, nhead, dim_feedforward=2048, dropout=0.1, kdim=None, vdim=None):
        super(TransformerDecoderLayer, self).__init__()
        self.self_attn = MultiheadAttention(d_model, nhead, dropout=dropout)
        self.multihead_attn = MultiheadAttention(d_model, nhead, dropout=dropout, kdim=kdim, vdim=vdim)
        # Implementation of Feedforward model
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(dim_feedforward, d_model)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.dropout3 = nn.Dropout(dropout)

    def forward(self, tgt, memory, tgt_mask=None, memory_mask=None,
                tgt_key_padding_mask=None, memory_key_padding_mask=None):
        r"""Pass the inputs (and mask) through the decoder layer.

        Args:
            tgt: the sequence to the decoder layer (required).
            memory: the sequnce from the last layer of the encoder (required).
            tgt_mask: the mask for the tgt sequence (optional).
            memory_mask: the mask for the memory sequence (optional).
            tgt_key_padding_mask: the mask for the tgt keys per batch (optional).
            memory_key_padding_mask: the mask for the memory keys per batch (optional).

        Shape:
            see the docs in Transformer class.
        """
        tgt2 = self.self_attn(tgt, tgt, tgt, attn_mask=tgt_mask,
                              key_padding_mask=tgt_key_padding_mask)[0]
        tgt = tgt + self.dropout1(tgt2)
        tgt = self.norm1(tgt)
        tgt2 = self.multihead_attn(tgt, memory, memory, attn_mask=memory_mask,
                                   key_padding_mask=memory_key_padding_mask)[0]
        tgt = tgt + self.dropout2(tgt2)
        tgt = self.norm2(tgt)
        tgt2 = self.linear2(self.dropout(F.relu(self.linear1(tgt))))
        tgt = tgt + self.dropout3(tgt2)
        tgt = self.norm3(tgt)
        return tgt
