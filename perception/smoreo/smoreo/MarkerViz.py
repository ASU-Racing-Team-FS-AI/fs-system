"""
Class MarkerViz for visualizing cones using ROS markers
"""
from typing import List
import rclpy
from visualization_msgs.msg import Marker, MarkerArray

from asurt_msgs.msg import Landmark, LandmarkArray

class MarkerViz:
    """
    Class for visualizing cones using ROS markers
    """

    def __init__(self, coneRadius: float, coneHeight: float, zShift: float = 0):
        self.coneRadius = coneRadius
        self.coneHeight = coneHeight
        self.zShift = zShift
        self.counter = 0

    def createDeleteMsg(self, frameId: str) -> Marker:
        """
        Creates a delete message that clears all the current visualized markers.

        Parameters
        ----------
        frameId : str
            Frame id of the message

        Returns
        -------
        Marker
            The created Marker message to clear all visualized markers
        """
        delMsg = Marker()
        delMsg.header.frame_id = frameId
        delMsg.header.stamp = rclpy.time.Time()
        delMsg.type = Marker.CUBE
        delMsg.action = Marker.DELETEALL
        return delMsg

    def getConeColor(self, coneType: int) -> List[int]:
        """
        Fetches the color of a cone based on its type.

        Parameters
        ----------
        coneType : int
            Cone type according to definition in asurt_msgs/Landmark.msg

        Returns
        -------
        List[int]
            List containing the RGB values of the cone color

        Raises
        ------
        ValueError
            If the cone type is unknown
        """
        if coneType == Landmark.BLUE_CONE:
            return [0, 0, 255]
        if coneType == Landmark.YELLOW_CONE:
            return [255, 255, 0]
        if coneType in [Landmark.ORANGE_CONE, Landmark.LARGE_CONE]:
            return [255, 0, 0]
        if coneType == Landmark.CONE_TYPE_UNKNOWN:
            return [0, 0, 0]
        raise ValueError(f"Unknown cone type: {coneType}")

    def coneToMarker(self, landmark: Landmark, frameId: str, idx: int) -> Marker:
        """
        Creates a Marker message for a cone.

        Parameters
        ----------
        landmark : Landmark
            Cone to create a marker for
        frameId : str
            Frame id of the message
        idx : int
            Index to add for the marker (unique for each cone at a given time)

        Returns
        -------
        Marker
            The created Marker message for the cone
        """
        msg = Marker()
        msg.header.frame_id = frameId
        msg.header.stamp = rclpy.time.Time()
        msg.ns = str(self.counter)
        msg.id = idx
        msg.type = Marker.CUBE
        msg.action = Marker.ADD

        # Cone position
        msg.pose.position.x = landmark.position.x
        msg.pose.position.y = landmark.position.y
        msg.pose.position.z = self.zShift
        msg.pose.orientation.x = 0
        msg.pose.orientation.y = 0
        msg.pose.orientation.z = 0
        msg.pose.orientation.w = 1

        # Cone size
        msg.scale.x = self.coneRadius * 2
        msg.scale.y = self.coneRadius * 2
        msg.scale.z = self.coneHeight

        # Set marker color
        color = self.getConeColor(landmark.type)
        msg.color.r = color[0]
        msg.color.g = color[1]
        msg.color.b = color[2]
        msg.color.a = 0.75
        return msg

    def conesToMarkers(self, landmarks: LandmarkArray) -> MarkerArray:
        """
        Creates a MarkerArray message for a LandmarkArray message

        Parameters
        ----------
        landmarks : LandmarkArray
            LandmarkArray message to create a MarkerArray message for

        Returns
        -------
        MarkerArray
            The created MarkerArray message for the LandmarkArray message
        """
        frameId = landmarks.header.frame_id
        markers = [self.createDeleteMsg(frameId)]
        self.counter += 1

        for idx, landmark in enumerate(landmarks.landmarks):
            markers.append(self.coneToMarker(landmark, frameId, idx))

        msg = MarkerArray()
        msg.markers = markers
        return msg