import rclpy
from rclpy.node import Node
from std_msgs.msg import String


# 1. /message1 을 구독하는 msub 클래스
class Msub(Node):

    def __init__(self):
        super().__init__("msub")
        self.sub = self.create_subscription(
            String, "message1", self.listener_callback, 10
        )

    def listener_callback(self, msg):
        self.get_logger().info(f'msub received: "{msg.data}"')


# 2. /message2 를 구독하는 m2sub 클래스
class M2sub(Node):

    def __init__(self):
        super().__init__("m2sub")
        self.sub = self.create_subscription(
            String, "message2", self.listener_callback, 10
        )

    def listener_callback(self, msg):
        self.get_logger().info(f'm2sub received: "{msg.data}"')


# setup.py 의 console_scripts 항목에 맞춰 실행 함수 정의
def main(args=None):
    rclpy.init(args=args)
    node = Msub()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


def main2(args=None):
    rclpy.init(args=args)
    node = M2sub()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()