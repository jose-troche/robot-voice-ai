import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class NavigationExecutorNode(Node):
    def __init__(self) -> None:
        super().__init__("navigation_executor_node")
        self.create_subscription(String, "/task_plan", self.handle_plan, 10)
        self.response_pub = self.create_publisher(String, "/robot_response", 10)
        self.get_logger().info("navigation_executor_node ready")

    def handle_plan(self, msg: String) -> None:
        plan = json.loads(msg.data)
        if plan.get("type") != "navigate":
            return
        goal = plan.get("goal", "")
        self.get_logger().info(f"would send Nav2 goal for '{goal}'")
        self.response_pub.publish(String(data=f"Starting navigation to {goal}"))


def main() -> None:
    rclpy.init()
    node = NavigationExecutorNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
