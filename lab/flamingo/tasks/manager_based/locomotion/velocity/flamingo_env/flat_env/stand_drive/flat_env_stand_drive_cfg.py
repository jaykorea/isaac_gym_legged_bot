# Copyright (c) 2022-2024, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
import math
from omni.isaac.lab.managers import RewardTermCfg as RewTerm
from omni.isaac.lab.managers import SceneEntityCfg
from omni.isaac.lab.utils import configclass

# import omni.isaac.orbit_tasks.locomotion.velocity.mdp as mdp
from omni.isaac.lab.managers import CurriculumTermCfg as CurrTerm
import lab.flamingo.tasks.manager_based.locomotion.velocity.mdp as mdp
from lab.flamingo.tasks.manager_based.locomotion.velocity.velocity_env_cfg import (
    LocomotionVelocityFlatEnvCfg,
    RewardsCfg,
    CurriculumCfg,
)


# from omni.isaac.orbit_assets.flamingo import FLAMINGO_CFG
from lab.flamingo.assets.flamingo import FLAMINGO_CFG  # isort: skip


@configclass
class FlamingoCurriculumCfg(CurriculumCfg):

    curriculum_dof_torques = CurrTerm(
        func=mdp.modify_reward_weight, params={"term_name": "dof_torques_l2", "weight": -2.5e-3, "num_steps": 50000}
    )


@configclass
class FlamingoRewardsCfg(RewardsCfg):
    termination_penalty = RewTerm(func=mdp.is_terminated, weight=-200.0)
    joint_deviation_hip = RewTerm(
        func=mdp.joint_deviation_l1,
        weight=-1.0,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=[".*_hip_joint"])},
    )
    joint_deviation_range_shoulder = RewTerm(
        func=mdp.joint_target_deviation_range_l1,
        weight=0.55,
        params={
            "min_angle": -0.261799,
            "max_angle": 0.1,
            "in_range_reward": 0.0,
            "asset_cfg": SceneEntityCfg("robot", joint_names=[".*_shoulder_joint"]),
        },  # target: -0.261799
    )
    joint_deviation_range_leg = RewTerm(
        func=mdp.joint_target_deviation_range_l1,
        weight=0.55,
        params={
            "min_angle": 0.46810467,
            "max_angle": 0.66810467,
            "in_range_reward": 0.0,
            "asset_cfg": SceneEntityCfg("robot", joint_names=[".*_leg_joint"]),
        },  # target: 0.56810467
    )
    dof_pos_limits_hip = RewTerm(
        func=mdp.joint_pos_limits,
        weight=-1.0,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=".*_hip_joint")},
    )
    dof_pos_limits_shoulder = RewTerm(
        func=mdp.joint_pos_limits,
        weight=-1.0,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=".*_shoulder_joint")},
    )
    dof_pos_limits_leg = RewTerm(
        func=mdp.joint_pos_limits,
        weight=-2.0,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=".*_leg_joint")},
    )
    undesired_contacts = RewTerm(
        func=mdp.undesired_contacts,
        weight=-1.0,
        params={
            "sensor_cfg": SceneEntityCfg("contact_forces", body_names=[".*_shoulder_link", ".*_leg_link"]),
            "threshold": 1.0,
        },
    )
    joint_applied_torque_limits = RewTerm(
        func=mdp.applied_torque_limits,
        weight=-0.05,  # default: -0.1
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=".*_joint")},
    )
    # stand_origin_still = RewTerm(
    #     func=mdp.stand_origin_base,
    #     weight=-0.0,  # default: -0.1
    #     params={
    #         "command_name": "base_velocity",
    #         "asset_cfg": SceneEntityCfg("robot", body_names="base_link"),
    #     },
    # )
    shoulder_align_l1 = RewTerm(
        func=mdp.joint_align_l1,
        weight=-0.25,  # default: -0.5
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=".*_shoulder_joint")},
    )
    leg_align_l1 = RewTerm(
        func=mdp.joint_align_l1,
        weight=-0.25,  # default: -0.5
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=".*_leg_joint")},
    )
    flat_orientation_l2 = RewTerm(func=mdp.flat_orientation_l2, weight=-5.0)
    base_range_height = RewTerm(
        func=mdp.base_height_range_l2,
        weight=20.0,
        params={
            "min_height": 0.35482,
            "max_height": 0.35482,
            "in_range_reward": 0.0,
            "asset_cfg": SceneEntityCfg("robot", body_names="base_link"),
        },
    )  # default: 0.35482, 28482 works better
    # ! Terms below should be off if it is first training ! #
    # wheel_applied_torque_limits = RewTerm(
    #     func=mdp.applied_torque_limits,
    #     weight=-0.1,  # default: -0.025
    #     params={"asset_cfg": SceneEntityCfg("robot", joint_names=".*_wheel_joint")},
    # )
    # ! Terms above should be off if it is first training ! #

    # action_smoothness = RewTerm(func=mdp.action_smoothness_hard, weight=-0.0)


