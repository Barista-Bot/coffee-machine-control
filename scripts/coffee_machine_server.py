#!/usr/bin/env python

from coffee_machine_control.srv import *
import rospy

coffee_capsule_loader={
    'coffee_type: mocha':(1,10),
    'coffee_type: caramel':(2,10),
    'coffee_type: vanilla':(3,10),
    'coffee_type: espresso':(4,10)
}

def setup_coffee_for_vending(coffee_type):
    print str(coffee_type)+" selected."
    if (coffee_capsule_loader[str(coffee_type)][1] == 0):
        return coffee_machineResponse(False, "Out of chosen capsules")
    # Rotate capsule holder
    # Drop capsule into machine
    return coffee_machineResponse(True, "Capsule loaded.")

def coffee_machine_control_server():
    rospy.init_node('coffee_machine_control_server')
    rospy.Service('coffee_machine', coffee_machine, setup_coffee_for_vending)
    print "Ready to load capsules"
    rospy.spin()

if __name__ == "__main__":
    coffee_machine_control_server()
