#Miichael Abraham
#GTID: 903982906

"""
Fill in the Blank 2: IR Sensors

This script will give you experience on the event mechanism
for the IR sensors. You will be able to manipulate the data
readings of all 7 sensors, analyze them, and perform simple
robotic tasks depending on the sensor readings.
"""

## TODO: Fill in the blanks below to implement the following 2 functions 
## such that:
##     - The robot is able to detect objects placed in front of it.
##     - The robot is able to determine which side of the robot
##       the object is located.
##     - If the object is on the left side, the robot's ring light
##       will shine red.
##     - If the object is on the right side, the robot's ring light
##       will shine green. 
##    - If the object is right down the middle, the robot's ring light
##       will shine white.

"""
Fun fact: These light configurations are similar to the navigational
lights of a plane or ship!

To aid you in this assignment, all lines that need to be changed will be marked with (TODO) 
in a nearby comment.

Recall: There are seven sensors located at the front and sides of the robot. Each sensor
makes an angle of [-65.3, -38.0, -20.0, -3.0, 14.25, 34.0, 65.3] to the center of the robot.
While the angle information is not important for this script, you will definitely need it in
future robot assignments!

For this script, you can assume that the first 3 sensors are on the left side, the last 3
sensors are on the right side, and the 4th sensor is in the middle of the robot.
"""

# importing the Bluetooth class from the irobot_edu_sdk.backend module
from irobot_edu_sdk.backend.bluetooth import Bluetooth
# importing various classes and decorators from the irobot_edu_sdk.robots module
from irobot_edu_sdk.robots import event, hand_over, Color, Robot, Root, Create3
# importing the Note class from the irobot_edu_sdk.music module
from irobot_edu_sdk.music import Note

# creating a robot instance using the Create3 class.
# this will be used to control the robot and set up events
# the robot connects via Bluetooth to the robot named "BORELA".

# TODO: Replace the name of the robot in the parenthesis with
# the robot you are currently working on
robot = Create3(Bluetooth("BORELA"))

# a list of angles for the robot's infrared (IR) sensors,
# indicating their respective positions.
IR_ANGLES = [-65.3, -38.0, -20.0, -3.0, 14.25, 34.0, 65.3]

# -------------------------------------------------------------------------------------

# Function 1: findClosestSensor()
'''TODO: Implement this function by yourself.'''
# Parameters: readings (a list of 7 elements representing the readings
#     obtained from the 7 sensors)
# Returns: sensorIndex (representing the index of the sensor with the
#     closest reading)
# Description: This function takes in a list of sensor readings, and returns the
#     index of the sensor with the closest proximity (which is the largest sensor reading).
#     This function should only analyze the sensors with readings that are at least 20.
#     If none of the sensors have readings that are at least 20, return -1.

# Note: You can assume there will be no duplicate values that are at least 20 in the list.

# Recall: You can submit this file to Gradescope to check if this function has been
# implemented correctly!

def findClosestSensor(readings):
    max_reading = -1
    sensorIndex = -1

    for i in range(len(readings)):
        if readings[i] >= 20:
            if readings[i] > max_reading:
                max_reading = readings[i]
                sensorIndex = i

    return sensorIndex

# -------------------------------------------------------------------------------------

# Function 2: play()
# TODO: Fill in the blanks to implement this function.
# This function continuously checks the robots sensors for the closest object,
# and changes the color of the ring light depending on which side the closest 
# object is on:
#     - Sensors 0, 1, 2: Red
#     - Sensor 3: White
#     - Sensors 4, 5, 6: Green

# set up an event that starts when the robot's play button is activated.
@event(robot.when_play)
async def play(robot):
    await robot.set_lights_rgb(255, 255, 255)                          # set the robot's light to white.
    # begin an infinite loop to constantly read from the IR sensors.
    while True:
        readings = (await robot.get_ir_proximity()).sensors # a list   # get the IR raw proximity readings from the robot's sensors.
        indexOfMaxReading = findClosestSensor(readings)                    # TODO: call findClosestSensor() to find the sensor with the closest object.
        if indexOfMaxReading in [0, 1, 2]:                             # if the closest sensor is sensor 0, 1, or 2:
            await robot.set_lights_rgb(255, 0, 0)                       # TODO: set the robot's light to red.
            print("Sensor Readings: {}, Closest Sensor: {} (left)".format(readings, indexOfMaxReading))
        elif indexOfMaxReading in [4, 5, 6]:                                  # TODO: if the closest sensor is sensor 4, 5, or 6:
            await robot.set_lights_rgb(0, 255, 0)                                    # TODO: set the robot's light to green.
            print("Sensor Readings: {}, Closest Sensor: {} (right)".format(readings, indexOfMaxReading))
        else:                                                          # else (if the closest sensor is sensor 3 or there is no
                                                                       # object detected)
            await robot.set_lights_rgb(255, 255, 255)                     # TODO: set the robot's light to white.
            print("Sensor Readings: {}, Closest Sensor: {} (middle / no object found)".format(readings, indexOfMaxReading))
        await robot.wait(0.5)                                          # block execution for half a second

# start the robot's functionality, effectively "booting up" the system and listening for events.
robot.play()
