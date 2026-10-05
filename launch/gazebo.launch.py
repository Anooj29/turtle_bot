"""Spawn turtle_bot in Gazebo (gz-sim) with ROS 2 bridges, robot_state_publisher and RViz2."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory("turtle_bot")
    ros_gz_sim_share = get_package_share_directory("ros_gz_sim")

    xacro_path = os.path.join(pkg_share, "urdf", "turtle_bot.urdf.xacro")
    bridge_config = os.path.join(pkg_share, "config", "turtle_bot_bridge.yaml")
    rviz_config = os.path.join(pkg_share, "rviz", "urdf_view.rviz")
    default_world = os.path.join(pkg_share, "worlds", "turtle_world.world")

    world = LaunchConfiguration("world")
    use_urdf_rviz = LaunchConfiguration("use_urdf_rviz")
    x_pose = LaunchConfiguration("x_pose")
    y_pose = LaunchConfiguration("y_pose")

    robot_description = ParameterValue(
        Command(["xacro ", xacro_path]), value_type=str
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": [world, " -r"]}.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument("world", default_value=default_world,
                               description="Full path to the Gazebo world file"),
        DeclareLaunchArgument("use_urdf_rviz", default_value="true",
                               description="Launch RViz2 alongside the simulation"),
        DeclareLaunchArgument("x_pose", default_value="0.0"),
        DeclareLaunchArgument("y_pose", default_value="0.0"),

        gz_sim,

        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": robot_description, "use_sim_time": True}],
        ),

        Node(
            package="ros_gz_sim",
            executable="create",
            name="spawn_turtle_bot",
            output="screen",
            arguments=[
                "-topic", "robot_description",
                "-name", "turtle_bot",
                "-x", x_pose, "-y", y_pose, "-z", "0.05",
            ],
        ),

        Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            name="turtle_bot_bridge",
            output="screen",
            parameters=[{"config_file": bridge_config, "use_sim_time": True}],
        ),

        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", rviz_config],
            parameters=[{"use_sim_time": True}],
            condition=IfCondition(use_urdf_rviz),
        ),
    ])
