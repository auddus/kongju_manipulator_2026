import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MPub(Node):
    def __init__(self):
        super().__init__('mpub')
        self.pub1 = self.create_publisher(String, 'message1', 10)
        self.pub2 = self.create_publisher(String, 'message2', 10)
        self.create_timer(1.0, self.timer_callback)
        self.count = 0

    def timer_callback(self):
        msg1 = String()
        msg1.data = f'Message1 Data: {self.count}'
        self.pub1.publish(msg1)

        msg2 = String()
        msg2.data = f'Message2 Data: {self.count}'
        self.pub2.publish(msg2)

        self.count += 1

def main(args=None):
    rclpy.init(args=args)
    node = MPub()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()