from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(package="gong_basic", executable="mpub", name="mpub"),
            Node(package="gong_basic", executable="tpub", name="tpub"),
            Node(package="gong_basic", executable="msub", name="msub"),
            Node(package="gong_basic", executable="m2sub", name="m2sub"),  # 👈 이 줄이 빠져있거나 오타가 있는지 확인!
            Node(package="gong_basic", executable="mtsub", name="mtsub"),
        ]
    )