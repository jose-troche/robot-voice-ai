import rclpy
from geometry_msgs.msg import Point32
from rclpy.node import Node
from robot_voice_ai_interfaces.msg import ObjectSighting
from std_msgs.msg import String


class ObjectDetectionNode(Node):
    def __init__(self) -> None:
        super().__init__("object_detection_node")
        self.detection_pub = self.create_publisher(ObjectSighting, "/detected_objects", 10)
        self.object_update_pub = self.create_publisher(
            ObjectSighting, "/semantic_map/object_updates", 10
        )
        self.get_logger().info("object_detection_node ready; replace with detector backend")

    def publish_detection(self, label: str, pose=None, room_name: str = "") -> None:
        pose = pose or [0.0, 0.0]
        msg = ObjectSighting()
        msg.label = label
        msg.position = Point32(x=float(pose[0]), y=float(pose[1]), z=0.0)
        msg.room_name = room_name
        msg.last_seen = self.get_clock().now().to_msg()
        self.detection_pub.publish(msg)
        self.object_update_pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = ObjectDetectionNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
