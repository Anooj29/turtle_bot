"""Top-level entry point: Gazebo simulation + (SLAM mapping OR AMCL localization) + Nav2 + RViz2.

Examples
--------
Build a map while driving around (SLAM mode, default):
    ros2 launch turtle_bot bringup.launch.py

Navigate autonomously using a previously saved map:
    ros2 launch turtle_bot bringup.launch.py slam:=false map:=/path/to/map.yaml
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_share = get_package_share_directory("turtle_bot")
    nav2_bringup_share = get_package_share_directory("nav2_bringup")

    default_world = os.path.join(pkg_share, "worlds", "turtle_world.world")
    default_nav2_params = os.path.join(pkg_share, "config", "nav2_params.yaml")
    default_map = os.path.join(pkg_share, "maps", "turtle_world.yaml")
    nav2_rviz_config = os.path.join(nav2_bringup_share, "rviz", "nav2_default_view.rviz")

    world = LaunchConfiguration("world")
    slam = LaunchConfiguration("slam")
    map_yaml = LaunchConfiguration("map")
    nav2_params = LaunchConfiguration("nav2_params")
    use_rviz = LaunchConfiguration("use_rviz")
    x_pose = LaunchConfiguration("x_pose")
    y_pose = LaunchConfiguration("y_pose")
    use_sim_time = LaunchConfiguration("use_sim_time")

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, "launch", "gazebo.launch.py")
        ),
        launch_arguments={
            "world": world,
            "use_urdf_rviz": "false",
            "x_pose": x_pose,
            "y_pose": y_pose,
        }.items(),
    )

    slam_mapping = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, "launch", "slam.launch.py")
        ),
        launch_arguments={"use_sim_time": use_sim_time}.items(),
        condition=IfCondition(slam),
    )

    amcl_localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, "launch", "localization.launch.py")
        ),
        launch_arguments={
            "map": map_yaml,
            "params_file": nav2_params,
            "use_sim_time": use_sim_time,
        }.items(),
        condition=UnlessCondition(slam),
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, "launch", "navigation.launch.py")
        ),
        launch_arguments={
            "params_file": nav2_params,
            "use_sim_time": use_sim_time,
        }.items(),
    )

    nav2_rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_share, "launch", "rviz_launch.py")
        ),
        launch_arguments={"rviz_config": nav2_rviz_config}.items(),
        condition=IfCondition(use_rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument("world", default_value=default_world,
                               description="Full path to the Gazebo world file"),
        DeclareLaunchArgument("slam", default_value="true",
                               description="true = build a new map with slam_toolbox; "
                                           "false = localize with AMCL on an existing map"),
        DeclareLaunchArgument("map", default_value=default_map,
                               description="Map yaml to use when slam:=false"),
        DeclareLaunchArgument("nav2_params", default_value=default_nav2_params,
                               description="Nav2 parameters file"),
        DeclareLaunchArgument("use_rviz", default_value="true"),
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument("x_pose", default_value="0.0"),
        DeclareLaunchArgument("y_pose", default_value="0.0"),

        gazebo,
        slam_mapping,
        amcl_localization,
        navigation,
        nav2_rviz,
    ])
