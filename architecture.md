# Robot Voice AI Architecture

This document turns the imported ChatGPT design discussion into a working architecture reference for the project.

## Goal

Build a ROS 2 system for a Hiwonder MentorPi robot that can:

- map and localize in a new environment
- tag rooms by voice while the robot is being guided
- navigate to named rooms using semantic understanding instead of raw coordinates
- search for objects in rooms using planning, navigation, and perception

## Core Idea

The system bridges three worlds that normally stay separate:

- robot navigation and localization
- human language and room names
- task-level reasoning for search and navigation

Instead of storing a room as a single point, the semantic layer stores polygons with centroids and entry points. That makes room-aware navigation and room coverage much more practical.

## Deployment Split

### Raspberry Pi 5 on robot

- base control and hardware drivers
- SLAM
- Nav2
- localization and low-latency robot interfaces

### Dev laptop VM

- speech-to-text and text-to-speech
- task planning and agentic reasoning
- semantic map services
- object detection and object search coordination

Both machines should share the same ROS 2 domain and DDS configuration.

## System Layers

### 1. Robot core

- `robot_bringup`
- `slam_mapping`
- `navigation_stack`

Responsibilities:

- publish `/map` and `/tf`
- localize the robot
- execute Nav2 goals
- avoid obstacles and follow paths

### 2. Voice interface

- `speech_to_text_node`
- `voice_command_router_node`
- `text_to_speech_node`

Responsibilities:

- convert microphone input into text
- classify high-level intent like navigate, tag room, or search object
- provide spoken status back to the user

### 3. Semantic layer

- `semantic_map_node`
- polygon utilities and storage

Responsibilities:

- store named rooms as polygons
- answer semantic queries such as "where is the kitchen?"
- store object sightings and last known locations
- translate between human concepts and map coordinates

### 4. Task planning and execution

- `task_planner_node`
- `navigation_executor_node`
- `object_search_node`

Responsibilities:

- turn user intent into structured task plans
- choose room centroids, entry points, or search waypoints
- invoke Nav2 goals and track completion
- search candidate rooms until the target object is found

### 5. Perception

- `object_detection_node`

Responsibilities:

- detect named objects from camera input
- publish detections and update semantic memory
- help confirm whether the searched object is present in a room

## Recommended Nodes

### `exploration_manager_node`

Purpose:

- supports guided exploration and room annotation

Inputs:

- teleop or guided movement
- current pose from localization
- room-tagging voice command

Outputs:

- room polygon annotations
- updates to semantic map storage

### `semantic_map_node`

Purpose:

- central authority for room and object meaning

Stores:

- room name
- polygon vertices
- centroid
- entry points
- object memory

Suggested room structure:

```json
{
  "name": "kitchen",
  "polygon": [[x1, y1], [x2, y2], [x3, y3]],
  "centroid": [cx, cy],
  "entry_points": [[ex1, ey1], [ex2, ey2]]
}
```

### `task_planner_node`

Purpose:

- convert parsed voice commands into execution plans

Example plans:

```json
{
  "type": "navigate",
  "goal": "kitchen"
}
```

```json
{
  "type": "search_object",
  "object": "backpack",
  "locations": ["office", "living_room"]
}
```

### `navigation_executor_node`

Purpose:

- translate semantic goals into concrete Nav2 action requests

Behavior:

- ask semantic map for a destination inside or near a room
- pick centroid, entry point, or nearest reachable interior point
- send goal to Nav2
- monitor completion and failure states

### `object_search_node`

Purpose:

- manage room-by-room object search

Behavior:

- pick candidate rooms from semantic memory
- generate search waypoints inside the room polygon
- coordinate navigation and object detection
- stop early when the object is found

### `object_detection_node`

Purpose:

- detect user-requested objects from robot perception

Output example:

```json
{
  "label": "backpack",
  "pose": [x, y]
}
```

## Node Graph

```text
speech_to_text_node
  -> /voice_text
voice_command_router_node
  -> /high_level_command
task_planner_node
  -> /task_plan
  <-> semantic_map_node
navigation_executor_node
  -> /navigate_to_pose (Nav2 action)
object_search_node
  <-> semantic_map_node
  <-> object_detection_node
exploration_manager_node
  -> semantic_map_node
```

## Key Flows

### Mapping and room tagging

```text
User drives robot
-> user says "This is the kitchen"
-> speech_to_text_node
-> voice_command_router_node
-> exploration_manager_node
-> semantic_map_node stores polygon and metadata
```

### Navigate to a room

```text
"Go to the kitchen"
-> speech_to_text_node
-> voice_command_router_node
-> task_planner_node
-> semantic_map_node resolves room target
-> navigation_executor_node
-> Nav2
```

### Search for an object

```text
"Find my backpack in my office"
-> speech_to_text_node
-> voice_command_router_node
-> task_planner_node
-> object_search_node
-> semantic_map_node returns candidate rooms and search region
-> navigation_executor_node + object_detection_node
-> semantic_map_node updates object memory
```

## Polygon-Based Behaviors

Why polygons matter:

- a centroid is better than a random saved point for room entry
- entry points help route the robot to an accessible approach
- containment checks let the system say which room the robot or object is in
- polygon coverage patterns make search behavior systematic

Useful operations:

- point-in-polygon for room membership
- centroid calculation for default navigation target
- nearest reachable point inside polygon
- sweep or spiral waypoint generation for room search

## ROS 2 Package Layout

```text
mentorpi_ws/
└── src/
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

Suggested responsibilities:

- `robot_bringup`: drivers, launch, hardware config
- `navigation_stack`: Nav2 config and planner tuning
- `slam_mapping`: SLAM toolbox config and mapping launch
- `semantic_map_pkg`: polygon storage, services, room/object queries
- `exploration_pkg`: tagging and polygon creation tools
- `voice_interface_pkg`: STT, TTS, and intent routing
- `task_planning_pkg`: planner, tools, and reasoning interfaces
- `navigation_executor_pkg`: Nav2 action client and status handling
- `perception_pkg`: object detection and tracking

## Suggested MVP

1. Build mapping plus manual room tagging.
2. Store rooms as polygons in the semantic layer.
3. Support "go to the kitchen" with semantic lookup plus Nav2.
4. Add object detections and last-seen object memory.
5. Add room coverage search for commands like "find my backpack."

## Open Design Choices

- whether voice and planning should stay fully local or use cloud services
- whether semantic storage starts as JSON or SQLite
- how room polygons are drawn: RViz clicks, guided path capture, or both
- whether object search is waypoint-based only or mixed with active perception
