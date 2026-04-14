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

## Smoke Test Launch

```bash
cd mentorpi_ws
source install/setup.bash
ros2 launch robot_bringup smoke_test.launch.py
```

This launch starts the semantic map, voice router, task planner, navigation executor,
exploration manager, and object search nodes together.

## Speech-To-Text Usage

Run the local Whisper STT node:

```bash
cd mentorpi_ws
source install/setup.bash
ros2 run voice_interface_pkg speech_to_text_node
```

Run with a different Whisper model:

```bash
ros2 run voice_interface_pkg speech_to_text_node --ros-args -p model_name:=small
```

List available audio devices at startup:

```bash
ros2 run voice_interface_pkg speech_to_text_node --ros-args -p list_audio_devices:=true
```

Use a specific input device:

```bash
ros2 run voice_interface_pkg speech_to_text_node --ros-args -p audio_device:=\"USB Audio Device\"
```

Transcribe a local audio file on startup:

```bash
ros2 run voice_interface_pkg speech_to_text_node --ros-args -p auto_listen:=false -p audio_file:=/tmp/sample.wav
```

Run in push-to-talk mode:

```bash
ros2 run voice_interface_pkg speech_to_text_node --ros-args -p push_to_talk:=true
```

Start microphone capture:

```bash
ros2 topic pub --once /speech_to_text/control std_msgs/msg/String '{data: start}'
```

Stop microphone capture:

```bash
ros2 topic pub --once /speech_to_text/control std_msgs/msg/String '{data: stop}'
```

Toggle microphone capture:

```bash
ros2 topic pub --once /speech_to_text/control std_msgs/msg/String '{data: toggle}'
```

Transcribe a file through the control topic:

```bash
ros2 topic pub --once /speech_to_text/control std_msgs/msg/String '{data: "file:/tmp/sample.wav"}'
```

The node publishes recognized text to `/voice_text`.

## Speech-To-Text Troubleshooting

If `speech_to_text_node` fails with an error like:

```text
AttributeError: module 'coverage' has no attribute 'types'
```

that usually means `numba` and `coverage` are mismatched in the Python environment used by Whisper.

Quick fix:

```bash
python3 -m pip install --user --upgrade "coverage>=7"
```

Then verify:

```bash
python3 - <<'PY'
import coverage, numba, whisper
print("coverage", coverage.__version__)
print("numba", numba.__version__)
print("whisper", whisper.__version__)
PY
```

Then retry:

```bash
cd mentorpi_ws
source install/setup.bash
ros2 run voice_interface_pkg speech_to_text_node --ros-args -p list_audio_devices:=true
```

If your system Python has a lot of mixed packages, a virtual environment is safer:

```bash
python3 -m venv ~/.venvs/robot-voice-ai
source ~/.venvs/robot-voice-ai/bin/activate
pip install --upgrade pip
pip install "coverage>=7" numpy sounddevice openai-whisper
```

## Suggested Next Steps

1. Wire `robot_bringup` to actual MentorPi drivers and launch files.
2. Finish connecting `navigation_executor_pkg` to a live Nav2 stack and AMCL.
3. Back `semantic_map_pkg` with SQLite or a more durable store.
4. Add RViz tools for polygon creation and inspection.
5. Replace placeholder speech and perception backends with production integrations.
