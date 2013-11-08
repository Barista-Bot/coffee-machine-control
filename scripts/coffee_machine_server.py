#!/usr/bin/env python

from coffee_machine_control.srv import *
import rospy, time
import RPi.GPIO as GPIO

# capsule type: (loader position, capsule count)
coffee_capsule_loader={
    'coffee_type: mocha':(1,10),
    'coffee_type: caramel':(2,10),
    'coffee_type: vanilla':(3,10),
    'coffee_type: espresso':(4,10)
}

output_bus = [14, 15, 18, 23]

step_sequence = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    for gpio_channel in output_bus:
        GPIO.setup(gpio_channel, GPIO.OUT)
        GPIO.output(gpio_channel, False)

def setup_coffee_for_vending(coffee_type):

    print str(coffee_type)+" selected."

    if (coffee_capsule_loader[str(coffee_type)][1] == 0):
        return coffee_machineResponse(False, "Out of chosen capsules")


    # Rotate capsule holder

    # Load capsule
    print "Loading capsule"
    while True:
    	for step_count in range(0, 8):
        	print "."
        	for bit in range(0, 4):
            		if (step_sequence[step_count][bit] == 0):
                		GPIO.output(output_bus[bit], True)
            		else:
                		GPIO.output(output_bus[bit], False)
		time.sleep(0.01)
    print "Capsule loading complete, ready to vend."
    return coffee_machineResponse(True, "Capsule loaded.")

def coffee_machine_control_server():
    setup_gpio()
    rospy.init_node('coffee_machine_control_server')
    rospy.Service('coffee_machine', coffee_machine, setup_coffee_for_vending)
    print "Ready to load capsules"
    rospy.spin()

if __name__ == "__main__":
    coffee_machine_control_server()
