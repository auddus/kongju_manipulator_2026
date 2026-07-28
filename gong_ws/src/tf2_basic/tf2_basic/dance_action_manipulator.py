import os
import random
import yaml

from action_msgs.msg import GoalStatus
from ament_index_python.packages import get_package_share_directory
from control_msgs.action import GripperCommand, FollowJointTrajectory
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

        # Action Client 및 Subscription 설정
        # (기존 Publisher를 ActionClient로 변경)
        self.arm_client = ActionClient(
            self, FollowJointTrajectory, "arm_controller/follow_joint_trajectory"
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

        # 암 컨트롤러 서버 대기
        if not self.arm_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().warn("arm_controller Action 서버 대기 중...")
            return

        # 2. random 함수를 사용해 포지션 무작위 선택
        selected_key = random.choice(self.pose_keys)
        target_pose = self.dance_data["poses"][selected_key]

        self.get_logger().info(f"[Dance Action] 선택된 춤 동작: {selected_key}")

        # Trajectory 메시지 구성
        trajectory_msg = JointTrajectory()
        trajectory_msg.joint_names = self.joint_names

        point = JointTrajectoryPoint()
        point.positions = [float(p) for p in target_pose["positions"]]

        # 이동 완료 시간 설정
        seconds = int(self.duration_sec)
        nanoseconds = int((self.duration_sec - seconds) * 1_000_000_000)
        point.time_from_start.sec = seconds
        point.time_from_start.nanosec = nanoseconds

        trajectory_msg.points.append(point)

        # 3. Action Goal 설정 및 전송
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = trajectory_msg

        # Arm Action 전송 (완료 시 피드백을 받으려면 콜백 추가 가능)
        send_goal_future = self.arm_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.arm_goal_callback)

        # 그리퍼 동작 수행
        if "gripper" in target_pose:
            self.move_gripper(target_pose["gripper"])

    def arm_goal_callback(self, future: Future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn("로봇팔 동작 거부됨")
            return
        
        # 동작 완료 후의 결과를 확인하고 싶다면 아래 주석을 해제하세요.
        # get_result_future = goal_handle.get_result_async()
        # get_result_future.add_done_callback(self.arm_result_callback)

    # def arm_result_callback(self, future: Future):
    #     result = future.result().status
    #     if result == GoalStatus.STATUS_SUCCEEDED:
    #         self.get_logger().info("로봇팔 이동 완료")

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
        send_goal_future.add_done_callback(self.gripper_goal_callback)

    def gripper_goal_callback(self, future: Future):
        goal_handle = future.result() 
        if not goal_handle.accepted:
            return
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.gripper_result_callback)

    def gripper_result_callback(self, future: Future):
        result: GripperCommand_GetResult_Response = future.result()
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