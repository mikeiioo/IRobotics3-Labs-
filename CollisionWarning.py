#Michael Abraham GTID: 903982906
#Deep Patel GTID: 904000124


from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, hand_over, Color, Robot, Root, Create3
from irobot_edu_sdk.music import Note

robot = Create3(Bluetooth())   # Put robot name here.

# --------------------------------------------------------
# Implement the first two functions so that the robot
# will stop and turn on a solid red light
# when any button or bumper is pressed.
# --------------------------------------------------------


ROBOT_TOUCHED = False

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

# --------------------------------------------------------
# Implement avoidCollision() so that the robot CONTINUOUSLY 
# reads the IR measurement from the CENTER sensor.
# When the robot senses that the wall in front of the robot is:
#     <= 5 units away, stop the robot, set a red light, and play D7.
#     <= 30 units away, slow down the robot to 1 unit/s, set an orange light,
#        and play D6.
#     <= 100 units away, move the robot at a moderate speed (4 units/s), 
#        set a yellow light, and play D5.
#     > 100 units away, proceed at a faster pace (8 units/s), set a green light.
# --------------------------------------------------------

@event(robot.when_play)
async def avoidCollision(robot):
    global ROBOT_TOUCHED
    while ROBOT_TOUCHED == False:
        readings = (await robot.get_ir_proximity()).sensors
        middle_readings = readings[3]
        proximity = 4095/(middle_readings + 1)
        if proximity <= 5:
            await robot.set_lights_rgb(255, 0, 0)
            await robot.set_wheel_speeds(0,0)
            await robot.play_note(Note.D7, 1)
        elif proximity > 5 and proximity <= 30:
            await robot.set_lights_rgb(255, 64, 0)
            await robot.set_wheel_speeds(1,1)
            await robot.play_note(Note.D6, 1)
        elif proximity > 30 and proximity <= 100:
            await robot.set_lights_rgb(255, 115, 0)
            await robot.set_wheel_speeds(4,4)
            await robot.play_note(Note.D5, 1)
        else:
            await robot.set_lights_rgb(0, 255, 0)
            await robot.set_wheel_speeds(8,8)

        if ROBOT_TOUCHED:
            await robot.set_lights_rgb(255, 0, 0)
            await robot.set_wheel_speeds(0,0)


# start the robot
robot.play()
