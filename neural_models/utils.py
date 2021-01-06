# coding=utf8

import numpy
import torch
from typing import List


def has_nan(x: torch.Tensor) -> bool:
    return torch.isnan(x).any()


def matrix_cosine_similarity(x: torch.Tensor, y: torch.Tensor, eps: float=1e-8):
    """
    :param x (batch_size, length_1, dim)
    :param y (batch_size, length_2, dim)
    :return 
        (batch_size, length_1, length_2)
    """
    length_1, length_2 = x.size(1), y.size(1)
    # shape: (batch_size, length_1, length_2)
    dot_product = x.bmm(y.permute(0, 2, 1))
    # shape: (batch_size, length_1), (batch_size, length_2)
    x_norm, y_norm = x.norm(dim=-1, p=None), y.norm(dim=-1, p=None)
    # added eps for numerical stability
    x_norm = torch.max(x_norm, eps * x_norm.new_ones(x_norm.size()))
    y_norm = torch.max(y_norm, eps * y_norm.new_ones(y_norm.size()))

    expanded_x_norm = x_norm.unsqueeze(-1).repeat(1, 1, length_2)
    expanded_y_norm = y_norm.unsqueeze(1).repeat(1, length_1, 1)
    # shape: (batch_size, length_1, length_2)
    norm = expanded_x_norm * expanded_y_norm
    similarity = dot_product / norm
    return similarity


def get_one_hot_mask(num_classes: int, ids: List):
    targets = numpy.array(ids, dtype=int)
    one_hot = numpy.eye(num_classes)[targets]
    return torch.from_numpy(one_hot.sum(0))