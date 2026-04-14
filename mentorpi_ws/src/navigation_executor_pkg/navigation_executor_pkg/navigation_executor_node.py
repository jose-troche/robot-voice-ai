import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.action import ActionClient
from rclpy.node import Node
from robot_voice_ai_interfaces.msg import TaskPlan
from robot_voice_ai_interfaces.srv import GetRoom
from std_msgs.msg import String

try:
    from nav2_msgs.action import NavigateToPose
except ImportError:
    NavigateToPose = None


class NavigationExecutorNode(Node):
    def __init__(self) -> None:
        super().__init__("navigation_executor_node")
        self.create_subscription(TaskPlan, "/task_plan", self.handle_plan, 10)
        self.response_pub = self.create_publisher(String, "/robot_response", 10)
        self.get_room_client = self.create_client(GetRoom, "/semantic_map/get_room")
        self.nav_client = (
            ActionClient(self, NavigateToPose, "/navigate_to_pose")
            if NavigateToPose is not None
            else None
        )
        if self.nav_client is None:
            self.get_logger().warning(
                "nav2_msgs is unavailable; navigation goals will be reported but not executed"
            )
        self.get_logger().info("navigation_executor_node ready")

    def handle_plan(self, msg: TaskPlan) -> None:
        if msg.plan_type != "navigate":
            return
        room_name = msg.goal
        request = GetRoom.Request()
        request.name = room_name

        if self.nav_client is None:
            self.response_pub.publish(
                String(data="Nav2 is unavailable in this environment; cannot execute navigation")
            )
            self.get_logger().warning("cannot execute navigation without nav2_msgs")
            return

        if not self.get_room_client.wait_for_service(timeout_sec=1.0):
            self.response_pub.publish(String(data="Semantic map service not available"))
            self.get_logger().warning("semantic map service unavailable")
            return

        future = self.get_room_client.call_async(request)
        future.add_done_callback(
            lambda done_future: self._handle_room_lookup(done_future, room_name)
        )

    def _handle_room_lookup(self, future, room_name: str) -> None:
        response = future.result()
        if response is None or not response.found:
            self.response_pub.publish(String(data=f"Unknown room: {room_name}"))
            self.get_logger().warning(f"room lookup failed for '{room_name}'")
            return

        pose = PoseStamped()
        pose.header.frame_id = "map"
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = response.room.centroid.x
        pose.pose.position.y = response.room.centroid.y
        pose.pose.orientation.w = 1.0

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose

        if not self.nav_client.wait_for_server(timeout_sec=1.0):
            self.response_pub.publish(String(data="Nav2 action server not available"))
            self.get_logger().warning("navigate_to_pose action server unavailable")
            return

        self.response_pub.publish(String(data=f"Starting navigation to {room_name}"))
        send_goal_future = self.nav_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(
            lambda done_future: self._handle_goal_response(done_future, room_name)
        )

    def _handle_goal_response(self, future, room_name: str) -> None:
        goal_handle = future.result()
        if goal_handle is None or not goal_handle.accepted:
            self.response_pub.publish(String(data=f"Navigation rejected for {room_name}"))
            self.get_logger().warning(f"navigation goal rejected for '{room_name}'")
            return

        self.get_logger().info(f"navigation goal accepted for '{room_name}'")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(
            lambda done_future: self._handle_goal_result(done_future, room_name)
        )

    def _handle_goal_result(self, future, room_name: str) -> None:
        result = future.result()
        status = getattr(result, "status", None)
        self.response_pub.publish(
            String(data=f"Navigation finished for {room_name} with status {status}")
        )
        self.get_logger().info(f"navigation finished for '{room_name}' with status {status}")


def main() -> None:
    rclpy.init()
    node = NavigationExecutorNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
