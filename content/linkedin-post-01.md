# LinkedIn Post 01

## Title

Building a Voice-Enabled, AI-Powered Home Robot with ROS 2: Part 1, The Problem

## Draft

```md
🚀 **Building a Voice-Enabled, AI-Powered Home Robot with ROS 2 — Part 1: The Problem**

What if your home robot didn’t just follow commands, but actually *understood* your space?

That’s the challenge I’ve started tackling with a **Hiwonder MentorPi (ROS 2) robot powered by a Raspberry Pi 5** by combining SLAM, voice interaction, and agentic AI into a single system.

Here’s the vision:

🗺️ You manually guide the robot through a new environment  
🗣️ You say: *"This is the kitchen"*  
🧠 The robot remembers it, not just as a point, but as a meaningful space  

Later:

➡️ *"Go to the kitchen"* and it navigates autonomously  
🎒 *"Find my backpack in my office"* and it searches intelligently  

## The real problem

Robots today are already good at:

- Mapping spaces with SLAM
- Navigating to coordinates
- Avoiding obstacles

But humans do not think in coordinates.

We think in:

- Rooms
- Objects
- Intent

That means the real challenge is this:

How do we convert **natural language -> spatial understanding -> autonomous action**?

## The core challenge

To make this work, I need to combine:

- **Voice recognition** for understanding commands
- **Semantic mapping** for turning maps into named rooms with meaning
- **Navigation with Nav2** for reliable motion and obstacle avoidance
- **Agentic AI** for planning multi-step tasks like searching for objects

The interesting part is that these components do not naturally speak the same language.

## The architecture direction

At a high level:

- The **robot** handles SLAM and navigation
- A **dev laptop VM** handles voice, planning, and heavier AI workloads
- A **semantic map layer** connects rooms, objects, and robot actions

The goal is to move from:

❌ "Go to (x, y)"  
to  
✅ "Go to the kitchen and find my backpack"

## What comes next

In the next post, I’ll show how I’m moving from raw SLAM maps to a **polygon-based semantic map**, where rooms become named regions the robot can reason about.

If you're working on ROS 2, robotics, spatial AI, or voice interfaces, I’d love to compare notes.
```

## Suggested Companion Image Note

Use the architecture image generated in the original conversation or replace it with a repo-native diagram later.

Imported image metadata:

- `asset_pointer`: `sediment://file_00000000c2a071f5bff86c259adfab4f?shared_conversation_id=69dd8e49-3170-8326-825e-94707d7415e5`
- `generation_id`: `04588e2a-5e27-4294-8350-adab27702a14`
- `size`: `1024x1536`

## Optional Shorter Version

```md
I’m building a voice-enabled home robot with ROS 2 on a Hiwonder MentorPi powered by a Raspberry Pi 5.

The interesting challenge is not just mapping or navigation. It’s teaching the robot to understand spaces the way humans do:

- kitchen
- office
- backpack
- intent

The goal is to go beyond "navigate to (x, y)" and toward commands like:

"Go to the kitchen."
"Find my backpack in my office."

That means combining SLAM, Nav2, semantic mapping, voice interfaces, and AI planning into one system.

Next I’ll share how I’m representing rooms as polygons instead of points so the robot can reason about space more naturally.
```
