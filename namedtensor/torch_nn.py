import torch.nn as nn
from .torch_helpers import NamedTensor

class Module(nn.Module):
    def register_parameter(self, name, tensor):
        if isinstance(tensor, NamedTensor):
            param = nn.Parameter(tensor.values)
            super(Module, self).register_parameter("_" + name + "_named", param)
            tensor._tensor = param
            setattr(self, name, tensor)
        else:
            super(Module, self).register_parameter(name, tensor)

ModuleList = nn.ModuleList


class _Update:
    def rename(self, **kwargs):
        self._updates = kwargs
        return self

    def __call__(self, input):
        updates = {} if "_updates" not in self.__dict__ else self._updates
        return input.op(super(_Update, self).forward, **updates)


class _Flat:
    def __call__(self, input):
        return input.op(super(_Flat, self).forward)


class _Loss:
    def reduce(self, dims):
        self._reduced = dims
        return self

    def __call__(self, input, target):
        assert "_reduced" in dir(self), "Must call 'reduce' first."

        return input.reduce2(
            target, super(_Loss, self).forward, self._reduced
        )

class _Augment:
    def augment(self, name):
        self._augment = name
        return self

    def forward(self, input):
        augment = (
            "embedding" if "_augment" not in self.__dict__ else self._augment
        )

        return input.augment(super(_Augment, self).forward, augment)


_wrap = ["Dropout"]


class Dropout(_Flat, nn.Dropout):
    pass


_update = [
    "Linear",
    "Conv1d",
    "Conv2d",
    "Conv3d",
    "MaxPool1d",
    "MaxPool2d",
    "MaxPool3d",
]


class Linear(_Update, nn.Linear):
    pass


class Conv1d(_Update, nn.Conv1d):
    pass


class Conv2d(_Update, nn.Conv2d):
    pass


class Conv3d(_Update, nn.Conv2d):
    pass


class MaxPool1d(_Update, nn.MaxPool1d):
    pass


class MaxPool2d(_Update, nn.MaxPool2d):
    pass


class MaxPool3d(_Update, nn.MaxPool2d):
    pass


_loss = ["CrossEntropyLoss", "NLLLoss"]


class CrossEntropyLoss(_Loss, nn.CrossEntropyLoss):
    pass


class NLLLoss(_Loss, nn.NLLLoss):
    pass


_augment = ["Embedding"]


class Embedding(_Augment, nn.Embedding):
    pass
