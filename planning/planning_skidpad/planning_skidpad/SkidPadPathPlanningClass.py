"""Module providing a function printing python version."""

from typing import Tuple
from typing import Dict, Any
import math
import numpy as np
from nav_msgs.msg import Odometry


class SendPath:
    """
    Class for generating a path for the skidpad.

    Attributes:
        state (Odometry): The current state of the vehicle.
        count (int): The number of orange nodes passed.
        pastPos (np.array): The previous position of the vehicle.
        origin (np.array): The origin of the path.
        threshold (float): The maximum distance between points to merge.
        flag (int): A flag to check if the origin has been set.
        reduisMean (float): The mean radius of the circles.
    """

    def __init__(self) -> None:
        self.state = Odometry()
        self.count = 0
        self.pastPos = np.empty(2)
        self.origin = np.array([0, 0])
        self.threshold = 0.2
        self.flag = 0
        self.reduisMean = 0.0

    def mergePoints(
        self,
        points: np.ndarray[np.float_, Any],
        threshold: float,
    ) -> np.ndarray[np.float_, Any]:
        """
        Merges points that are close to each other based on a given threshold,
        considering the maximum repeated color.

        Args:
            points (np.ndarray): Array of points.
            threshold (float): Maximum distance between points to merge.

        Returns:
            np.ndarray: Merged array of points.
        """
        num = len(points)

        # Create a boolean array to keep track of merged points
        merged = np.zeros(num, dtype=bool)

        # Initialize merged points array with zeros
        mergedPoints: np.ndarray[np.float_, Any] = np.zeros(
            (0, points.shape[1]), dtype=points.dtype
        )

        # Create a dictionary to count the occurrences of each color
        colorCounts: Dict[int, int] = {}

        # Iterate over each point
        for i in range(num):
            # Skip if the current point has already been merged
            if merged[i]:
                continue

            # Add the current point to the merged points array
            mergedPoints = np.vstack((mergedPoints, points[i]))

            # Get the color of the current point
            color = points[i, 2]

            # Reset the color counts dictionary
            colorCounts.clear()

            # Count the occurrences of the current color
            colorCounts[color] = 1

            # Compare the current point with the remaining points
            for j in range(i + 1, num):
                # Skip if the point has already been merged
                if merged[j]:
                    continue

                # Calculate the Euclidean distance between the points
                distance = np.linalg.norm(
                    np.array([points[i, 0], points[i, 1]]) - np.array([points[j, 0], points[j, 1]])
                )

                # Merge the points if they are close enough
                if distance <= threshold:
                    merged[j] = True
                    # Update the color counts
                    color = max(color, points[j, 2])
                    colorCounts[points[j, 2]] = colorCounts.get(points[j, 2], 0) + 1

            # Update the color of the merged point with the maximum repeated color
            mergedPoints[-1, 2] = max(colorCounts, key=lambda x: colorCounts[x])

        return mergedPoints

    def conesClassification(
        self, cones: np.ndarray[np.float_, Any]
    ) -> Tuple[
        np.ndarray[np.float_, Any],
        np.ndarray[np.float_, Any],
        np.ndarray[np.float_, Any],
        np.ndarray[np.float_, Any],
        np.ndarray[np.float_, Any],
        np.ndarray[np.float_, Any],
        np.ndarray[np.float_, Any],
    ]:
        """
        Classifies cones based on their position relative to the robot's pose.

        Returns:
            Tuple: A tuple containing the classified cones arrays in the following order:
            - rightBlueCones: Array of blue cones on the right side of the robot.
            - leftBlueCones: Array of blue cones on the left side of the robot.
            - rightYellowCones: Array of yellow cones on the right side of the robot.
            - leftYellowCones: Array of yellow cones on the left side of the robot.
            - orangeCones: Array of orange cones.
            - bigOrange: Array of large orange cones.
            - unknownCones: Array of unknown cones.
        """
        # filter_outliers cones based on position and color
        rightBlueCones: np.ndarray[np.float_, Any] = np.array(
            cones[cones[:, 2] == 0][cones[cones[:, 2] == 0][:, 0] > 0]
        )
        leftBlueCones: np.ndarray[np.float_, Any] = np.array(
            cones[cones[:, 2] == 0][cones[cones[:, 2] == 0][:, 0] <= 0]
        )
        rightYellowCones: np.ndarray[np.float_, Any] = np.array(
            cones[cones[:, 2] == 1][cones[cones[:, 2] == 1][:, 0] > 0]
        )
        leftYellowCones: np.ndarray[np.float_, Any] = np.array(
            cones[cones[:, 2] == 1][cones[cones[:, 2] == 1][:, 0] <= 0]
        )
        orangeCones: np.ndarray[np.float_, Any] = np.array(cones[cones[:, 2] == 2])
        bigOrange: np.ndarray[np.float_, Any] = np.array(cones[cones[:, 2] == 3])
        unknownCones: np.ndarray[np.float_, Any] = np.array(cones[cones[:, 2] == 4])

        # Sort cones based on distance from robot's pose
        rightBlueCones = rightBlueCones[
            np.argsort(
                (rightBlueCones[:, 0] - self.state.pose.pose.position.x) ** 2
                + (rightBlueCones[:, 1] - self.state.pose.pose.position.y) ** 2
            )
        ]
        leftBlueCones = leftBlueCones[
            np.argsort(
                (leftBlueCones[:, 0] - self.state.pose.pose.position.x) ** 2
                + (leftBlueCones[:, 1] - self.state.pose.pose.position.y) ** 2
            )
        ]
        rightYellowCones = rightYellowCones[
            np.argsort(
                (rightYellowCones[:, 0] - self.state.pose.pose.position.x) ** 2
                + (rightYellowCones[:, 1] - self.state.pose.pose.position.y) ** 2
            )
        ]
        leftYellowCones = leftYellowCones[
            np.argsort(
                (leftYellowCones[:, 0] - self.state.pose.pose.position.x) ** 2
                + (leftYellowCones[:, 1] - self.state.pose.pose.position.y) ** 2
            )
        ]
        orangeCones = orangeCones[
            np.argsort(
                (orangeCones[:, 0] - self.state.pose.pose.position.x) ** 2
                + (orangeCones[:, 1] - self.state.pose.pose.position.y) ** 2
            )
        ]
        bigOrange = bigOrange[
            np.argsort(
                (bigOrange[:, 0] - self.state.pose.pose.position.x) ** 2
                + (bigOrange[:, 1] - self.state.pose.pose.position.y) ** 2
            )
        ]
        unknownCones = unknownCones[
            np.argsort(
                (unknownCones[:, 0] - self.state.pose.pose.position.x) ** 2
                + (unknownCones[:, 1] - self.state.pose.pose.position.y) ** 2
            )
        ]

        return (
            rightBlueCones,
            leftBlueCones,
            rightYellowCones,
            leftYellowCones,
            orangeCones,
            bigOrange,
            unknownCones,
        )

    def findOrangeNodes(
        self, orangeConesMap: np.ndarray[np.float_, Any]
    ) -> np.ndarray[np.float_, Any]:
        """
        Finds orange nodes based on specific conditions from the given orange cones map.

        Args:
            orangeConesMap (numpy.ndarray): Array containing nodes information.

        Returns:
            numpy.ndarray: Array of orange nodes that satisfy the conditions.
        """
        # Initialize an empty array to store orange nodes
        orangeNodes: np.ndarray[np.float_, Any] = np.zeros((0, 3))

        for cone1 in orangeConesMap:
            lowestDist = float("inf")
            nearestCone = np.zeros((0,))

            # Find the nearest cone to the current cone
            for cone2 in orangeConesMap:
                if not np.array_equal(cone1, cone2) and cone1[0] * cone2[0] < 0:
                    dist = math.sqrt((cone1[0] - cone2[0]) ** 2 + (cone1[1] - cone2[1]) ** 2)
                    if dist < lowestDist:
                        lowestDist = dist
                        nearestCone = cone2
            # Calculate the average position between the current cone and the nearest cone
            if not np.array_equal(nearestCone, np.zeros((0,))):
                avgX = round((cone1[0] + nearestCone[0]) / 2, 2)
                avgY = round((cone1[1] + nearestCone[1]) / 2, 2)
                newNode = np.array([[avgX, avgY, cone1[2]]])

                # Add the new node to the orange nodes array if it does not already exist
                if not np.any(np.all(orangeNodes[:, :2] == newNode[:, :2], axis=1)):
                    orangeNodes = np.concatenate((orangeNodes, newNode), axis=0)
        return orangeNodes

    def dist(self, seta1: float, seta2: float) -> float:
        """
        Calculates the distance between two angles.

        Args:
            seta1 (float): First angle.
            seta2 (float): Second angle.

        Returns:
            float: Distance between the two angles.
        """
        return abs(seta1 - seta2)

    def linePath(
        self, orangeNodes: np.ndarray[np.float_, Any], pos: np.ndarray[np.float_, Any]
    ) -> np.ndarray[np.float_, Any]:
        """
        Generates a line path based on orange nodes and a given position.

        Args:
            orangeNodes (np.ndarray): Array of orange nodes.
            pos (list): Current position.

        Returns:
            np.ndarray: Array representing the line path.
        """
        # Initialize variables
        if self.origin[1] != 0:
            x = np.append(orangeNodes[:, 0], self.origin[0])
            y = np.append(orangeNodes[:, 1], self.origin[1])
        else:
            x = orangeNodes[:, 0]
            y = orangeNodes[:, 1]
        noNeedIndex = np.array([], dtype=int)
        path: np.ndarray[np.float_, Any] = np.zeros((0, 2))

        # Check if there are no orange nodes
        if orangeNodes.shape[0] < 1:
            return path

        # filter_outliers orange nodes based on position
        for i in range(len(orangeNodes)):
            if orangeNodes[i, 1] < pos[1]:
                noNeedIndex = np.append(noNeedIndex, i)
        noNeedIndex = np.flip(noNeedIndex)
        orangeNodes = np.delete(orangeNodes, noNeedIndex, axis=0)

        # Generate the path
        try:
            matrix = np.c_[x, np.ones_like(x)]
            slope, const = np.linalg.solve(matrix.T @ matrix, matrix.T @ y)
        except np.linalg.LinAlgError:
            slope = 0
            const = 0

        # Find the end point of the path
        if self.count < 4 and self.origin[1] != 0:
            y = np.linspace(
                float(pos[1]), self.origin[1], int(abs(pos[1] - self.origin[1]) + 1) * 5
            )
        elif self.count < 4:
            y = np.linspace(
                float(pos[1]), float(pos[1]) + 5, int(abs(pos[1] - (float(pos[1]) + 5)) + 1) * 5
            )
        else:
            end = orangeNodes[:, 1].max()
            y = np.linspace(float(pos[1]), end, int(abs(pos[1] - end) + 1) * 10)

        if round(slope, 1) != 0.0:
            path = np.column_stack(((y - const) / slope, y))
        else:
            path = np.column_stack((np.full_like(y, pos[0]), y))

        return path

    def fitCircle(self, points: np.ndarray[np.float_, Any]) -> Tuple[float, float, float]:
        """
        Fits a circle to the given points using a least squares method.

        Args:
            points (np.ndarray): Array of points.

        Returns:
            Tuple[float, float, float]:
            x-coordinate of the center, y-coordinate of the center, and radius of the circle.
        """
        # Fit a circle to the given points
        matrix = np.c_[-2 * points[:, 0], -2 * points[:, 1], np.ones_like(points[:, 0])]
        # Solve the linear system of equations
        xRightCenter, yRightCenter, const = np.linalg.solve(
            matrix.T @ matrix, matrix.T @ (-points[:, 0] ** 2 - points[:, 1] ** 2)
        )
        # Calculate the radius of the circle
        raduis = np.sqrt(xRightCenter**2 + yRightCenter**2 - const)

        # get deviation of each point from the circle
        for point in points:
            deviation = (
                math.sqrt((point[0] - xRightCenter) ** 2 + (point[1] - yRightCenter) ** 2) - raduis
            )
            if deviation > self.threshold:
                points = np.delete(points, np.where((points == point).all(axis=1)), axis=0)
                xRightCenter, yRightCenter, raduis = self.fitCircle(points)

        return xRightCenter, yRightCenter, raduis

    def rightCirclePath(
        self,
        innerCones: np.ndarray[np.float_, Any],
        pos: np.ndarray[np.float_, Any] = np.array([0, 0]),
    ) -> np.ndarray[np.float_, Any]:
        """
        Generates a circular path based inner cones.

        Args:
            innerCones (np.ndarray): Array of inner cones.
            pos (np.ndarray, optional): Position array. Defaults to np.array([0, 0]).

        Returns:
            np.ndarray: Circular path represented by an array of points.
        """
        # Initialize variables
        path: np.ndarray[np.float_, Any] = np.empty((0, 2))
        xPath = np.empty(0)
        yPath1 = np.empty(0)
        yPath2 = np.empty(0)

        # Calculate the mean circle
        xCenter, yCenter, meanReduis = self.fitCircle(innerCones)
        meanReduis = math.sqrt((xCenter - self.origin[0]) ** 2 + (yCenter - self.origin[1]) ** 2)
        if np.array_equal(pos, [0, 0]):
            pos = np.array([xCenter - meanReduis, yCenter])
        # Calculate the start angle
        if round((pos[0] - xCenter), 3) == 0:
            if pos[1] > yCenter:
                start = math.pi / 2
            else:
                start = -math.pi / 2
        else:
            start = math.atan(round((pos[1] - yCenter) / (pos[0] - xCenter), 3))

        # Generate the circular path
        if round((pos[0] - xCenter), 3) < 0 and round((pos[1] - yCenter), 3) < 0:
            start = start - math.pi
        elif round((pos[0] - xCenter), 3) < 0:
            if round((pos[1] - yCenter), 3) >= 0:
                start = start + math.pi

        seta = np.linspace(start, -math.pi, int(self.dist(start, -math.pi) + 1) * 5)
        for i in seta:
            xPath = np.append(xPath, meanReduis * np.cos(i) + xCenter)
            if i < 0:
                yPath2 = np.append(
                    yPath2,
                    -math.sqrt(round(meanReduis**2 - (xPath[-1] - xCenter) ** 2, 3)) + yCenter,
                )
            else:
                yPath1 = np.append(
                    yPath1,
                    math.sqrt(round(meanReduis**2 - (xPath[-1] - xCenter) ** 2, 3)) + yCenter,
                )
        path = np.vstack(
            (
                np.column_stack((xPath[: len(yPath1)], yPath1)),
                np.column_stack((xPath[len(yPath1) :], yPath2)),
            )
        )
        return path

    def leftCirclePath(
        self,
        innerCones: np.ndarray[np.float_, Any],
        pos: np.ndarray[np.float_, Any] = np.array([0, 0]),
    ) -> np.ndarray[np.float_, Any]:
        """
        Generates a circular path based inner cones.

        Args:
            innerCones (np.ndarray): Array of inner cones.
            pos (np.ndarray, optional): Position array. Defaults to np.array([0, 0]).

        Returns:
            np.ndarray: Circular path represented by an array of points.
        """
        # Initialize variables
        path: np.ndarray[np.float_, Any] = np.empty((0, 2))
        xPath = np.empty(0)
        yPath1 = np.empty(0)
        yPath2 = np.empty(0)

        # Calculate the mean circle
        xCenter, yCenter, meanReduis = self.fitCircle(innerCones)
        meanReduis = math.sqrt((xCenter - self.origin[0]) ** 2 + (yCenter - self.origin[1]) ** 2)
        if np.array_equal(pos, [0, 0]):
            pos = np.array([xCenter + meanReduis, yCenter])
        # Calculate the start angle
        if round((pos[0] - xCenter), 3) == 0:
            if pos[1] > yCenter:
                start = math.pi / 2
            else:
                start = -math.pi / 2
        else:
            start = math.atan(round((pos[1] - yCenter) / (pos[0] - xCenter), 3))

        # Generate the circular path
        if start < 0:
            start = start + 2 * math.pi
        if round((pos[0] - xCenter), 3) < 0 and round((pos[1] - yCenter), 3) < 0:
            start = start + math.pi
        elif round((pos[0] - xCenter), 3) < 0:
            if round((pos[1] - yCenter), 3) >= 0:
                start = start - math.pi

        seta = np.linspace(start, 2 * math.pi, int(self.dist(start, 2 * math.pi) + 1) * 5)
        for i in seta:
            xPath = np.append(xPath, meanReduis * np.cos(i) + xCenter)
            if i > math.pi:
                yPath2 = np.append(
                    yPath2,
                    -math.sqrt(round(meanReduis**2 - (xPath[-1] - xCenter) ** 2, 3)) + yCenter,
                )
            else:
                yPath1 = np.append(
                    yPath1,
                    math.sqrt(round(meanReduis**2 - (xPath[-1] - xCenter) ** 2, 3)) + yCenter,
                )
        path = np.vstack(
            (
                np.column_stack((xPath[: len(yPath1)], yPath1)),
                np.column_stack((xPath[len(yPath1) :], yPath2)),
            )
        )
        return path

    def counter(self, pos: np.ndarray[np.float_, Any]) -> None:
        """
        Counts the number of orange nodes passed in and updates internal state.

        Args:
            pos (np.array): Current position [x, y].
            bigOrange (np.array): Array of big orange nodes.

        Returns:
            None
        """
        # Check if the robot has passed an orange node and update the counter and origin
        if np.array_equal(self.origin, np.array([0, 0])):
            return None
        # Check if the robot has passed origin
        if (pos[1] > self.origin[1]) and (self.pastPos[1] < self.origin[1]):
            if round(pos[0], 0) < round(self.origin[0] + 1, 0) and round(pos[0], 0) > round(
                self.origin[0] - 1, 0
            ):
                self.count += 1
        return None

    def getOrigin(
        self,
        bigOrange: np.ndarray[np.float_, Any],
        leftBlueCones: np.ndarray[np.float_, Any],
        rightYellowCones: np.ndarray[np.float_, Any],
    ) -> None:
        """
        Gets the origin based on the given cones.

        Args:
            bigOrange (np.ndarray): Array of big orange cones.
            leftBlueCones (np.ndarray): Array of left blue cones.
            rightYellowCones (np.ndarray): Array of right yellow cones.

        Returns:
            None
        """
        xRightCenter = 0.0
        yRightCenter = 0.0
        xLeftCenter = 0.0
        yLeftCenter = 0.0
        counterOrangeNodes = self.findOrangeNodes(bigOrange)
        if len(counterOrangeNodes) == 2:
            self.origin = np.array(
                [
                    (counterOrangeNodes[0][0] + counterOrangeNodes[1][0]) / 2,
                    (counterOrangeNodes[0][1] + counterOrangeNodes[1][1]) / 2,
                ]
            )
            self.flag = 1
        elif len(leftBlueCones) >= 3 and len(rightYellowCones) >= 3 and self.flag == 0:
            xRightCenter, yRightCenter, _ = self.fitCircle(rightYellowCones)
            xLeftCenter, yLeftCenter, _ = self.fitCircle(leftBlueCones)
            self.origin = np.array(
                [
                    (xRightCenter + xLeftCenter) / 2,
                    (yRightCenter + yLeftCenter) / 2,
                ]
            )
            self.reduisMean = math.sqrt(
                (xRightCenter - self.origin[0]) ** 2 + (yRightCenter - self.origin[1]) ** 2
            )

    def classifyPoints(
        self, colorPoints: np.ndarray[np.float_, Any], unknownPoints: np.ndarray[np.float_, Any]
    ) -> np.ndarray[np.float_, Any]:
        """
        Classifies unknown points as inside
        or outside of a given circle based on the center and radius.

        Args:
            colorPoints:
            np.ndarray representing points with known color, including the color value.
            unknown_points: np.ndarray representing points with unknown color.

        Returns:
            np.ndarray: Array of classified points.
        """

        classifiedPoints: np.ndarray[np.float_, Any] = colorPoints
        xRightCenter, yRightCenter, radius = self.fitCircle(colorPoints)
        for point in unknownPoints:
            x, y = point[0], point[1]
            distance = math.sqrt((x - xRightCenter) ** 2 + (y - yRightCenter) ** 2)
            if abs(distance - radius) <= self.threshold:
                classifiedPoints = np.append(classifiedPoints, [[x, y, colorPoints[0, 2]]], axis=0)
        return classifiedPoints

    def path(
        self,
        leftBlueCones: np.ndarray[np.float_, Any],
        rightYellowCones: np.ndarray[np.float_, Any],
        orangeCones: np.ndarray[np.float_, Any],
        bigOrange: np.ndarray[np.float_, Any],
    ) -> np.ndarray[np.float_, Any]:
        """
        Generates a path based on the given cones and current state.

        Args:
            rightBlueCones (np.array): Right blue cones.
            leftBlueCones (np.array): Left blue cones.
            rightYellowCones (np.array): Right yellow cones.
            leftYellowCones (np.array): Left yellow cones.
            orangeCones (np.array): Orange cones.
            bigOrange (np.array): Big orange cones.
            unknownCones (np.array): Unknown cones.

        Returns:
            np.array: Generated path as a NumPy array.
        """
        # Initialize variables
        path: np.ndarray[np.float_, Any] = np.empty((0, 2))  # Initialize an empty NumPy array
        # Get the current position
        pos = np.array([self.state.pose.pose.position.x, self.state.pose.pose.position.y])
        # sum all orange cones(big and small)
        orange = np.concatenate((orangeCones, bigOrange), axis=0)
        # Sort orange cones based on distance from robot's pose
        orange = orange[np.lexsort(((orange[:, 1] - pos[1]) ** 2 + (orange[:, 0] - pos[0]) ** 2,))]
        # Find orange nodes
        orangeNodes = self.findOrangeNodes(orange)
        # update the counter if there are more than 2 big orange cones
        if len(bigOrange) > 2:
            self.counter(pos)
        # Get the origin if it is not set
        if np.array_equal(self.origin, np.array([0, 0])):
            self.getOrigin(bigOrange, leftBlueCones, rightYellowCones)
        # Generate the path based on the current count
        if self.count < 1:
            path = self.linePath(orangeNodes, pos)
            if len(rightYellowCones) >= 3:
                path = np.concatenate((path, self.rightCirclePath(rightYellowCones)), axis=0)
        elif self.count < 2:
            path = self.rightCirclePath(rightYellowCones, pos)
            path = np.concatenate((path, self.rightCirclePath(rightYellowCones)), axis=0)
        elif self.count < 3:
            path = self.rightCirclePath(rightYellowCones, pos)
            if len(leftBlueCones) >= 3:
                path = np.concatenate((path, self.leftCirclePath(leftBlueCones)), axis=0)
        elif self.count < 4:
            path = self.leftCirclePath(leftBlueCones, pos)
            path = np.concatenate((path, self.leftCirclePath(leftBlueCones)), axis=0)
        elif self.count < 5:
            path = self.leftCirclePath(leftBlueCones, pos)
            if len(orangeNodes) > 0 and pos[1] < self.origin[1]:
                path = np.concatenate((path, self.linePath(orangeNodes, path[-1])), axis=0)
        elif self.count >= 5:
            path = np.concatenate((path, self.linePath(orangeNodes, pos)), axis=0)
        return path

    def orangeFilter(self, orangeCones: np.ndarray[np.float_, Any]) -> np.ndarray[np.float_, Any]:
        """
        Filters out the orange cones that are outside the track.

        Args:
            orangeCones (np.ndarray): Array of orange cones.

        Returns:
            np.ndarray: Filtered array of orange cones.
        """
        for cone in orangeCones:
            if cone[0] < -1.7:
                orangeCones = np.delete(
                    orangeCones, np.where((orangeCones == cone).all(axis=1)), axis=0
                )
            elif cone[0] > 1.7:
                orangeCones = np.delete(
                    orangeCones, np.where((orangeCones == cone).all(axis=1)), axis=0
                )
        # rightOrangeCones = np.array(orangeCones[orangeCones[:, 0] > 0])
        # leftOrangeCones = np.array(orangeCones[orangeCones[:, 0] <= 0])
        return orangeCones

    def getPath(
        self, state: Odometry, cones: np.ndarray[np.float_, Any]
    ) -> Tuple[np.ndarray[np.float_, Any], np.ndarray[np.float_, Any]]:
        """
        Generates a path based on the given cones and current state.

        Args:
            state (Odometry): Current state.
            cones (np.ndarray): Array of cones.

        Returns:
            Tuple[np.ndarray, np.ndarray]:
              Generated path as a NumPy array and the merged cones array.
        """
        # Store the previous position if the current state is not None
        if self.state is not None:
            self.pastPos = np.array(
                [self.state.pose.pose.position.x, self.state.pose.pose.position.y]
            )
        self.state = state

        # Merge cones that are close to each other
        if len(cones) > 300:
            returnCones = self.mergePoints(cones, self.threshold)
            cones = returnCones
        else:
            returnCones = cones
            cones = self.mergePoints(cones, self.threshold)
        # initialize variables
        rightBlueCones = np.empty((0, 3))
        leftBlueCones = np.empty((0, 3))
        rightYellowCones = np.empty((0, 3))
        leftYellowCones = np.empty((0, 3))
        orangeCones = np.empty((0, 3))
        bigOrange = np.empty((0, 3))
        unknownCones = np.empty((0, 3))
        # Classify cones based on their position and color
        (
            rightBlueCones,
            leftBlueCones,
            rightYellowCones,
            leftYellowCones,
            orangeCones,
            bigOrange,
            unknownCones,
        ) = self.conesClassification(cones)

        # Filter out the orange cones
        orangeCones = self.orangeFilter(np.concatenate((orangeCones, bigOrange), axis=0))
        # Classify unknown cones based on the known cones
        if len(rightBlueCones) >= 3:
            rightBlueCones = self.classifyPoints(rightBlueCones, unknownCones)
        if len(leftBlueCones) >= 3:
            leftBlueCones = self.classifyPoints(leftBlueCones, unknownCones)
        if len(rightYellowCones) >= 3:
            rightYellowCones = self.classifyPoints(rightYellowCones, unknownCones)
        if len(leftYellowCones) >= 3:
            leftYellowCones = self.classifyPoints(leftYellowCones, unknownCones)

        # Generate the path
        path = self.path(leftBlueCones, rightYellowCones, orangeCones, bigOrange)
        return path, returnCones
