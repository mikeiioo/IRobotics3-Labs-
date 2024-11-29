#Michael Abraham GTID: 903982906
#Deep Patel GTID: 904000124

from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, hand_over, Color, Robot, Root, Create3
from irobot_edu_sdk.music import Note

robot = Create3(Bluetooth())   # Put robot name here.

# IR Sensor Angles
IR_ANGLES = [-65.3, -38.0, -20.0, -3.0, 14.25, 34.0, 65.3]

# --------------------------------------------------------
# Implement the first two functions so that the robot
# will stop and turn on a solid red light
# when any button or bumper is pressed.
# --------------------------------------------------------

ROBOT_TOUCHED = False
COLOR = True
NUM = 0
NOTENUM = 0
# EITHER BUTTON
@event(robot.when_touched, [True, True])  # User buttons: [(.), (..)]
async def when_either_touched(robot):
    global ROBOT_TOUCHED 
    ROBOT_TOUCHED = True
    

# EITHER BUMPER
@event(robot.when_bumped, [True, True])  # [left, right]
async def when_either_bumped(robot):
    global ROBOT_TOUCHED 
    ROBOT_TOUCHED = True

async def changeColor(robot):
    global NUM
    NUM += 1
    if NUM % 2 == 0:
        await robot.set_lights_rgb(0, 255, 255)
    else:
        await robot.set_lights_rgb(255, 0, 255)


    
# --------------------------------------------------------
# Implement robotPong() so that the robot:
#     Sets the initial light to cyan.
#     Moves in a straight line at 15 units/s.
#     CONTINUOUSLY checks IR readings for nearby walls.
#     If the closest wall is <= 20 units away,
#         Momentarily stop.
#         Reflect its direction based on the angle of the wall.
#         Change the light from cyan to magenta, or vice versa.
# --------------------------------------------------------

@event(robot.when_play)
async def robotPong(robot):
    await robot.set_lights_rgb(0, 255, 255)
    """
    Use the following two lines somewhere in your code to calculate the
    angle and direction of reflection from a list of IR readings:
        (approx_dist, approx_angle) = angleOfClosestWall(ir_readings)
        (direction, turningAngle) = calculateReflectionAngle(approx_angle)
    Then, if the closest wall is less than 20 cm away, use the
    direction and the turningAngle to determine how to rotate the robot to
    reflect.
    """
    while ROBOT_TOUCHED == False:
        readings = (await robot.get_ir_proximity()).sensors
        await robot.set_wheel_speeds(15,15)
       # await angleOfClosestWall(readings)
        cDistance, cAngle = angleOfClosestWall(readings)
        if cDistance < 20:
            await robot.set_wheel_speeds(0,0)
            await changeColor(robot)
            await robotNote(robot)
            cDirection, cReflection = calculateReflectionAngle(cAngle)
            if cDirection == "left":
                await robot.turn_left(cReflection)
                await robot.set_wheel_speeds(15,15)
            else:
                await robot.turn_right(cReflection)
                await robot.set_wheel_speeds(15,15)

        if ROBOT_TOUCHED == True:
            await robot.set_lights_rgb(255, 0, 0)
            await robot.set_wheel_speeds(0,0)



def angleOfClosestWall(readings):
    """Remember that this function can be autograded!"""
    IR_ANGLES = [-65.3, -38.0, -20.0, -3.0, 14.25, 34.0, 65.3]
    angle = 0
    distance = 0
    final_distance = 0
    
    for i in range(len(readings)):
        if readings[i] > distance:
            distance = readings[i]
            angle = IR_ANGLES[i]

    final_distance = 4095/(distance + 1)
    final_distance = round(final_distance, 3)

    return (final_distance, angle)


def calculateReflectionAngle(angle):
    """Remember that this function can be autograded!"""
    reflection = 0
    direction = ""
    if angle > 0:
        reflection = 180 - (2 * angle)
        direction = "left"
       
    else:
        reflection = 180 + (2 * angle)
        direction = "right"

    reflection = round(reflection, 3)

    return (direction, reflection)


async def robotNote(robot):
    global NOTENUM
    NOTENUM += 1
    if NOTENUM % 7 == 1:
        await robot.play_note(Note.C5, 0.5)   
    elif NOTENUM % 7 == 2:
        await robot.play_note(Note.D5, 0.5)   
    elif NOTENUM % 7 == 3:
        await robot.play_note(Note.E5, 0.5)
    elif NOTENUM % 7 == 4:
        await robot.play_note(Note.F5, 0.5)
    elif NOTENUM % 7 == 5:
        await robot.play_note(Note.G5, 0.5)
    elif NOTENUM % 7 == 6:
        await robot.play_note(Note.A5, 0.5)
    elif NOTENUM % 7 == 0:
        await robot.play_note(Note.B5, 0.5)   

# start the robot
robot.play()
