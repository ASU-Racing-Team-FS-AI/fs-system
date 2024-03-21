#!/usr/bin/env python3

import rclpy
from std_msgs.msg import Bool
from asurt_msgs.msg import RoadState
from tf_helper.src.tf_helper.StatusPublisher import StatusPublisher

ROAD_STATE = RoadState()


def roadStateCallback(msg: RoadState) -> None:
    """
    Callback to retrieve the road state
    """
    global ROAD_STATE  # pylint: disable=global-statement
    ROAD_STATE = msg


def main() -> None:
    """
    track drive
    """

    global ROAD_STATE  # pylint: disable=global-statement, global-variable-not-assigned
    rclpy.init()
    node = rclpy.create_node("autocross_finisher")

    is_finished_topic = node.get_parameter("/finisher/is_finished").get_parameter_value().string_value
    road_state_topic = node.get_parameter("/slam/road_state").get_parameter_value().string_value

    is_finish_pub = node.create_publisher(Bool, is_finished_topic, 10)

    node.create_subscription(RoadState, road_state_topic, roadStateCallback, 10)

    status = StatusPublisher("/status/autocross")
    status.starting()
    status.ready()

    rate = node.create_rate(10)

    try:
        while rclpy.ok():
            status.running()
            if ROAD_STATE.laps >= 1:
                is_finish_pub.publish(True)

            rate.sleep()

    except KeyboardInterrupt:
        pass

    finally:
        rclpy.shutdown()


if __name__ == "__main__":
    ROAD_STATE = RoadState()
    main()
