import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .polygon_builder import build_polygon
from .voice_tag_handler import parse_room_tag


class ExplorationManagerNode(Node):
    def __init__(self) -> None:
        super().__init__("exploration_manager_node")
        self.create_subscription(String, "/voice_text", self.handle_voice_text, 10)
        self.map_update_pub = self.create_publisher(String, "/semantic_map/update", 10)
        self.get_logger().info("exploration_manager_node ready")

    def handle_voice_text(self, msg: String) -> None:
        room_name = parse_room_tag(msg.data)
        if not room_name:
            return

        # Placeholder polygon until RViz or path-capture tooling is added.
        polygon = build_polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        payload = {
            "type": "room",
            "name": room_name,
            "polygon": polygon,
            "entry_points": [[0.5, 0.0]],
        }
        self.map_update_pub.publish(String(data=json.dumps(payload)))
        self.get_logger().info(f"published room annotation for '{room_name}'")


def main() -> None:
    rclpy.init()
    node = ExplorationManagerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
