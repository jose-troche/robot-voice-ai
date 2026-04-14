import json

import rclpy
from rclpy.node import Node
from robot_voice_ai_interfaces.msg import TaskPlan
from std_msgs.msg import String

from .llm_interface import build_plan


class TaskPlannerNode(Node):
    def __init__(self) -> None:
        super().__init__("task_planner_node")
        self.create_subscription(String, "/high_level_command", self.handle_command, 10)
        self.plan_pub = self.create_publisher(TaskPlan, "/task_plan", 10)
        self.get_logger().info("task_planner_node ready")

    def handle_command(self, msg: String) -> None:
        intent_payload = json.loads(msg.data)
        plan = build_plan(intent_payload)
        task_plan = TaskPlan()
        task_plan.plan_type = plan.get("type", "")
        task_plan.goal = plan.get("goal", "")
        task_plan.query = plan.get("query", "")
        task_plan.target_name = plan.get("name", "")
        task_plan.reason = plan.get("reason", "")
        self.plan_pub.publish(task_plan)
        self.get_logger().info(f"published task plan '{task_plan.plan_type}'")


def main() -> None:
    rclpy.init()
    node = TaskPlannerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
