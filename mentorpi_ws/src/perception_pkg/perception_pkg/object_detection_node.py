import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ObjectDetectionNode(Node):
    def __init__(self) -> None:
        super().__init__("object_detection_node")
        self.detection_pub = self.create_publisher(String, "/detected_objects", 10)
        self.get_logger().info("object_detection_node ready; replace with detector backend")

    def publish_detection(self, label: str, pose=None) -> None:
        pose = pose or [0.0, 0.0]
        payload = {"label": label, "pose": pose}
        self.detection_pub.publish(String(data=json.dumps(payload)))


def main() -> None:
    rclpy.init()
    node = ObjectDetectionNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
