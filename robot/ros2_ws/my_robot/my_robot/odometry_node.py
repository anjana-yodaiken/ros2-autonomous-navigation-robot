import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from my_robot_msgs.msg import WheelTicks
from tf2_ros.transform_broadcaster import TransformBroadcaster
from my_robot.constants import (WHEELBASE, DIST_PER_TICK)
import numpy as np 


class OdometryNode(Node):

    def __init__(self, 
                 wheelbase = WHEELBASE, 
                 dist_per_tick=DIST_PER_TICK):
        super().__init__('odometry_node')
        self.get_logger().info('Odometry node started!')

        self.tf_broadcaster = TransformBroadcaster(self)

        self.wheelbase = wheelbase
        self.dist_per_tick = dist_per_tick

        self.left_ticks = 0
        self.right_ticks = 0
        self.prev_left_ticks = 0
        self.prev_right_ticks = 0

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0


        # create a subscriber for the wheel_ticks
        self.subscriber = self.create_subscription(msg_type=WheelTicks, topic='/wheel_ticks', callback=self.subscriber_read_wheel_ticks, qos_profile=10) 

        # create publisher to publish odom data
        self.publisher = self.create_publisher(msg_type=Odometry, topic='/odom', qos_profile=10) 
        self.timer = self.create_timer(0.05, self.publish_odom)
    
    def subscriber_read_wheel_ticks(self, msg):
        self.left_ticks = msg.left
        self.right_ticks = msg.right

    def _count_ticks_from_last_update(self):
        dl = self.left_ticks - self.prev_left_ticks
        dr = self.right_ticks - self.prev_right_ticks
        self.prev_left_ticks = self.left_ticks
        self.prev_right_ticks = self.right_ticks
        return dl, dr
        
    def publish_odom(self):
        # publish odom 
        msg = Odometry()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'odom'
        msg.child_frame_id = 'base_link'

        dl, dr = self._count_ticks_from_last_update()
        left_dist = dl * self.dist_per_tick
        right_dist = dr * self.dist_per_tick
        delta_theta = (right_dist - left_dist)/self.wheelbase
        center_dist = (left_dist + right_dist)/2

        self.theta += delta_theta
        self.x += center_dist * np.cos(self.theta)
        self.y += center_dist * np.sin(self.theta)

        msg.pose.pose.position.x = self.x
        msg.pose.pose.position.y = self.y
        msg.pose.pose.orientation.z = np.sin(self.theta / 2)    
        msg.pose.pose.orientation.w = np.cos(self.theta / 2) 
        self.publisher.publish(msg)

        t = TransformStamped()                                             
        t.header.stamp = msg.header.stamp
        t.header.frame_id = 'odom'                                         
        t.child_frame_id = 'base_link'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0                                    
        t.transform.rotation.z = np.sin(self.theta / 2)
        t.transform.rotation.w = np.cos(self.theta / 2)                    
        self.tf_broadcaster.sendTransform(t)                               
   
def main(args=None):
    rclpy.init(args=args)
    node = OdometryNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
