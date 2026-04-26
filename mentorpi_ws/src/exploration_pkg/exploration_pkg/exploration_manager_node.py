import rclpy
from geometry_msgs.msg import Point, Point32, PointStamped
from rclpy.node import Node
from robot_voice_ai_interfaces.msg import Room
from std_msgs.msg import String
from visualization_msgs.msg import Marker

from .polygon_builder import build_polygon
from .voice_tag_handler import is_clear_polygon_command, parse_room_tag


LINE_MARKER_ID = 1
POINT_MARKER_ID = 2


class ExplorationManagerNode(Node):
    def __init__(self) -> None:
        super().__init__("exploration_manager_node")
        self._clicked_points = []
        self.create_subscription(String, "/voice_text", self.handle_voice_text, 10)
        self.create_subscription(PointStamped, "/clicked_point", self.handle_clicked_point, 10)
        self.room_update_pub = self.create_publisher(Room, "/semantic_map/room_updates", 10)
        self.marker_pub = self.create_publisher(Marker, "/exploration/current_polygon", 10)
        self.get_logger().info("exploration_manager_node ready")

    def handle_clicked_point(self, msg: PointStamped) -> None:
        self._clicked_points.append((float(msg.point.x), float(msg.point.y)))
        self.publish_polygon_markers()
        self.get_logger().info(
            f"added polygon point {len(self._clicked_points)} at ({msg.point.x:.2f}, {msg.point.y:.2f})"
        )

    def handle_voice_text(self, msg: String) -> None:
        if is_clear_polygon_command(msg.data):
            self.clear_polygon()
            self.get_logger().info("cleared in-progress room polygon")
            return

        room_name = parse_room_tag(msg.data)
        if not room_name:
            return

        if len(self._clicked_points) < 3:
            self.get_logger().warning(
                "need at least 3 clicked points in RViz before saving a room polygon"
            )
            return

        polygon = build_polygon(self._clicked_points)
        centroid_x = sum(x for x, _ in polygon) / len(polygon)
        centroid_y = sum(y for _, y in polygon) / len(polygon)
        room_msg = Room()
        room_msg.name = room_name
        room_msg.polygon = [Point32(x=x, y=y, z=0.0) for x, y in polygon]
        room_msg.centroid = Point32(x=centroid_x, y=centroid_y, z=0.0)
        room_msg.entry_points = [Point32(x=polygon[0][0], y=polygon[0][1], z=0.0)]
        self.room_update_pub.publish(room_msg)
        self.get_logger().info(f"published room annotation for '{room_name}'")
        self.clear_polygon()

    def clear_polygon(self) -> None:
        self._clicked_points = []
        self.publish_polygon_markers()

    def publish_polygon_markers(self) -> None:
        self.marker_pub.publish(self._build_line_marker())
        self.marker_pub.publish(self._build_point_marker())

    def _build_line_marker(self) -> Marker:
        marker = Marker()
        marker.header.frame_id = "map"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "room_polygon"
        marker.id = LINE_MARKER_ID
        marker.action = Marker.ADD if self._clicked_points else Marker.DELETE
        marker.type = Marker.LINE_STRIP
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.05
        marker.color.a = 0.95
        marker.color.r = 0.1
        marker.color.g = 0.8
        marker.color.b = 0.2

        for x, y in self._clicked_points:
            marker.points.append(Point(x=x, y=y, z=0.0))

        if len(self._clicked_points) >= 3:
            first_x, first_y = self._clicked_points[0]
            marker.points.append(Point(x=first_x, y=first_y, z=0.0))

        return marker

    def _build_point_marker(self) -> Marker:
        marker = Marker()
        marker.header.frame_id = "map"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "room_polygon"
        marker.id = POINT_MARKER_ID
        marker.action = Marker.ADD if self._clicked_points else Marker.DELETE
        marker.type = Marker.SPHERE_LIST
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.15
        marker.scale.y = 0.15
        marker.scale.z = 0.15
        marker.color.a = 0.95
        marker.color.r = 1.0
        marker.color.g = 0.55
        marker.color.b = 0.1

        for x, y in self._clicked_points:
            marker.points.append(Point(x=x, y=y, z=0.0))

        return marker


def main() -> None:
    rclpy.init()
    node = ExplorationManagerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
