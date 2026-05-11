from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_file = LaunchConfiguration('map')

    return LaunchDescription([
        DeclareLaunchArgument('params_file', default_value='/workspace/nav2_params.yaml'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('map', default_value='/workspace/maps/map.yaml'),

        # ── LOCALIZATION ──
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time, 'yaml_filename': map_file}],
        ),
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}],
        ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[
                {'use_sim_time': use_sim_time},
                {'autostart': True},
                {'node_names': ['map_server', 'amcl']},
            ],
        ),

        # ── NAVIGATION (delayed to let AMCL publish map→odom first) ──
        TimerAction(period=40.0, actions=[
            Node(
                package='nav2_controller',
                executable='controller_server',
                output='screen',
                parameters=[params_file, {'use_sim_time': use_sim_time}],
            ),
            Node(
                package='nav2_smoother',
                executable='smoother_server',
                output='screen',
                parameters=[params_file, {'use_sim_time': use_sim_time}],
            ),
            Node(
                package='nav2_planner',
                executable='planner_server',
                name='planner_server',
                output='screen',
                parameters=[params_file, {'use_sim_time': use_sim_time}],
            ),
            Node(
                package='nav2_behaviors',
                executable='behavior_server',
                name='behavior_server',
                output='screen',
                parameters=[params_file, {'use_sim_time': use_sim_time}],
            ),
            Node(
                package='nav2_bt_navigator',
                executable='bt_navigator',
                name='bt_navigator',
                output='screen',
                parameters=[params_file, {'use_sim_time': use_sim_time}],
            ),
            Node(
                package='nav2_waypoint_follower',
                executable='waypoint_follower',
                name='waypoint_follower',
                output='screen',
                parameters=[params_file, {'use_sim_time': use_sim_time}],
            ),
            Node(
                package='nav2_velocity_smoother',
                executable='velocity_smoother',
                name='velocity_smoother',
                output='screen',
                parameters=[params_file, {'use_sim_time': use_sim_time}],
            ),
            Node(
                package='nav2_collision_monitor',
                executable='collision_monitor',
                name='collision_monitor',
                output='screen',
                parameters=[params_file, {'use_sim_time': use_sim_time}],
            ),
            Node(
                package='nav2_lifecycle_manager',
                executable='lifecycle_manager',
                name='lifecycle_manager_navigation',
                output='screen',
                parameters=[
                    {'use_sim_time': use_sim_time},
                    {'autostart': True},
                    {'node_names': [
                        'controller_server', 'smoother_server', 'planner_server',
                        'behavior_server', 'bt_navigator', 'waypoint_follower',
                        'velocity_smoother', 'collision_monitor',
                    ]},
                ],
            ),
        ]),
    ])
