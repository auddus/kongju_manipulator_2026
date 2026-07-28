"""OpenManipulator-X MoveItPy arm·gripper 실습 launch."""

from pathlib import Path

from launch import LaunchDescription
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description() -> LaunchDescription:
    """MoveIt 설정 전체를 실습 노드에 전달한다."""
    moveit_config = (
        MoveItConfigsBuilder(
            robot_name='open_manipulator_x',
            package_name='open_manipulator_moveit_config',
        )
        .robot_description_semantic(
            str(
                Path('config')
                / 'open_manipulator_x'
                / 'open_manipulator_x.srdf'
            )
        )
        .joint_limits(
            str(
                Path('config')
                / 'open_manipulator_x'
                / 'joint_limits.yaml'
            )
        )
        .trajectory_execution(
            str(
                Path('config')
                / 'open_manipulator_x'
                / 'moveit_controllers.yaml'
            )
        )
        .robot_description_kinematics(
            str(
                Path('config')
                / 'open_manipulator_x'
                / 'kinematics.yaml'
            )
        )
        .to_moveit_configs()
    )

    urdf_xacro = PathJoinSubstitution(
        [
            FindPackageShare('open_manipulator_description'),
            'urdf',
            'open_manipulator_x',
            'open_manipulator_x.urdf.xacro',
        ]
    )
    robot_description = {
        'robot_description': ParameterValue(
            Command(['xacro ', urdf_xacro]),
            value_type=str,
        )
    }

    moveit_py_node = Node(
        package='tf2_basic',
        executable='moveit_test',
        name='open_manipulator_moveit_py',
        output='screen',
        parameters=[
            moveit_config.to_dict(),
            robot_description,
        ],
    )
    return LaunchDescription([moveit_py_node])