#Michael Abraham
#GTID:903982906

"""
Fill in the Blank 1: Bumpers and Buttons

This script will give you experience on the event mechanism
for the bumpers and buttons. You will also be able to engage
many of the robot's interactive features, like wheel movement,
lights, and sounds. 
"""

# Tasks: Fill in the blanks below to implement the following 4 functions 
# such that:
#    - When the left bumper is pressed, the robot starts to spin counter-clockwise,
#      and the ring light will turn on in solid cyan. The speed of rotation should be reset to the default speed of 4.
#    - When the right bumper is pressed, the robot starts to spin clockwise,
#     and the ring light will turn on in solid magenta. The speed of rotation should be reset to the default speed of 4.
#    - When the (.) button is pressed, the robot will decrease its spinning speed by 2,
#      and play the note C5.
#    - When the (..) button is pressed, the robot will increase its spinning speed by 2,
#      and play the note D5.

# Make sure to delete/replace the ________ (line) with your code

"""
To aid you in this assignment, all lines that need to be changed will be marked with (TODO) 
in a nearby comment.

We will use a variable called SPEED to store the current speed of the robot, and a variable
called ROTATION_DIR to track which direction the robot is moving. Since
we'll need to interact and change these variables across multiple functions in this script,
we must make SPEED and ROTATION_DIR GLOBAL variables.
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

# creating a GLOAL variable for the wheel speed and rotation direction
# we normally name global variables in all caps to remind us
# they are not local variables
SPEED = 4 # cm/s
ROTATION_DIR = None   # possible values: None, "clockwise", "counter-clockwise"

# -------------------------------------------------------------------------------------

# Function 1: bumped_left()
'''THIS FUNCTION HAS ALREADY BEEN IMPLEMENTED FOR YOU.'''
# Please use it as a reference!

# defining an event that is triggered when the robot's left bumper is pressed
@event(robot.when_bumped, [True, False])       # the list [True, False] indicates the left bumper is pressed
async def bumped_left(robot):                  # asynchronous function that runs when the event is triggered
    global SPEED, ROTATION_DIR                 # specify that SPEED and ROTATION_DIR are global variables
    print('Left bumper pressed')               # output message indicating the left bumper was pressed
    SPEED = 4                                  # reset SPEED to the default value of 4
    ROTATION_DIR = "counter-clockwise"         # change ROTATION_DIR to counter clockwise
    await robot.set_wheel_speeds(-SPEED,SPEED) # set the robot's wheel speeds: left wheel to -SPEED and right wheel to SPEED
                                                   # This causes the robot to rotate counter-clockwise.
    await robot.set_lights_rgb(0, 255, 255)    # set the robot's light to cyan - R: 0, G: 255, B: 255

# -------------------------------------------------------------------------------------
    
# Function 2: bumped_right()
# TODO: Fill in the blanks to implement this function.
# Recall: When the right bumper is pressed, the robot starts to spin clockwise,
# and the ring light will turn on in solid magenta.

# defining another event for when the robot's right bumper is pressed.
@event(robot.when_bumped, [False, True])        # the list [False, True] indicates the right bumper is pressed
async def bumped_right(robot):                  # asynchronous function that runs when the event is triggered
    global SPEED, ROTATION_DIR                 # specify that SPEED and ROTATION_DIR are global variables                                        # TODO: specify that SPEED and ROTATION_DIR are global variables
    print('Right bumper pressed')               # output message indicating the right bumper was pressed
    SPEED = 4                                   # reset SPEED to the default value of 4
    ROTATION_DIR = "clockwise"                  # change ROTATION_DIR to clockwise
    await robot.set_wheel_speeds(SPEED, -SPEED)         # TODO: set the robot's wheel speeds so that the robot rotates clockwise
                                                # Hint: Check the previous function to see how to change the wheel speeds!
    await robot.set_lights_rgb(255, 0, 255)                 # TODO: set the robot's lights to magenta - R: 255, G: 0, B
# -------------------------------------------------------------------------------------
    
# Function 3: touched_left()
# TODO: Fill in the blanks to implement this function.
# Recall: When the (.) button is pressed, the robot will decrease its spinning speed by 2,
# and play the note C5.

# setting up an event that will be triggered when the left button on the robot is touched.
@event(robot.when_touched, [True, False])          # the [True, False] list indicates the left button is touched.
async def touched_left(robot):                 
    global SPEED, ROTATION_DIR                     # TODO: specify that SPEED and ROTATION_DIR are global variables
    print('Left button pressed')                   # output message for debugging or user feedback.
    SPEED -= 2                                     # decrease the SPEED by 2
    if ROTATION_DIR == "clockwise":
        await robot.set_wheel_speeds(SPEED,-SPEED) # set the robot's wheel speeds to rotate clockwise.
    elif ROTATION_DIR == "counter-clockwise":
        await robot.set_wheel_speeds(-SPEED, SPEED)        # TODO: set the robot's wheel speeds to rotate counter-clockwise.
    await robot.play_note(Note.C5, 0.5)            # play the note C5 for half a second.

# -------------------------------------------------------------------------------------
    
# Function 4: touched_right()
# TODO: Fill in the blanks to implement this function.
# Recall: When the (..) button is pressed, the robot will increase its spinning speed by 2,
# and play the note D5.

# setting up an event that will be triggered when the left button on the robot is touched.
@event(robot.when_touched, [False, True])          # the [True, False] list indicates the left button is touched.
async def touched_right(robot):                 
    global SPEED, ROTATION_DIR                     # TODO: specify that SPEED and ROTATION_DIR are global variables
    print('Right button pressed')                  # output message for debugging or user feedback.
    SPEED += 2                                     # increase the SPEED by 2
    if ROTATION_DIR == "clockwise":
        await robot.set_wheel_speeds(SPEED,-SPEED) # set the robot's wheel speeds to rotate clockwise.
    elif ROTATION_DIR == "counter-clockwise":
        await robot.set_wheel_speeds(-SPEED, SPEED)                 # TODO: set the robot's wheel speeds to rotate counter-clockwise.
    await robot.play_note(Note.D5, 0.5)                 # TODO: play the note D5 for half a second.

# trigger the system execution
robot.play()
