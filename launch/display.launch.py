"""Visualize the turtle_bot URDF in RViz2 (no simulation)."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory("turtle_bot")
    xacro_path = os.path.join(pkg_share, "urdf", "turtle_bot.urdf.xacro")
    rviz_config = os.path.join(pkg_share, "rviz", "urdf_view.rviz")

    use_gui = LaunchConfiguration("use_gui")

    robot_description = ParameterValue(
        Command(["xacro ", xacro_path]), value_type=str
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "use_gui", default_value="true",
            description="Launch joint_state_publisher_gui to move the wheel joints manually",
        ),

        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": robot_description, "use_sim_time": False}],
        ),

        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            name="joint_state_publisher_gui",
            condition=IfCondition(use_gui),
        ),

        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", rviz_config],
        ),
    ])
