import torch
import torch.nn as nn
from .utils import ACT_FN

class BartClassificationHead(nn.Module):
    def __init__(
        self,
        input_dim: int,
        inner_dim: int,
        num_classes: int,
        dropout: float,
        act_fn: str=None,
    ):
        super().__init__()
        self.act_fn = act_fn
        self.dense = nn.Linear(
            in_features=input_dim,
            out_features=inner_dim,
        )
        self.dropout = dropout
        self.out = nn.Linear(
            in_features=inner_dim,
            out_features=num_classes,
        )

    def forward(
        self,
        hidden_states: torch.Tensor
    ):
        hidden_states = nn.functional.dropout(
            input=hidden_states,
            p=self.dropout,
            training=self.training,
        )
        hidden_states = self.dense(hidden_states)
        if self.act_fn is not None:
            hidden_states = ACT_FN[self.act_fn](hidden_states)
        hidden_states = nn.functional.dropout(
            input=hidden_states,
            p=self.dropout,
            training=self.training,
        )
        hidden_states = self.out(hidden_states)
        return hidden_states
    
__all__ = [
    "BartClassificationHead",
]