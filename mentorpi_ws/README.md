# MentorPi ROS 2 Workspace

This workspace scaffolds the architecture described in [../architecture.md](/home/jatroche/robot-voice-ai/architecture.md).

## Layout

```text
mentorpi_ws/
└── src/
    ├── robot_voice_ai_interfaces/
    ├── robot_bringup/
    ├── navigation_stack/
    ├── slam_mapping/
    ├── semantic_map_pkg/
    ├── exploration_pkg/
    ├── voice_interface_pkg/
    ├── task_planning_pkg/
    ├── navigation_executor_pkg/
    └── perception_pkg/
```

## What This Scaffold Includes

- `ament_python` package skeletons
- a shared ROS 2 interfaces package for rooms and object memory
- starter nodes for the main architecture components
- placeholder launch and config files
- a real Nav2 action-client scaffold in the navigation executor

## What It Does Not Include Yet

- real hardware drivers
- real Nav2 and SLAM integration
- custom ROS messages and services
- production-ready speech, object detection, or agent tooling

## Build

From the repo root:

```bash
cd mentorpi_ws
colcon build
source install/setup.bash
```

## Suggested Next Steps

1. Wire `robot_bringup` to actual MentorPi drivers and launch files.
2. Finish connecting `navigation_executor_pkg` to a live Nav2 stack and AMCL.
3. Back `semantic_map_pkg` with SQLite or a more durable store.
4. Add RViz tools for polygon creation and inspection.
5. Replace placeholder speech and perception backends with production integrations.
