import os
import random
import yaml

from action_msgs.msg import GoalStatus
from ament_index_python.packages import get_package_share_directory
from control_msgs.action import GripperCommand, GripperCommand_GetResult_Response
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.task import Future
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


class DanceManipulator(Node):
    def __init__(self):
        super().__init__("dance_manipulator")

        # 패키지의 share 디렉토리에서 YAML 파일 경로 자동 탐색
        try:
            package_share_dir = get_package_share_directory("tf2_basic")
            yaml_path = os.path.join(package_share_dir, "config", "dance_positions.yaml")
        except Exception:
            yaml_path = "config/dance_positions.yaml"

        # 1. 포지션 데이터 로드
        self.dance_data = self.load_dance_positions(yaml_path)
        self.joint_names = self.dance_data.get(
            "joint_names", ["joint1", "joint2", "joint3", "joint4"]
        )
        self.pose_keys = list(self.dance_data.get("poses", {}).keys())

        # 동작 변경 주기 (2초)
        self.duration_sec = 2.0
        self.create_timer(self.duration_sec, self.timer_callback)

        # Publisher, Action Client, Subscription 설정
        self.pub = self.create_publisher(
            JointTrajectory, "arm_controller/joint_trajectory", 10
        )
        self.gripper_client = ActionClient(
            self, GripperCommand, "/gripper_controller/gripper_cmd"
        )
        self.joint_state_subscription = self.create_subscription(
            JointState, "joint_states", self.joint_callback, 10
        )

        self.current_joint_position = [0.0, 0.0, 0.0, 0.0]

    def load_dance_positions(self, file_path: str) -> dict:
        """YAML 파일 로드"""
        if not os.path.exists(file_path):
            self.get_logger().error(f"파일을 찾을 수 없습니다: {file_path}")
            return {"poses": {}}

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            self.get_logger().info(f"춤 포지션 데이터 로드 완료: {file_path}")
            return data

    def timer_callback(self):
        if not self.pose_keys:
            self.get_logger().warn("사용 가능한 춤 포지션이 없습니다.")
            return

        # 2. random 함수를 사용해 포지션 무작위 선택
        selected_key = random.choice(self.pose_keys)
        target_pose = self.dance_data["poses"][selected_key]

        self.get_logger().info(f"[Dance Action] 선택된 춤 동작: {selected_key}")

        # Trajectory 메시지 구성
        msg = JointTrajectory()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "move_manipulator"
        msg.joint_names = self.joint_names

        point = JointTrajectoryPoint()
        point.positions = [float(p) for p in target_pose["positions"]]

        # 이동 완료 시간 설정
        seconds = int(self.duration_sec)
        nanoseconds = int((self.duration_sec - seconds) * 1_000_000_000)
        point.time_from_start.sec = seconds
        point.time_from_start.nanosec = nanoseconds

        msg.points.append(point)  # type: ignore
        self.pub.publish(msg)

        # 그리퍼 동작 수행
        if "gripper" in target_pose:
            self.move_gripper(target_pose["gripper"])

    def joint_callback(self, msg: JointState):
        self.current_joint_position = list(msg.position)

    def move_gripper(self, position: float, max_effort=10.0, timeout_sec=1.0):
        if not self.gripper_client.wait_for_server(timeout_sec=timeout_sec):
            self.get_logger().warn("gripper_controller Action 서버 대기 중...")
            return

        goal = GripperCommand.Goal()
        goal.command.position = float(position)
        goal.command.max_effort = float(max_effort)

        send_goal_future = self.gripper_client.send_goal_async(goal)
        send_goal_future.add_done_callback(self.goal_callback)

    def goal_callback(self, future: Future):
        goal_handle = future.result()  # type: ignore
        if not goal_handle.accepted:
            return
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future: Future):
        result: GripperCommand_GetResult_Response = future.result()  # type: ignore
        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f"그리퍼 이동 완료: {result.result.position}")


def main(args=None):
    rclpy.init(args=args)
    node = DanceManipulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()