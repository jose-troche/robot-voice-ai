from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            SetEnvironmentVariable("ROS_LOG_DIR", "/tmp/roslogs"),
            Node(
                package="semantic_map_pkg",
                executable="semantic_map_node",
                name="semantic_map_node",
                output="screen",
            ),
            Node(
                package="voice_interface_pkg",
                executable="voice_command_router_node",
                name="voice_command_router_node",
                output="screen",
            ),
            Node(
                package="task_planning_pkg",
                executable="task_planner_node",
                name="task_planner_node",
                output="screen",
            ),
            Node(
                package="navigation_executor_pkg",
                executable="navigation_executor_node",
                name="navigation_executor_node",
                output="screen",
            ),
            Node(
                package="exploration_pkg",
                executable="exploration_manager_node",
                name="exploration_manager_node",
                output="screen",
            ),
            Node(
                package="perception_pkg",
                executable="object_search_node",
                name="object_search_node",
                output="screen",
            ),
        ]
    )
