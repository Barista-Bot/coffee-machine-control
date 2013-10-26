#!/usr/bin/env python
import roslib; roslib.load_manifest('coffee_machine_control')

import sys

import rospy
from coffee_machine_control.srv import *

def coffee_machine_client(coffee_type):
    rospy.wait_for_service('coffee_machine')
    coffee_machine_control = rospy.ServiceProxy('coffee_machine', coffee_machine)
    try:
        resp = coffee_machine_control(coffee_type)
        print resp
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e

if __name__ == "__main__":
    coffee_machine_client("dharkan")
