import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from nav_msgs.msg import Odometry, Path
import math
from tf_transformations import euler_from_quaternion

# node file , purepursuit file
# launch file with parameters
# search index function
# pkg folder structure

class AdaptivePurePursuit:
    def __init__(self):
        #state_callback function initialization
        self.velocity = 0.0
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.target_speed = 0.0
        self.prev_error = 0.0
        self.error_sum = 0.0
        #path_callback function initialization
        self.waypoints = []
        self.pathFlag = False


        #pid_controller function initialization
        #From launch file
        self.kp = rclpy.Node.get_parameter_value('/control/kp')
        self.ki = 1.0
        self.kd = 0.5
        self.dt = 0.1
        self.lookahead_distance = 4.2
        self.lookaheadconstant = 2.0
        self.gain = 0.3
        self.minspeed = 0.5
        self.maxspeed = 3.5

       
        #adaptivePurepursuit function initialization
        

        #speedControl function initialization
        
# (path, state hy5osholak) -> function purepursuit -> steering -> pid -> throttle -> publish(steering, throttle)

    def pid_controller(self,steering):
        self.target_speed = self.speedControl(steering)
        error = self.target_speed - self.velocity
        p_term = self.kp * error
        self.error_sum += error
        i_term = self.ki * self.error_sum
        d_term = self.kd * (error - self.prev_error) / self.dt
        control_signal = p_term + i_term + d_term
        self.prev_error = error
        control_signal= max(-1.0, min(1.0, control_signal))
        acceleration = control_signal
        return acceleration


    def search_target_point(self):
        min_distance = float('inf')
        target_index = None
        for i, waypoint in enumerate(self.waypoints):
            distance = self.calculate_distance(self.state[:2], waypoint)
            if distance < min_distance:
                min_distance = distance
                min_index = i
        look_ahead_distance = 1.0
        for i in range(min_index,len(self.waypoints) - 1):
            distance = self.calculate_distance(self.state[:2], waypoint)
            if distance > look_ahead_distance :
                target_index = i
                break
        return target_index
    @staticmethod


    def calculate_distance(point1: list, point2: list):
        delta_x = point2[0] - point1[0]
        delta_y = point2[1] - point1[1]
        return math.sqrt(delta_x ** 2 + delta_y ** 2)


    def adaptivePurepursuit(self):
        self.lookahead_distance = self.velocity * self.gain + self.lookaheadconstant
        target_index = self.search_target_point()
        target_waypoint = self.waypoints[target_index]
        tx, ty = target_waypoint
        dx = tx - self.x
        dy = ty - self.y
        # if target_index == len(self.waypoints) - 1:
        #         return 0
        alpha = math.atan2(dy, dx) - self.yaw
        lookahead_angle = math.atan2(2 * 0.5 * math.sin(alpha) / self.lookahead_distance, 1)
        steering_angle = max(-0.5, min(0.5, lookahead_angle))
        return steering_angle
    

    def speedControl(self, steering_angle: float) -> float:
        self.target_speed: float = (20.0/3.6) / (abs(steering_angle) + 0.001) # change steering angle to rad
        #targetSpeed: float = map(abs(steering_angle),0,30,3,0.5)
        self.target_speed = min(self.target_speed,self.maxspeed)
        self.target_speed = max(self.target_speed,self.minspeed)
        return self.target_speed
    

    def publish_control_signals(self):
        if self.pathFlag == True :
            steering_angle = Float32()
            steering_angle.data = self.adaptivePurepursuit()*(180/math.pi)
            self.steer_pub.publish(steering_angle)
            if len(self.waypoints) > 0 and self.search_target_point == len(self.waypoints) - 1:
                throttle = 0
            else:
                throttle = Float32()
                throttle.data = self.pid_controller(steering_angle.data)
            self.throttle_pub.publish(throttle)
            log = "tracking waypoint: " + str(self.waypoints[self.i])
            self.get_logger().info(log)