import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SpeechToTextNode(Node):
    def __init__(self) -> None:
        super().__init__("speech_to_text_node")
        self.voice_pub = self.create_publisher(String, "/voice_text", 10)
        self.get_logger().info("speech_to_text_node ready; replace with real STT backend")


def main() -> None:
    rclpy.init()
    node = SpeechToTextNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
