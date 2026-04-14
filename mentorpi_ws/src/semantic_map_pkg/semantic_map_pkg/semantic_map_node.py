import json
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .polygon_utils import centroid, normalize_polygon


class SemanticMapNode(Node):
    def __init__(self) -> None:
        super().__init__("semantic_map_node")
        self._db_path = Path(__file__).resolve().parents[1] / "storage" / "map_db.json"
        self._db = self._load_db()
        self.create_subscription(String, "/semantic_map/update", self.handle_update, 10)
        self.query_pub = self.create_publisher(String, "/semantic_map/query_result", 10)
        self.get_logger().info("semantic_map_node ready")

    def _load_db(self) -> dict:
        if self._db_path.exists():
            return json.loads(self._db_path.read_text(encoding="utf-8"))
        return {"rooms": {}, "objects": {}}

    def _save_db(self) -> None:
        self._db_path.write_text(json.dumps(self._db, indent=2), encoding="utf-8")

    def handle_update(self, msg: String) -> None:
        payload = json.loads(msg.data)
        update_type = payload.get("type")

        if update_type == "room":
            room_name = payload["name"]
            polygon = normalize_polygon(payload["polygon"])
            room_entry = {
                "name": room_name,
                "polygon": polygon,
                "centroid": centroid(polygon),
                "entry_points": payload.get("entry_points", []),
            }
            self._db["rooms"][room_name] = room_entry
            self._save_db()
            self.get_logger().info(f"stored room '{room_name}'")
            return

        if update_type == "object":
            label = payload["label"]
            self._db["objects"][label] = payload
            self._save_db()
            self.get_logger().info(f"stored object sighting '{label}'")
            return

        if update_type == "query_room":
            room_name = payload["name"]
            result = self._db["rooms"].get(room_name, {})
            self.query_pub.publish(String(data=json.dumps(result)))
            self.get_logger().info(f"queried room '{room_name}'")


def main() -> None:
    rclpy.init()
    node = SemanticMapNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
