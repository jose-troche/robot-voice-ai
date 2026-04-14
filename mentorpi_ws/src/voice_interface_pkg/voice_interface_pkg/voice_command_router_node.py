import rclpy
from rclpy.node import Node
from robot_voice_ai_interfaces.msg import IntentCommand
from std_msgs.msg import String

from .intent_parser import parse_intent


class VoiceCommandRouterNode(Node):
    def __init__(self) -> None:
        super().__init__("voice_command_router_node")
        self.create_subscription(String, "/voice_text", self.handle_voice_text, 10)
        self.intent_pub = self.create_publisher(IntentCommand, "/high_level_command", 10)
        self.get_logger().info("voice_command_router_node ready")

    def handle_voice_text(self, msg: String) -> None:
        parsed = parse_intent(msg.data)
        intent_msg = IntentCommand()
        intent_msg.intent = parsed.get("intent", "")
        intent_msg.target = parsed.get("target", "")
        intent_msg.query = parsed.get("query", "")
        intent_msg.raw_text = parsed.get("raw_text", msg.data)
        self.intent_pub.publish(intent_msg)
        self.get_logger().info(f"routed intent '{intent_msg.intent}'")


def main() -> None:
    rclpy.init()
    node = VoiceCommandRouterNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
