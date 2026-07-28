import rclpy
from geometry_msgs.msg import PoseStamped
from moveit.planning import MoveItPy

def plan_and_execute(moveit_instance, planning_component):
    """플래닝 컴포넌트의 궤적을 생성하고 실행하는 헬퍼 함수"""
    plan_result = planning_component.plan()
    if plan_result:
        # 생성된 궤적(Trajectory)을 실제 로봇(또는 시뮬레이터)에 실행
        moveit_instance.execute(plan_result.trajectory, controllers=[])
        return True
    return False

def create_pose_stamped(x, y, z, qx=0.0, qy=1.0, qz=0.0, qw=0.0, frame_id="base_link"):
    """목표 좌표와 자세를 담은 PoseStamped 메시지 생성"""
    pose = PoseStamped()
    pose.header.frame_id = frame_id
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = z
    # 로봇팔 끝단(End-effector)의 방향 (쿼터니언) - 보통 아래를 향하도록 설정
    pose.pose.orientation.x = qx
    pose.pose.orientation.y = qy
    pose.pose.orientation.z = qz
    pose.pose.orientation.w = qw
    return pose

def main(args=None):
    rclpy.init(args=args)

    # 1. MoveItPy 인스턴스 생성 및 플래닝 그룹 로드
    moveit = MoveItPy(node_name="pick_and_place_node")
    arm = moveit.get_planning_component("ur_manipulator") # 로봇팔 그룹명 (UR 예시)
    gripper = moveit.get_planning_component("gripper")    # 그리퍼 그룹명

    # 물건 위치와 목표 위치 설정 (미터 단위)
    item_x, item_y, item_z = 0.5, 0.0, 0.1
    target_x, target_y, target_z = 0.0, 0.5, 0.1
    safe_z = 0.3 # 들어올릴 안전 높이

    print("--- 픽앤플레이스 시퀀스 시작 ---")

    # 2. 접근 위치로 이동 (Approach)
    print("물건 위로 접근 중...")
    approach_pose = create_pose_stamped(item_x, item_y, safe_z)
    arm.set_start_state_to_current_state()
    arm.set_goal_state(pose_stamped_msg=approach_pose, pose_link="tool0")
    plan_and_execute(moveit, arm)

    # 3. 하강 (Descend) & 파지 (Grasp)
    print("하강 및 물건 잡기...")
    grasp_pose = create_pose_stamped(item_x, item_y, item_z)
    arm.set_start_state_to_current_state()
    arm.set_goal_state(pose_stamped_msg=grasp_pose, pose_link="tool0")
    plan_and_execute(moveit, arm)

    # 그리퍼 닫기 (사전 정의된 "close" 상태 활용)
    gripper.set_start_state_to_current_state()
    gripper.set_goal_state(configuration_name="close")
    plan_and_execute(moveit, gripper)

    # 4. 안전 높이로 상승 및 목표 위치로 이동
    print("목표 위치로 이동 중...")
    arm.set_start_state_to_current_state()
    arm.set_goal_state(pose_stamped_msg=create_pose_stamped(item_x, item_y, safe_z), pose_link="tool0")
    plan_and_execute(moveit, arm)

    target_approach_pose = create_pose_stamped(target_x, target_y, safe_z)
    arm.set_start_state_to_current_state()
    arm.set_goal_state(pose_stamped_msg=target_approach_pose, pose_link="tool0")
    plan_and_execute(moveit, arm)

    # 5. 하강 및 물건 놓기 (Release)
    print("하강 및 물건 놓기...")
    arm.set_start_state_to_current_state()
    arm.set_goal_state(pose_stamped_msg=create_pose_stamped(target_x, target_y, target_z), pose_link="tool0")
    plan_and_execute(moveit, arm)

    # 그리퍼 열기
    gripper.set_start_state_to_current_state()
    gripper.set_goal_state(configuration_name="open")
    plan_and_execute(moveit, gripper)

    # 6. 홈 위치로 복귀
    print("홈 위치 복귀 중...")
    arm.set_start_state_to_current_state()
    arm.set_goal_state(pose_stamped_msg=target_approach_pose, pose_link="tool0") # 먼저 위로 회피
    plan_and_execute(moveit, arm)
    
    arm.set_start_state_to_current_state()
    arm.set_goal_state(configuration_name="home")
    plan_and_execute(moveit, arm)

    rclpy.shutdown()

if __name__ == "__main__":
    main()