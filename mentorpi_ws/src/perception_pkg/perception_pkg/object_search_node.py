import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ObjectSearchNode(Node):
    def __init__(self) -> None:
        super().__init__("object_search_node")
        self.create_subscription(String, "/task_plan", self.handle_plan, 10)
        self.create_subscription(String, "/detected_objects", self.handle_detection, 10)
        self.response_pub = self.create_publisher(String, "/robot_response", 10)
        self.current_query = None
        self.get_logger().info("object_search_node ready")

    def handle_plan(self, msg: String) -> None:
        plan = json.loads(msg.data)
        if plan.get("type") != "search_object":
            return
        self.current_query = plan.get("query", "")
        self.get_logger().info(f"starting object search for '{self.current_query}'")
        self.response_pub.publish(String(data=f"Searching for {self.current_query}"))

    def handle_detection(self, msg: String) -> None:
        if not self.current_query:
            return
        detection = json.loads(msg.data)
        self.get_logger().info(f"received detection candidate {detection}")


def main() -> None:
    rclpy.init()
    node = ObjectSearchNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
