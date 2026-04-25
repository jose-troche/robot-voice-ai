#!/usr/bin/env python3

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


WORKSPACE_DIR = Path(__file__).resolve().parents[1]
MAP_DB_PATH = WORKSPACE_DIR / "src" / "semantic_map_pkg" / "storage" / "map_db.json"
DEFAULT_TIMEOUT_SECONDS = 20.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch the MentorPi smoke-test stack, publish a room tag, and verify it lands in map_db.json."
    )
    parser.add_argument(
        "--room-name",
        default=f"smoke_test_room_{int(time.time())}",
        help="Room name to publish through /voice_text.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Seconds to wait for subscribers and semantic map updates.",
    )
    parser.add_argument(
        "--keep-room",
        action="store_true",
        help="Keep the inserted room in map_db.json instead of restoring the original file contents.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"rooms": {}, "objects": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def restore_original_map_db(original_contents: Optional[str]) -> None:
    if original_contents is None:
        if MAP_DB_PATH.exists():
            MAP_DB_PATH.unlink()
        return
    MAP_DB_PATH.write_text(original_contents, encoding="utf-8")


def wait_for_room_in_db(room_name: str, timeout: float) -> Optional[dict]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        db = load_json(MAP_DB_PATH)
        room = db.get("rooms", {}).get(room_name)
        if room:
            return room
        time.sleep(0.25)
    return None


def wait_for_subscriber(node: Node, publisher, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)
        if publisher.get_subscription_count() > 0:
            return True
        time.sleep(0.1)
    return False


def shutdown_launch_process(process: subprocess.Popen, timeout: float = 10.0) -> None:
    if process.poll() is not None:
        return

    process.send_signal(signal.SIGINT)
    try:
        process.wait(timeout=timeout)
        return
    except subprocess.TimeoutExpired:
        process.terminate()

    try:
        process.wait(timeout=5.0)
        return
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5.0)


def main() -> int:
    args = parse_args()

    os.environ.setdefault("RMW_IMPLEMENTATION", "rmw_fastrtps_cpp")
    os.environ.setdefault("ROS_LOG_DIR", str(WORKSPACE_DIR / "log"))

    launch_log_path = WORKSPACE_DIR / "log" / "exploration_smoke_test.launch.log"
    launch_log_path.parent.mkdir(parents=True, exist_ok=True)
    original_map_db = MAP_DB_PATH.read_text(encoding="utf-8") if MAP_DB_PATH.exists() else None

    launch_cmd = ["ros2", "launch", "robot_bringup", "smoke_test.launch.py"]
    launch_log = launch_log_path.open("w", encoding="utf-8")
    launch_process = subprocess.Popen(
        launch_cmd,
        cwd=WORKSPACE_DIR,
        env=os.environ.copy(),
        stdout=launch_log,
        stderr=subprocess.STDOUT,
        text=True,
    )

    room_entry = None
    published_phrase = f"this is {args.room_name}"
    node = None

    try:
        time.sleep(5.0)
        if launch_process.poll() is not None:
            launch_log.close()
            log_tail = launch_log_path.read_text(encoding="utf-8").splitlines()[-40:]
            print("Launch exited before the smoke test could publish.", file=sys.stderr)
            if log_tail:
                print("\n".join(log_tail), file=sys.stderr)
            return 1

        rclpy.init()
        node = Node("exploration_smoke_test_publisher")
        publisher = node.create_publisher(String, "/voice_text", 10)

        if not wait_for_subscriber(node, publisher, args.timeout):
            print(
                "Timed out waiting for a subscriber on /voice_text. "
                f"Check {launch_log_path} for stack startup logs.",
                file=sys.stderr,
            )
            return 1

        msg = String()
        msg.data = published_phrase
        for _ in range(3):
            publisher.publish(msg)
            rclpy.spin_once(node, timeout_sec=0.1)
            time.sleep(0.2)

        room_entry = wait_for_room_in_db(args.room_name, args.timeout)
        if not room_entry:
            print(
                f"Room '{args.room_name}' was not written to {MAP_DB_PATH}. "
                f"Check {launch_log_path} for details.",
                file=sys.stderr,
            )
            return 1

        print("Exploration smoke test passed.")
        print(f"Published phrase: {published_phrase}")
        print(json.dumps(room_entry, indent=2))
        return 0
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

        shutdown_launch_process(launch_process)
        launch_log.close()

        if room_entry and not args.keep_room:
            restore_original_map_db(original_map_db)
            print("Restored original map_db.json contents.")


if __name__ == "__main__":
    raise SystemExit(main())
