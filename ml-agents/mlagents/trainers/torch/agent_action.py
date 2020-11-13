from typing import List, Optional, NamedTuple, Dict
from mlagents.torch_utils import torch
import numpy as np

from mlagents.trainers.torch.utils import ModelUtils


class AgentAction(NamedTuple):
    """
    A NamedTuple containing the tensor for continuous actions and list of tensors for
    discrete actions. Utility functions provide numpy <=> tensor conversions to be
    sent as actions to the environment manager as well as used by the optimizers.
    :param continuous_tensor: Torch tensor corresponding to continuous actions
    :param discrete_list: List of Torch tensors each corresponding to discrete actions
    """

    continuous_tensor: torch.Tensor
    discrete_list: Optional[List[torch.Tensor]]

    @property
    def discrete_tensor(self):
        """
        Returns the discrete action list as a stacked tensor
        """
        return torch.stack(self.discrete_list, dim=-1)

    def to_numpy_dict(self) -> Dict[str, np.ndarray]:
        """
        Returns a Dict of np arrays with an entry correspinding to the continuous action
        and an entry corresponding to the discrete action. "continuous_action" and
        "discrete_action" are added to the agents buffer individually to maintain a flat buffer.
        """
        array_dict: Dict[str, np.ndarray] = {}
        if self.continuous_tensor is not None:
            array_dict["continuous_action"] = ModelUtils.to_numpy(
                self.continuous_tensor
            )
        if self.discrete_list is not None:
            array_dict["discrete_action"] = ModelUtils.to_numpy(
                self.discrete_tensor[:, 0, :]
            )
        return array_dict

    @staticmethod
    def from_dict(buff: Dict[str, np.ndarray]) -> "AgentAction":
        """
        A static method that accesses continuous and discrete action fields in an AgentBuffer
        and constructs the corresponding AgentAction from the retrieved np arrays.
        """
        continuous: torch.Tensor = None
        discrete: List[torch.Tensor] = None  # type: ignore
        if "continuous_action" in buff:
            continuous = ModelUtils.list_to_tensor(buff["continuous_action"])
        if "discrete_action" in buff:
            discrete_tensor = ModelUtils.list_to_tensor(
                buff["discrete_action"], dtype=torch.long
            )
            discrete = [
                discrete_tensor[..., i] for i in range(discrete_tensor.shape[-1])
            ]
        return AgentAction(continuous, discrete)
