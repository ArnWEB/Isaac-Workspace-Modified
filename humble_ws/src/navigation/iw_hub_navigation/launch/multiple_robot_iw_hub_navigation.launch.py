# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription, LogInfo
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, TextSubstitution


def generate_launch_description():
    # Get the launch and rviz directories
    iw_hub_nav_dir = get_package_share_directory("iw_hub_navigation")
    nav2_bringup_launch_dir = os.path.join(get_package_share_directory("nav2_bringup"), "launch")

    rviz_config_dir = os.path.join(iw_hub_nav_dir, "rviz2", "iw_hub_navigation.rviz")
    map_dir = os.path.join(iw_hub_nav_dir, "maps", "iw_hub_warehouse_navigation.yaml")

    # Names and poses of the robots
    robots = [
        {"name": "amr1", "x_pose": 0.23, "y_pose": 4.0},
        {"name": "amr2", "x_pose": 5.0, "y_pose": 4.0},
        {"name": "amr3", "x_pose": 10.0, "y_pose": 4.0},
    ]

    # Common settings
    use_sim_time = LaunchConfiguration("use_sim_time", default="True")
    use_rviz = LaunchConfiguration("use_rviz", default="True")
    log_settings = LaunchConfiguration("log_settings", default="True")

    # Declare the launch arguments
    declare_map_yaml_cmd = DeclareLaunchArgument(
        "map",
        default_value=map_dir,
        description="Full path to map file to load",
    )

    declare_amr1_params_file_cmd = DeclareLaunchArgument(
        "amr1_params_file",
        default_value=os.path.join(iw_hub_nav_dir, "params", "iw_hub_navigation_params_amr1.yaml"),
        description="Full path to the ROS2 parameters file to use for amr1 launched nodes",
    )

    declare_amr2_params_file_cmd = DeclareLaunchArgument(
        "amr2_params_file",
        default_value=os.path.join(iw_hub_nav_dir, "params", "iw_hub_navigation_params_amr2.yaml"),
        description="Full path to the ROS2 parameters file to use for amr2 launched nodes",
    )

    declare_amr3_params_file_cmd = DeclareLaunchArgument(
        "amr3_params_file",
        default_value=os.path.join(iw_hub_nav_dir, "params", "iw_hub_navigation_params_amr3.yaml"),
        description="Full path to the ROS2 parameters file to use for amr3 launched nodes",
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        "use_sim_time", 
        default_value="true", 
        description="Use simulation (Omniverse Isaac Sim) clock if true"
    )

    declare_use_rviz_cmd = DeclareLaunchArgument(
        "use_rviz", 
        default_value="true", 
        description="Whether to start RVIZ"
    )

    declare_log_settings_cmd = DeclareLaunchArgument(
        "log_settings", 
        default_value="true", 
        description="Whether to log robot launch settings"
    )

    # Define commands for launching the navigation instances
    nav_instances_cmds = []
    for robot in robots:
        params_file = LaunchConfiguration(robot["name"] + "_params_file")

        group = GroupAction(
            [
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(os.path.join(nav2_bringup_launch_dir, "rviz_launch.py")),
                    condition=IfCondition(use_rviz),
                    launch_arguments={
                        "namespace": TextSubstitution(text=robot["name"]),
                        "use_namespace": "True",
                        "rviz_config": rviz_config_dir,
                    }.items(),
                ),
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        os.path.join(iw_hub_nav_dir, "launch", "iw_hub_navigation.launch.py")
                    ),
                    launch_arguments={
                        "namespace": robot["name"],
                        "map": LaunchConfiguration("map"),
                        "use_sim_time": use_sim_time,
                        "params_file": params_file,
                        "use_rviz": "False",
                    }.items(),
                ),
                LogInfo(
                    condition=IfCondition(log_settings), 
                    msg=["Launching ", robot["name"], " with initial pose (", str(robot["x_pose"]), ", ", str(robot["y_pose"]), ")"]
                ),
                LogInfo(
                    condition=IfCondition(log_settings), 
                    msg=["AMR1 params: ", LaunchConfiguration("amr1_params_file")]
                ),
                LogInfo(
                    condition=IfCondition(log_settings), 
                    msg=["AMR2 params: ", LaunchConfiguration("amr2_params_file")]
                ),
                LogInfo(
                    condition=IfCondition(log_settings), 
                    msg=["AMR3 params: ", LaunchConfiguration("amr3_params_file")]
                ),
            ]
        )

        nav_instances_cmds.append(group)

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare the launch options
    ld.add_action(declare_map_yaml_cmd)
    ld.add_action(declare_amr1_params_file_cmd)
    ld.add_action(declare_amr2_params_file_cmd)
    ld.add_action(declare_amr3_params_file_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(declare_log_settings_cmd)

    # Add all robot instances
    for nav_instance_cmd in nav_instances_cmds:
        ld.add_action(nav_instance_cmd)

    return ld