@configclass
class FlamingoFlatEnvCfg(LocomotionVelocityFlatEnvCfg):

    rewards: FlamingoRewardsCfg = FlamingoRewardsCfg()
    # curriculum: FlamingoCurriculumCfg = FlamingoCurriculumCfg()

    def __post_init__(self):
        # post init of parent
        super().__post_init__()
        # scene
        self.scene.robot = FLAMINGO_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.scene.height_scanner.prim_path = "{ENV_REGEX_NS}/Robot/base_link"
        self.observations.policy.enable_corruption = True

        # reset_robot_joint_zero should be called here
        self.events.reset_robot_joints.params["position_range"] = (-0.1, 0.1)
        # self.events.push_robot = True
        self.events.push_robot.interval_range_s = (15.0, 17.0)
        self.events.push_robot.params = {
            "velocity_range": {"x": (-1.0, 1.0), "y": (-1.0, 1.0)},
        }
        # add base mass should be called here
        self.events.add_base_mass.params["asset_cfg"].body_names = ["base_link"]
        self.events.add_base_mass.params["mass_distribution_params"] = (-1.5, 2.5)
        # physics material should be called here
        self.events.physics_material.params["asset_cfg"].body_names = [".*_link"]
        self.events.physics_material.params["static_friction_range"] = (0.3, 1.0)
        self.events.physics_material.params["dynamic_friction_range"] = (0.3, 0.8)
        self.events.base_external_force_torque.params["asset_cfg"].body_names = ["base_link"]
        self.events.reset_base.params = {
            "pose_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5), "yaw": (-3.14, 3.14)},
            "velocity_range": {
                "x": (0.0, 0.0),
                "y": (0.0, 0.0),
                "z": (0.0, 0.0),
                "roll": (-0.25, 0.25),
                "pitch": (-0.25, 0.25),
                "yaw": (-0.0, 0.0),
            },
        }
        # rewards
        self.rewards.dof_torques_l2.weight = -5.0e-4  # default: -5.0e-6
        self.rewards.track_lin_vel_xy_exp.weight = 1.5
        self.rewards.track_ang_vel_z_exp.weight = 0.75
        self.rewards.lin_vel_z_l2.weight *= 1.0
        self.rewards.ang_vel_xy_l2.weight *= 1.0
        self.rewards.action_rate_l2.weight *= 1.0  # default: 1.5
        self.rewards.dof_acc_l2.weight *= 1.0  # default: 1.5

        # change terrain to flat
        self.scene.terrain.terrain_type = "plane"
        self.scene.terrain.terrain_generator = None

        # Terrain curriculum
        self.curriculum.terrain_levels = None

        # height scan
        self.scene.height_scanner.prim_path = "{ENV_REGEX_NS}/Robot/base_link"
        self.scene.height_scanner.debug_vis = False

        # commands
        self.commands.base_velocity.ranges.lin_vel_x = (-1.0, 1.0)
        self.commands.base_velocity.ranges.lin_vel_y = (0.0, 0.0)
        self.commands.base_velocity.ranges.ang_vel_z = (-1.5, 1.5)
        # self.commands.base_velocity.ranges.heading = (-math.pi, math.pi)
        self.commands.base_velocity.ranges.pos_z = (0.0, 0.0)

        # terminations
        self.terminations.base_contact.params["sensor_cfg"].body_names = [
            "base_link",
            ".*_hip_link",
            ".*_shoulder_link",
            ".*_leg_link",
        ]
