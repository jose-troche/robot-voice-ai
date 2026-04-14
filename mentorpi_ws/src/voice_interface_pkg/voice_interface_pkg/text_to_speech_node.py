import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TextToSpeechNode(Node):
    def __init__(self) -> None:
        super().__init__("text_to_speech_node")
        self.create_subscription(String, "/robot_response", self.handle_response, 10)
        self.get_logger().info("text_to_speech_node ready; replace with real TTS backend")

    def handle_response(self, msg: String) -> None:
        self.get_logger().info(f"TTS output: {msg.data}")


def main() -> None:
    rclpy.init()
    node = TextToSpeechNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
