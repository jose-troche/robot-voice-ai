import rclpy
from geometry_msgs.msg import Point32
from rclpy.node import Node
from robot_voice_ai_interfaces.msg import Room
from std_msgs.msg import String

from .polygon_builder import build_polygon
from .voice_tag_handler import parse_room_tag


class ExplorationManagerNode(Node):
    def __init__(self) -> None:
        super().__init__("exploration_manager_node")
        self.create_subscription(String, "/voice_text", self.handle_voice_text, 10)
        self.room_update_pub = self.create_publisher(Room, "/semantic_map/room_updates", 10)
        self.get_logger().info("exploration_manager_node ready")

    def handle_voice_text(self, msg: String) -> None:
        room_name = parse_room_tag(msg.data)
        if not room_name:
            return

        # Placeholder polygon until RViz or path-capture tooling is added.
        polygon = build_polygon([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        room_msg = Room()
        room_msg.name = room_name
        room_msg.polygon = [Point32(x=x, y=y, z=0.0) for x, y in polygon]
        room_msg.centroid = Point32(x=0.5, y=0.5, z=0.0)
        room_msg.entry_points = [Point32(x=0.5, y=0.0, z=0.0)]
        self.room_update_pub.publish(room_msg)
        self.get_logger().info(f"published room annotation for '{room_name}'")


def main() -> None:
    rclpy.init()
    node = ExplorationManagerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
