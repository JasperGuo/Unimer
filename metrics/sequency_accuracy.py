# coding=utf8

import torch
from overrides import overrides
from allennlp.training.metrics import Metric
from typing import Union, Tuple, Dict, List, Optional


class SequenceAccuracy(Metric):

    def __init__(self) -> None:
        self._correct_counts = 0.
        self._total_counts = 0.
        self._pad_index = -1

    def __call__(self, predictions: torch.Tensor, gold_labels: torch.Tensor, mask: torch.Tensor) -> None:

        batch_size, p_len = predictions.size()
        batch_size, g_len = gold_labels.size()

        if p_len >= g_len:
            _predictions = predictions[:, :g_len]
        else:
            _predictions = torch.cat((predictions, predictions.new_ones(batch_size, g_len - p_len) * self._pad_index),
                                     dim=-1)
        assert _predictions.size(1) == g_len
        masked_predictions = _predictions * mask
        masked_gold_labels = gold_labels * mask
        eqs = masked_gold_labels.eq(masked_predictions).int()
        result = (eqs.sum(-1) == g_len).int()

        self._correct_counts += result.sum()
        self._total_counts += batch_size

    @overrides
    def get_metric(self, reset: bool) -> Union[float, Tuple[float, ...], Dict[str, float], Dict[str, List[float]]]:
        """
        Returns
        -------
        The accumulated accuracy.
        """
        if self._total_counts > 0:
            accuracy = float(self._correct_counts) / float(self._total_counts)
        else:
            accuracy = 0

        if reset:
            self.reset()
        return {'accuracy': accuracy}

    @overrides
    def reset(self) -> None:
        self._correct_counts = 0.
        self._total_counts = 0.
