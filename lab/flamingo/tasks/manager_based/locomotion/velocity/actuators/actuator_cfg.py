from dataclasses import MISSING
from typing import Literal, Iterable

from omni.isaac.lab.utils import configclass
from omni.isaac.lab.actuators.actuator_cfg import (
    ActuatorNetLSTMCfg as BaseActuatorNetLSTMCfg,
    ActuatorNetMLPCfg as BaseActuatorNetMLPCfg,
)
from .actuator_net import ActuatorNetLSTM, ActuatorNetMLP


@configclass
class ActuatorNetLSTMCfg(BaseActuatorNetLSTMCfg):
    """Configuration for LSTM-based actuator model."""

    class_type: type = ActuatorNetLSTM
    # we don't use stiffness and damping for actuator net
    stiffness = None
    damping = None

    input_order: Literal["pos_vel", "vel_pos"] = MISSING
    """Order of the inputs to the network."""

    network_file: str = MISSING
    """Path to the file containing network weights."""


@configclass
class ActuatorNetMLPCfg(BaseActuatorNetMLPCfg):
    """Configuration for MLP-based actuator model."""

    class_type: type = ActuatorNetMLP
    # we don't use stiffness and damping for actuator net
    stiffness = None
    damping = None

    network_file: str = MISSING
    """Path to the file containing network weights."""

    pos_scale: float = MISSING
    """Scaling of the joint position errors input to the network."""
    vel_scale: float = MISSING
    """Scaling of the joint velocities input to the network."""
    torque_scale: float = MISSING
    """Scaling of the joint efforts output from the network."""

    input_order: Literal["pos_vel", "vel_pos"] = MISSING
    """Order of the inputs to the network."""

    input_idx: Iterable[int] = MISSING
    """Indices of the actuator history buffer passed as inputs to the network."""
