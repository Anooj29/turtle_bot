"""Start slam_toolbox (online async) to build a map while driving/exploring."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("turtle_bot")
    default_params = os.path.join(pkg_share, "config", "slam_toolbox_params.yaml")

    params_file = LaunchConfiguration("params_file")
    use_sim_time = LaunchConfiguration("use_sim_time")

    return LaunchDescription([
        DeclareLaunchArgument("params_file", default_value=default_params,
                               description="slam_toolbox parameters file"),
        DeclareLaunchArgument("use_sim_time", default_value="true"),

        Node(
            package="slam_toolbox",
            executable="async_slam_toolbox_node",
            name="slam_toolbox",
            output="screen",
            parameters=[params_file, {"use_sim_time": use_sim_time}],
        ),

        # async_slam_toolbox_node is a managed lifecycle node and stays "unconfigured"
        # until something drives it through configure -> activate. nav2's own
        # lifecycle_manager_navigation (started by navigation.launch.py) only manages
        # Nav2's own servers, so slam_toolbox needs its own small lifecycle manager here.
        Node(
            package="nav2_lifecycle_manager",
            executable="lifecycle_manager",
            name="lifecycle_manager_slam",
            output="screen",
            parameters=[{
                "use_sim_time": use_sim_time,
                "autostart": True,
                "node_names": ["slam_toolbox"],
                "bond_timeout": 0.0,
            }],
        ),
    ])
