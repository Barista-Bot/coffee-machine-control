#!/usr/bin/env python

from coffee_machine_control.srv import *
import rospy, time
import RPi.GPIO as GPIO
import pickle

# capsule type: (dispenser position, capsule count)
coffee_capsule_dispenser={
    'coffee_type: chocolate':(1,10),
    'coffee_type: caramel':(2,10),
    'coffee_type: christmas':(3,10),
    'coffee_type: vanilla':(4,10)
}

current_coffee_capsule_dispenser_position = pickle.load(open("/home/pi/settings.p", 'rb')) 
steps_per_quarter_rotation = 128
loader_motor_reverse_activation_time = 3
loader_motor_forward_activation_time = 1
loader_motor_partialforward_activation_time = 1

freq = 230
period = 1/freq

stepper_output_gpio_bus = [17, 22, 23, 4]
motor_reverse_gpio = 24
motor_forward_gpio = 25
coffee_switch_gpio = 27

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
        GPIO.output(gpio_channel, False) 
    GPIO.setup(motor_forward_gpio, GPIO.OUT)
    GPIO.setup(motor_reverse_gpio, GPIO.OUT)
    GPIO.output(motor_forward_gpio, False)
    GPIO.output(motor_reverse_gpio, False)
    GPIO.setup(coffee_switch_gpio, GPIO.OUT)
    GPIO.output(coffee_switch_gpio, False)

def setup_coffee_for_manual_vending(coffee_type):

    print "Coffee Machine: "+str(coffee_type)+" selected."

    if (coffee_capsule_dispenser[str(coffee_type)][1] == 0):
        return coffee_machineResponse(False, "Out of chosen capsules")

    # Rotate capsule holder to select chosen capsule
    print "Coffee Machine: Current capsule dispenser position is "+str(current_coffee_capsule_dispenser_position)
    print "Coffee Machine: Rotating capsule dispenser to position "+str(coffee_capsule_dispenser[str(coffee_type)][0])
    pickle.dump(coffee_capsule_dispenser[str(coffee_type)][0], open("/home/pi/settings.p", "wb"))
    quarter_rotation_steps_needed = (coffee_capsule_dispenser[str(coffee_type)][0] - current_coffee_capsule_dispenser_position) % 4
    for quarter_rotation_count in range(0, quarter_rotation_steps_needed):    
	for step_count in range(1, steps_per_quarter_rotation):
    		for step in range(0, 8):
               		for gpio_channel in range(0, 4):
            			if (step_sequence[step][gpio_channel] == 0):
                			GPIO.output(stepper_output_gpio_bus[gpio_channel], False)
            			else:
                			GPIO.output(stepper_output_gpio_bus[gpio_channel], True)
			time.sleep(0.01)
			
    # Open capsule tray to allow capsule to be loaded
    GPIO.output(motor_forward_gpio, True)
    time.sleep(loader_motor_partialforward_activation_time)
    GPIO.output(motor_forward_gpio, False) 

    # Pause to let capsule drop
    time.sleep(1)

    # Complete capsule opening
    GPIO.output(motor_forward_gpio, True)
    time.sleep(loader_motor_forward_activation_time)
    GPIO.output(motor_forward_gpio, False)

    # Disable stepper to prevent overheating
    for gpio_channel in stepper_output_gpio_bus:
        GPIO.setup(gpio_channel, GPIO.OUT)
        GPIO.output(gpio_channel, False) 
        
    print "Coffee Machine: Capsule selected and added to loader"

    time.sleep(1)
 
    # Load selected capsule into machine
    print "Coffee Machine: Loading capsule into Nespresso machine"
    GPIO.output(motor_reverse_gpio, True)
    time.sleep(loader_motor_reverse_activation_time)
    GPIO.output(motor_reverse_gpio, False)
    
    print "Coffee Machine: Capsule loaded into Nespresso machine, ready for coffee vend"
 
    # Dispense coffee

    #Push Button
    for count in range(0, 100):
	GPIO.output(27, 1)
	time.sleep(0.0016)
	GPIO.output(27, 0)
	time.sleep(0.0016)
    #Retract ServoMotor
    for count in range(0, 100):
	GPIO.output(27, 1)
	time.sleep(0.003)
	GPIO.output(27, 0)
	time.sleep(0.003)    

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

