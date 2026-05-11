import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from my_robot_msgs.msg import WheelTicks
from sensor_msgs.msg import Imu
from my_robot.constants import (WHEELBASE, ARDUINO_PORT, ARDUINO_COM_BAUDE_RATE)
import serial
import time
import threading

class SerialBridge(Node):

    def __init__(self, 
                 wheelbase = WHEELBASE, 
                 arduino_port=ARDUINO_PORT, 
                 arduino_com_baude_rate=ARDUINO_COM_BAUDE_RATE):
        super().__init__('serial_bridge')
        self.get_logger().info('Node started!')
        
        self.wheelbase = wheelbase
        self.arduino_port = arduino_port
        self.arduino_com_baude_rate = arduino_com_baude_rate

        self.left_ticks = 0
        self.right_ticks = 0

        # establish serial connection to Arduino
        self.ser = serial.Serial(self.arduino_port, self.arduino_com_baude_rate, timeout=1)
        time.sleep(2)

        self.lock = threading.Lock()

        # create a subscriber for the cmd_vel
        self.subscriber = self.create_subscription(msg_type=Twist,
                                                   topic='/cmd_vel',
                                                   callback=self.subscriber_read_send_cmd_vel,
                                                   qos_profile=10)

        # imu publisher
        self.imu_publisher = self.create_publisher(msg_type=Imu, topic='/imu', qos_profile=10)

        # create publisher to publish wheel tick data data
        self.wheel_ticks_publisher = self.create_publisher(msg_type=WheelTicks, topic='/wheel_ticks', qos_profile=10)
        self.timer = self.create_timer(0.05, self.publish_wheel_ticks)

        # start thread after publishers are ready
        thread = threading.Thread(target=self.read_serial, daemon=True)
        thread.start()
    
    def subscriber_read_send_cmd_vel(self, msg):
        v_x = msg.linear.x
        a_z = msg.angular.z

        # calculate left and right wheel speeds 
        left_speed = v_x - (a_z * self.wheelbase/2)
        right_speed = v_x + (a_z * self.wheelbase/2)

        # send cmd_vel instructions to Arduino 
        self._send_cmd_vel_to_arduino(left_speed, right_speed)

    def _send_cmd_vel_to_arduino(self, left_speed, right_speed):
        cmd = f"VEL {left_speed:.2f} {right_speed:.2f}\n"
        self.get_logger().info(f"TX: {cmd.strip()}")
        try:
            self.ser.write(cmd.encode())
        except Exception as e:
            self.get_logger().error(f"Serial write failed: {e}")

    def publish_wheel_ticks(self):
        msg = WheelTicks()
        with self.lock:
            msg.left = self.left_ticks
            msg.right = self.right_ticks
        self.wheel_ticks_publisher.publish(msg)

    def publish_imu(self, ax, ay, az, gx, gy, gz):
        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu'

        msg.linear_acceleration.x = ax
        msg.linear_acceleration.y = ay
        msg.linear_acceleration.z = az

        msg.angular_velocity.x = gx
        msg.angular_velocity.y = gy
        msg.angular_velocity.z = gz
        self.imu_publisher.publish(msg)

                                       
    def read_serial(self):
        while True:
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("ENC"):
                parts = line.split()
                with self.lock:
                    self.left_ticks = int(parts[1])
                    self.right_ticks = int(parts[2])
            elif line.startswith("IMU"):
                parts = line.split()
                self.publish_imu(ax=float(parts[1]), 
                                 ay=float(parts[2]), 
                                 az=float(parts[3]), 
                                 gx=float(parts[4]), 
                                 gy=float(parts[5]), 
                                 gz=float(parts[6]))
                
            elif line:
                print(f"Arduino: {line}")


def main(args=None):
    rclpy.init(args=args)
    node = SerialBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
