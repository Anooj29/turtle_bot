#!/usr/bin/env bash
# One-time setup: installs the ROS 2 packages turtle_bot depends on
# (Nav2 and slam_toolbox are not part of a base ROS 2 install).
# Run this once, then build the workspace. Requires sudo.
set -euo pipefail

ROS_DISTRO="${ROS_DISTRO:-jazzy}"

echo "Installing ROS 2 ($ROS_DISTRO) dependencies for turtle_bot..."
sudo apt-get update
sudo apt-get install -y \
  "ros-${ROS_DISTRO}-robot-state-publisher" \
  "ros-${ROS_DISTRO}-joint-state-publisher" \
  "ros-${ROS_DISTRO}-joint-state-publisher-gui" \
  "ros-${ROS_DISTRO}-xacro" \
  "ros-${ROS_DISTRO}-rviz2" \
  "ros-${ROS_DISTRO}-ros-gz" \
  "ros-${ROS_DISTRO}-ros-gz-sim" \
  "ros-${ROS_DISTRO}-ros-gz-bridge" \
  "ros-${ROS_DISTRO}-ros-gz-interfaces" \
  "ros-${ROS_DISTRO}-navigation2" \
  "ros-${ROS_DISTRO}-nav2-bringup" \
  "ros-${ROS_DISTRO}-slam-toolbox" \
  "ros-${ROS_DISTRO}-teleop-twist-keyboard" \
  python3-colcon-common-extensions

echo "Done. Next: build the workspace with 'colcon build --symlink-install'."
