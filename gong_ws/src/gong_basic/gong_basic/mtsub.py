import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Header

class MTSub(Node):
    def __init__(self):
        super().__init__('mtsub')
        # 토픽 2개 각각 구독 등록
        self.sub_msg = self.create_subscription(String, 'message1', self.msg_cb, 10)
        self.sub_time = self.create_subscription(Header, 'time', self.time_cb, 10)

    def msg_cb(self, msg):
        self.get_logger().info(f'mtsub (msg1): {msg.data}')

    def time_cb(self, msg):
        self.get_logger().info(f'mtsub (time): sec={msg.stamp.sec}')

def main(args=None):
    rclpy.init(args=args)
    node = MTSub()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
    