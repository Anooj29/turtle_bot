# turtle_bot

A complete ROS 2 (Jazzy) differential-drive mobile robot stack:

- **URDF/Xacro** robot description (chassis, 2 drive wheels, caster, LiDAR, IMU, camera)
- **Gazebo (gz-sim / Harmonic)** simulation with a custom world
- **RViz2** visualization
- **SLAM** mapping with `slam_toolbox`
- **Autonomous navigation** with **Nav2** (planner, controller, costmaps, behaviors)

Built for ROS 2 Jazzy on this machine, which uses the new Gazebo (`gz-sim`, via `ros_gz`)
rather than classic Gazebo.

## 1. Install dependencies (one-time, needs sudo — run this yourself)

Nav2 and slam_toolbox are not part of a base ROS 2 install and were **not** installed by
this session because it has no sudo access. Run:

```bash
cd ~/ROS2/turtle_bot
./scripts/install_dependencies.sh
```

This installs: `robot_state_publisher`, `joint_state_publisher(-gui)`, `xacro`, `rviz2`,
`ros-gz` / `ros-gz-sim` / `ros-gz-bridge` / `ros-gz-interfaces`, `navigation2`,
`nav2-bringup`, `slam-toolbox`, `teleop-twist-keyboard`.

## 2. Build the workspace

This repo is a single ROS 2 package. Put it in (or symlink it into) a colcon workspace's
`src/` folder, e.g.:

```bash
mkdir -p ~/ROS2/ros2_ws/src
ln -s ~/ROS2/turtle_bot ~/ROS2/ros2_ws/src/turtle_bot   # skip if it's already there
cd ~/ROS2/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

Add `source ~/ROS2/ros2_ws/install/setup.bash` to your `~/.bashrc` if you want this
available in every new terminal.

## 3. Check the robot model (no simulation)

```bash
ros2 launch turtle_bot display.launch.py
```

Opens RViz2 with the robot model, TF frames, and a joint_state_publisher_gui slider panel
to spin the wheels manually and sanity-check the URDF.

## 4. Simulate in Gazebo + RViz2

```bash
ros2 launch turtle_bot gazebo.launch.py
```

Spawns `turtle_bot` in the custom `turtle_world` (a bounded arena with boxes/cylinders as
mapping landmarks), bridges `/cmd_vel`, `/odom`, `/tf`, `/scan`, `/imu`, `/camera/*` and
`/joint_states` between Gazebo and ROS 2, and opens RViz2.

Drive it manually:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## 5. Build a map with SLAM

One command does simulation + slam_toolbox + Nav2 + RViz2 (Nav2's RViz panel gives you
the "2D Pose Estimate" / "Nav2 Goal" tools and shows the live occupancy grid):

```bash
ros2 launch turtle_bot bringup.launch.py
```

Drive the robot around the whole arena (teleop or Nav2 goals) until the map in RViz looks
complete, then save it:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/ROS2/turtle_bot/maps/turtle_world
```

This writes `maps/turtle_world.yaml` + `maps/turtle_world.pgm`, which is the default map
path `bringup.launch.py` expects in step 6.

## 6. Navigate autonomously on the saved map

```bash
ros2 launch turtle_bot bringup.launch.py slam:=false map:=~/ROS2/turtle_bot/maps/turtle_world.yaml
```

In RViz2: set **2D Pose Estimate** to tell AMCL where the robot starts, then use
**Nav2 Goal** to send it anywhere on the map — it will plan around obstacles and drive
there on its own.

## Package layout

```
urdf/           robot description (xacro) + Gazebo sensor/plugin definitions
worlds/         Gazebo world (turtle_world.world)
launch/
  display.launch.py      RViz-only URDF check
  gazebo.launch.py       sim + bridge + robot_state_publisher + RViz
  slam.launch.py         slam_toolbox (mapping)
  localization.launch.py map_server + AMCL (on a saved map)
  navigation.launch.py   Nav2 planner/controller/behavior/bt_navigator stack
  bringup.launch.py      top-level: everything together
config/         ros_gz_bridge topic map, nav2_params.yaml, slam_toolbox_params.yaml
rviz/           RViz2 config for the URDF-only view
maps/           saved occupancy-grid maps land here
scripts/        install_dependencies.sh
```

## Troubleshooting

This environment could not install Nav2/slam_toolbox or launch a graphical Gazebo/RViz
session to test-run the stack end-to-end (no sudo, no display). The package was written
against the well-documented Jazzy + gz-sim (Harmonic) + Nav2 + slam_toolbox integration
pattern, and `colcon build` / `xacro` parsing were verified. The one place that
sometimes needs a tweak on a fresh machine is **topic scoping between gz-sim and the ROS
bridge** (`config/turtle_bot_bridge.yaml`) — if `/odom`, `/tf`, or `/joint_states` don't
show up after `gazebo.launch.py`:

1. List real Gazebo topics while the sim is running: `gz topic -l`
2. Compare against the `gz_topic_name` values in `config/turtle_bot_bridge.yaml`
3. Fix any mismatched path (Gazebo scopes topics under `/model/<name>/...` or
   `/world/<world>/model/<name>/...` — the exact prefix can vary slightly by Gazebo
   point release) and re-run.

`/scan`, `/imu`, and `/camera/*` are set to fixed absolute topics directly in
`urdf/turtle_bot.gazebo.xacro` (`<topic>scan</topic>` etc.), so those should bridge
as-is.
