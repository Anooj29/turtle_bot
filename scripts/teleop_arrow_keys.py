#!/usr/bin/env python3
"""Drive turtle_bot with the 4 arrow keys. Space/k = stop, q = quit."""

import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node

LINEAR_SPEED = 0.4
ANGULAR_SPEED = 1.0

INSTRUCTIONS = """
turtle_bot arrow-key teleop
----------------------------
   Up    : drive forward
   Down  : drive backward
   Left  : turn left (in place)
   Right : turn right (in place)
   space or k : stop
   q     : quit
----------------------------
"""


def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    ch = sys.stdin.read(1)
    if ch == "\x1b":
        ch += sys.stdin.read(2)
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, settings)
    return ch


def main():
    settings = termios.tcgetattr(sys.stdin)

    rclpy.init()
    node = Node("teleop_arrow_keys")
    pub = node.create_publisher(Twist, "cmd_vel", 10)

    print(INSTRUCTIONS)

    try:
        while True:
            key = get_key(settings)
            twist = Twist()

            if key == "\x1b[A":        # Up
                twist.linear.x = LINEAR_SPEED
            elif key == "\x1b[B":      # Down
                twist.linear.x = -LINEAR_SPEED
            elif key == "\x1b[C":      # Right
                twist.angular.z = -ANGULAR_SPEED
            elif key == "\x1b[D":      # Left
                twist.angular.z = ANGULAR_SPEED
            elif key in (" ", "k"):
                pass  # zero twist, i.e. stop
            elif key == "q":
                break
            else:
                continue  # unrecognized key: don't publish, keep last state

            pub.publish(twist)

    finally:
        pub.publish(Twist())  # stop the robot on exit
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
