import math
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from turtlesim.msg import Color, Pose


class Move_tutle(Node):

    def __init__(self):
        super().__init__("move_turtle")

        # 0.05초 단위로 타이머 실행 (스무스한 움직임)
        self.create_timer(0.05, self.timer_callback)
        self.pub = self.create_publisher(Twist, "turtle1/cmd_vel", 10)
        self.create_subscription(Pose, "turtle1/pose", self.pose_callback, 10)
        self.create_subscription(
            Color, "turtle1/color_sensor", self.color_callback, 10
        )

        self.pose = Pose()
        self.color = Color()
        self.time_counter = 0.0
        self.state = "ZIGZAG"  # 상태: 'ZIGZAG' 또는 'TURN_WALL'
        self.turn_timer = 0

    def timer_callback(self):
        msg = Twist()
        self.time_counter += 0.05

        # 1. self.pose 기반 벽 충돌 경계 감지 (turtlesim의 맵크기: 0.0 ~ 11.0)
        is_near_wall = (
            self.pose.x < 1.5
            or self.pose.x > 9.5
            or self.pose.y < 1.5
            or self.pose.y > 9.5
        )

        if self.state == "ZIGZAG":
            if is_near_wall:
                # 벽에 가까워지면 회전 상태로 전환
                self.state = "TURN_WALL"
                self.turn_timer = 20  # 약 1초 동안 강제 유턴
                # self.color 정보를 사용해 로그 출력
                self.get_logger().warn(
                    f"🚨 벽 감지! 위치: ({self.pose.x:.1f}, {self.pose.y:.1f}) | 바닥 RGB: ({self.color.r}, {self.color.g}, {self.color.b})"
                )
            else:
                # [지그재그 주행] 직진 속도를 유지하면서 각속도를 사인파(sin)로 흔듦
                msg.linear.x = 2.0
                msg.angular.z = 4.0 * math.sin(
                    self.time_counter * 5.0
                )  # 좌우로 빠르게 번갈아가며 회전

        elif self.state == "TURN_WALL":
            # [벽 회피] 제자리에서 핑그르르 돌면서 방향 전환
            msg.linear.x = 0.5
            msg.angular.z = 3.5
            self.turn_timer -= 1

            # 유턴 타이머가 끝나고 벽에서 벗어나면 다시 지그재그 모드로 복귀
            if self.turn_timer <= 0 and not is_near_wall:
                self.state = "ZIGZAG"

        self.pub.publish(msg)

    def pose_callback(self, msg: Pose):
        self.pose = msg

    def color_callback(self, msg: Color):
        self.color = msg


def main(args=None):
    rclpy.init(args=args)
    node = Move_tutle()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("키보드 인터럽트")
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
    