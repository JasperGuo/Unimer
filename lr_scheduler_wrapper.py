# coding=utf8


from typing import Dict, Any
from overrides import overrides
from torch.optim.lr_scheduler import MultiStepLR
from allennlp.training.learning_rate_schedulers import LearningRateScheduler


class PyTorchMultiStepLearningRateSchedulerWrapper(LearningRateScheduler):

    def __init__(self, lr_scheduler: MultiStepLR) -> None:
        self.lr_scheduler = lr_scheduler

    def get_values(self):
        return self.lr_scheduler.get_lr()

    @overrides
    def step(self, metric: float = None, epoch: int = None) -> None:
        self.lr_scheduler.step(epoch)

    @overrides
    def state_dict(self) -> Dict[str, Any]:
        return self.lr_scheduler.state_dict()

    @overrides
    def load_state_dict(self, state_dict: Dict[str, Any]) -> None:
        self.lr_scheduler.load_state_dict(state_dict)
