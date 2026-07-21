import rclpy
from rclpy.node import Node
from std_msgs.msg import Header

class TPub(Node):
    def __init__(self):
        super().__init__('tpub')
        self.pub = self.create_publisher(Header, 'time', 10)
        self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        msg = Header()
        msg.stamp = self.get_clock().now().to_msg()
        msg.frame_id = 'time_frame'
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = TPub()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()