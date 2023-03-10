import launch
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            # Publish /joy messages from connected joystick controller
            Node(
                name="joy_node",
                package="joy",
                executable="joy_node",
                output="screen",
                parameters=[{
                    'dev_name': 'wireless_controller',
                    'deadzone': 0.3,
                    'autorepeat_rate': 20.0,
            }]),
            # # Convert /joy message to /cmd_vel message and publish
            # Node(
            #     name='teleop_twist_joy_node',
            #     package='teleop_twist_joy',
            #     executable='teleop_node',
            #     parameters=[{
            #         'axis_linear.x': 1,
            #         'axis_angular.yaw': 0,
            #         'scale_linear.x': 1.0,
            #         'scale_angular.yaw': 1.0,
            #         'enable_button': 0,
            #         'require_enable_button': False,
            #     }]),
            Node(
                name="robot_arm",
                package="robot_arm",
                executable="robot_arm_node",
                # parameters=[{"base_width": 0.175}],
                output="screen",
            ),
        ]
    )
