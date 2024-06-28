# pylint: disable-all
# mypy: ignore-errors
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from os.path import expanduser


def generate_launch_description():

    # Configure environment

    # Simulated time
    use_sim_time = LaunchConfiguration("use_sim_time", default="false")

    config = os.path.join(get_package_share_directory("yolo"), "config", "yolo_parameters.yaml")

    yolo_node = Node(
        package="yolo",
        executable="yolo_node",
        output="screen",
        parameters=[config],
    )

    ld = LaunchDescription()

    # Add node
    ld.add_action(yolo_node)

    return ld
