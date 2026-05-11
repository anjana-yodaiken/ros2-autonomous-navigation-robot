from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_robot',
            executable='serial_bridge',
            name='serial_bridge',
        ),
        Node(
            package='my_robot',
            executable='odometry_node',
            name='odometry_node',
        ),
        Node(
            package='rplidar_ros',
            executable='rplidar_composition',
            name='rplidar',
            parameters=[{
                'serial_port': '/dev/ttyUSB0',
                'serial_baudrate': 115200,
                'frame_id': 'laser',
                'angle_compensate': True,
            }],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_base_to_laser',
            arguments=['0.014', '0.0', '0.190', '0', '0', '0', 'base_link', 'laser'],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_base_to_imu',
            arguments=['0.072', '-0.029', '0.107', '0', '0', '0', 'base_link', 'imu'],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_base_to_footprint',
            arguments=['0.0', '0.0', '-0.0345', '0', '0', '0', 'base_link', 'base_footprint'],
        ),
    ])
