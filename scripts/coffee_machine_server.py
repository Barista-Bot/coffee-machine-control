#!/usr/bin/env python

from coffee_machine_control.srv import *
import rospy, time
import RPi.GPIO as GPIO
import pickle

# capsule type: (dispenser position, capsule count)
coffee_capsule_dispenser={
    'coffee_type: mocha':(1,10),
    'coffee_type: caramel':(2,10),
    'coffee_type: vanilla':(3,10),
    'coffee_type: espresso':(4,10)
}

current_coffee_capsule_dispenser_position = pickle.load(open("/home/pi/settings.p", 'rb')) 
steps_per_quarter_rotation = 128
loader_motor_activation_time = 2

stepper_output_gpio_bus = [17, 22, 23, 4]
motor_left_gpio = 24
motor_right_gpio = 25

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
    for gpio_channel in stepper_output_gpio_bus:
        GPIO.setup(gpio_channel, GPIO.OUT)
        GPIO.output(gpio_channel, True) # all outputs are inverted
    GPIO.setup(motor_left_gpio, GPIO.OUT)
    GPIO.setup(motor_right_gpio, GPIO.OUT)
    GPIO.output(motor_left_gpio, True)
    GPIO.output(motor_right_gpio, True)
    
def setup_coffee_for_manual_vending(coffee_type):

    print "Coffee Machine: "+str(coffee_type)+" selected."

    if (coffee_capsule_dispenser[str(coffee_type)][1] == 0):
        return coffee_machineResponse(False, "Out of chosen capsules")

    # Rotate capsule holder to select chosen capsule
    print "Coffee Machine: Current capsule dispenser position is "+str(current_coffee_capsule_dispenser_position)
    print "Coffee Machine: Rotating capsule dispenser to position "+str(coffee_capsule_dispenser[str(coffee_type)][0])
#    pickle.dump(coffee_capsule_dispenser[str(coffee_type)][0], open("/home/pi/settings.p", "wb"))
    quarter_rotation_steps_needed = (coffee_capsule_dispenser[str(coffee_type)][0] - current_coffee_capsule_dispenser_position) % 4
    for quarter_rotation_count in range(0, quarter_rotation_steps_needed):    
	for step_count in range(1, steps_per_quarter_rotation):
    		for step in range(0, 8):
               		for gpio_channel in range(0, 4):
            			if (step_sequence[step][gpio_channel] == 0):
                			GPIO.output(stepper_output_gpio_bus[gpio_channel], True)
            			else:
                			GPIO.output(stepper_output_gpio_bus[gpio_channel], False)
			time.sleep(0.01)
			
    # Disable stepper to prevent overheating
    for gpio_channel in stepper_output_gpio_bus:
        GPIO.setup(gpio_channel, GPIO.OUT)
        GPIO.output(gpio_channel, True) 
        
    print "Coffee Machine: Capsule selected and added to loader"
 
    # Load selected capsule into machine
    print "Coffee Machine: Loading capsule into Nespresso machine"
    GPIO.output(motor_left_gpio, False)
    GPIO.output(motor_right_gpio, False)
    time.sleep(loader_motor_activation_time)
    GPIO.output(motor_left_gpio, True)
    GPIO.output(motor_right_gpio, True)
    print "Coffee Machine: Capsule loaded into Nespresso machine, ready for manual coffee vend"
 
    # Decrement capsule count
    coffee_capsule_dispenser[str(coffee_type)] = (coffee_capsule_dispenser[str(coffee_type)][0],  coffee_capsule_dispenser[str(coffee_type)][1] - 1)
    print "Coffee Machine: "+str(coffee_capsule_dispenser[str(coffee_type)][1])+" of "+str(coffee_type)+" remaining"    
  
    return coffee_machineResponse(True, "Ready")

def coffee_machine_control_server():
    setup_gpio()
    rospy.init_node('coffee_machine_control_server')
    rospy.Service('coffee_machine', coffee_machine, setup_coffee_for_manual_vending)
    print "Ready to load capsules"
    rospy.spin()

if __name__ == "__main__":
    coffee_machine_control_server()
