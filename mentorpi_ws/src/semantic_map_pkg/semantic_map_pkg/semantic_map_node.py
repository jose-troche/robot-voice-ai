import json
from pathlib import Path

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point32
from robot_voice_ai_interfaces.msg import ObjectSighting, Room
from robot_voice_ai_interfaces.srv import GetRoom, QueryObject

class SemanticMapNode(Node):
    def __init__(self) -> None:
        super().__init__("semantic_map_node")
        self._db_path = Path(__file__).resolve().parents[1] / "storage" / "map_db.json"
        self._db = self._load_db()
        self.create_subscription(Room, "/semantic_map/room_updates", self.handle_room_update, 10)
        self.create_subscription(
            ObjectSighting, "/semantic_map/object_updates", self.handle_object_update, 10
        )
        self.create_service(GetRoom, "/semantic_map/get_room", self.handle_get_room)
        self.create_service(QueryObject, "/semantic_map/query_object", self.handle_query_object)
        self.get_logger().info("semantic_map_node ready")

    def _load_db(self) -> dict:
        if self._db_path.exists():
            return json.loads(self._db_path.read_text(encoding="utf-8"))
        return {"rooms": {}, "objects": {}}

    def _save_db(self) -> None:
        self._db_path.write_text(json.dumps(self._db, indent=2), encoding="utf-8")

    def handle_room_update(self, msg: Room) -> None:
        polygon = [(point.x, point.y) for point in msg.polygon]
        room_entry = {
            "name": msg.name,
            "polygon": polygon,
            "centroid": [msg.centroid.x, msg.centroid.y],
            "entry_points": [[point.x, point.y] for point in msg.entry_points],
        }
        self._db["rooms"][msg.name] = room_entry
        self._save_db()
        self.get_logger().info(f"stored room '{msg.name}'")

    def handle_object_update(self, msg: ObjectSighting) -> None:
        self._db["objects"][msg.label] = {
            "label": msg.label,
            "position": [msg.position.x, msg.position.y],
            "room_name": msg.room_name,
            "last_seen": {
                "sec": msg.last_seen.sec,
                "nanosec": msg.last_seen.nanosec,
            },
        }
        self._save_db()
        self.get_logger().info(f"stored object sighting '{msg.label}'")

    def handle_get_room(self, request: GetRoom.Request, response: GetRoom.Response):
        room = self._db["rooms"].get(request.name)
        if not room:
            response.found = False
            return response

        response.found = True
        response.room = self._room_from_dict(room)
        return response

    def handle_query_object(
        self, request: QueryObject.Request, response: QueryObject.Response
    ):
        sighting = self._db["objects"].get(request.label)
        if not sighting:
            response.found = False
            return response

        response.found = True
        response.sighting = self._object_from_dict(sighting)
        return response

    def _room_from_dict(self, room: dict) -> Room:
        room_msg = Room()
        room_msg.name = room["name"]
        room_msg.polygon = [Point32(x=float(x), y=float(y), z=0.0) for x, y in room["polygon"]]
        room_msg.centroid = Point32(
            x=float(room["centroid"][0]), y=float(room["centroid"][1]), z=0.0
        )
        room_msg.entry_points = [
            Point32(x=float(x), y=float(y), z=0.0) for x, y in room["entry_points"]
        ]
        return room_msg

    def _object_from_dict(self, sighting: dict) -> ObjectSighting:
        msg = ObjectSighting()
        msg.label = sighting["label"]
        msg.position = Point32(
            x=float(sighting["position"][0]), y=float(sighting["position"][1]), z=0.0
        )
        msg.room_name = sighting.get("room_name", "")
        msg.last_seen.sec = int(sighting.get("last_seen", {}).get("sec", 0))
        msg.last_seen.nanosec = int(sighting.get("last_seen", {}).get("nanosec", 0))
        return msg


def main() -> None:
    rclpy.init()
    node = SemanticMapNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
