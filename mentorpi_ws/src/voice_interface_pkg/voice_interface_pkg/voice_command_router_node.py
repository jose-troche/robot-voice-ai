import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .intent_parser import parse_intent


class VoiceCommandRouterNode(Node):
    def __init__(self) -> None:
        super().__init__("voice_command_router_node")
        self.create_subscription(String, "/voice_text", self.handle_voice_text, 10)
        self.intent_pub = self.create_publisher(String, "/high_level_command", 10)
        self.get_logger().info("voice_command_router_node ready")

    def handle_voice_text(self, msg: String) -> None:
        parsed = parse_intent(msg.data)
        self.intent_pub.publish(String(data=json.dumps(parsed)))
        self.get_logger().info(f"routed intent '{parsed['intent']}'")


def main() -> None:
    rclpy.init()
    node = VoiceCommandRouterNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
