#Michael Abraham GTID: 903982906
#Deep Patel GTID: 904000124

from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, hand_over, Color, Robot, Root, Create3
from irobot_edu_sdk.music import Note
import math as m

robot = Create3(Bluetooth())   # Put robot name here.

# --------------------------------------------------------
# Global Variables - feel free to add your own as necessary
# --------------------------------------------------------
ROBOT_TOUCHED = False

# Behavorial
HAS_COLLIDED = False     # The robot has collided with a wall.
HAS_EXPLORED = False     # The robot has finished exploring the box.
HAS_SWEPT = False        # The robot has finished sweeping, and
                         # has arrived at its final destination.

# Spatial Awareness
SENSOR2CHECK = 0         # The index of the sensor that corresponds 
                         # with the closest side wall,
                         # either 0 for left-most or -1 for right-most.  ROTATION_DIR SENSOR2CHECK
ROTATION_DIR = ""         # The direction the robot needs to explore.
CORNERS = []             # A list that stores all the corners as the robot explores.
DESTINATION = ()         # The point that is the farthest away from the robot.
                         # This point becomes the robot's final destination.
FINAL_D = False          # did you make it to the end?
TURN_NUM = 0
# Constants - Do not change.
ARRIVAL_THRESHOLD = 5    # We say that the robot has arrived at its final
                         # destination if the distance between the robot's
                         # position and the location of the final destination
                         # is less than or equal to this value.
SPEED = 10               # The speed at which the robot should normally move.
ROBOT_MOVE_DISTANCE = 15 # The distance by which the robot needs to move 
                         # to the side to sweep a new column of the box.

# --------------------------------------------------------
# Implement these three helper functions so that they
# can be used later on.
# --------------------------------------------------------

# Helper Function 1
def farthestDistance(currPosition, positions):
    """Remember that this function can be autograded!"""
    theTup = ()
    bigD = 0
    x1,y1 = currPosition
    for x2,y2 in positions:
        distance = m.sqrt((x2-x1)**2 + (y2-y1) ** 2)
        if distance > bigD:
            bigD = distance
            theTup = (x2,y2)

    return theTup

# Helper Function 2
def movementDirection(readings):
    """Remember that this function can be autograded!"""
    if readings[0] < readings[-1]:
        return "counterclockwise"
    else:
        return "clockwise"

# Helper Function 3
def checkPositionArrived(current_position, destination, threshold):
    """Remember that this function can be autograded!"""
    x1,y1 = current_position
    x2,y2 = destination 
    distance = m.sqrt((x2-x1)**2 + (y2-y1) ** 2)
    if distance <= threshold:
        return True
    else:
        return False

# Helper Function 4
def turn(ROTATION_DIR):
    global TURN_NUM
    TURN_NUM += 1
    if ROTATION_DIR == "right":
      if TURN_NUM % 2 == 1:
        return "right"
      else:
        return "left"
    else:
      if TURN_NUM % 2 == 1:
        return "left"
      else:
        return "right"

# --------------------------------------------------------
# Implement the these two functions so that the robot
# will stop and turn on a solid red light
# when any button or bumper is pressed.
# --------------------------------------------------------

# EITHER BUTTON
@event(robot.when_touched, [True, True])  # User buttons: [(.), (..)]
async def when_either_button_touched(robot):
    global ROBOT_TOUCHED 
    ROBOT_TOUCHED = True

# EITHER BUMPER
@event(robot.when_bumped, [True, True])  # [left, right]
async def when_either_bumped(robot):
    global ROBOT_TOUCHED 
    ROBOT_TOUCHED = True

# --------------------------------------------------------
# Implement play such that the robot:
#     Resets its navigational coordinate system.
#     Uses movementDirection() to determine which direction
#         the robot should plan to explore the box.
#     Sets SENSOR2CHECK and ROTATION_DIR depending on whether
#         the robot is going to move clockwise or counterclockwise.
#     Sets the wheel speed to SPEED
#     Calls sweep() and explore() inside of a while loop.
#         If the robot has not finished exploring, call explore()
#         If the robot has finished exploring, call sweep()
#     Stops execution after a collision or after the final
#         destination is reached.
# --------------------------------------------------------

@event(robot.when_play)
async def play(robot):
    global HAS_COLLIDED, HAS_EXPLORED, HAS_SWEPT, SENSOR2CHECK
    global ROTATION_DIR, CORNERS, DESTINATION, ARRIVAL_THRESHOLD
    global SPEED, ROBOT_MOVE_DISTANCE, FINAL_D
  
    await robot.reset_navigation() 
    readings = (await robot.get_ir_proximity()).sensors
    movement = movementDirection(readings)
    if movement == "clockwise":
      ROTATION_DIR = "right"
      SENSOR2CHECK = 0
    else:
      ROTATION_DIR = "left"
      SENSOR2CHECK = -1
    await robot.set_wheel_speeds(SPEED,SPEED)

      
    while ROBOT_TOUCHED == False: 
      if HAS_EXPLORED == False:
        await robot.set_lights_rgb(101, 197, 181) 
        await explore(robot)
      elif HAS_EXPLORED == True and HAS_SWEPT == False:
        await robot.set_lights_rgb(255, 64, 0)
        await sweep(robot)
      if ROBOT_TOUCHED == True:
        await robot.set_wheel_speeds(0,0)
        await robot.set_lights_rgb(255, 0, 0)
      if FINAL_D == True:
        break
      
      
# --------------------------------------------------------
# Implement explore such that the robot:
#     Finds the front and side proximity to a wall.
#     If there is a wall within 10 units in front,
#         stop, turn 90 degrees, and continue.
#     When all four corners have been found, determine
#         the furthest corner from the robot with farthestDistance() 
#     Auto-aligns with the side boundary if the robot drifts
#         away from the side wall.
# --------------------------------------------------------

async def explore(robot):
    global HAS_COLLIDED, HAS_EXPLORED, HAS_SWEPT, SENSOR2CHECK
    global ROTATION_DIR, CORNERS, DESTINATION, ARRIVAL_THRESHOLD
    global SPEED, ROBOT_MOVE_DISTANCE, FINAL_D
  
    readings = (await robot.get_ir_proximity()).sensors

    front_proximity = 4095/(readings[3] + 1)
    side_proximity = 4095/(readings[SENSOR2CHECK] + 1)
  
    if front_proximity < 10:
      await robot.set_wheel_speeds(0,0)
      pos = await robot.get_position()
      currPosition = (pos.x, pos.y)
      CORNERS.append(currPosition)
      
      if len(CORNERS) != 4:
        if ROTATION_DIR == "right":
          await robot.turn_right(90)
        else:
          await robot.turn_left(90)
        await robot.set_wheel_speeds(SPEED,SPEED)
      else:
        DESTINATION = farthestDistance(currPosition, CORNERS)
        print(f"{DESTINATION} is the farthest corner from the robot.")
        HAS_EXPLORED = True

    if side_proximity < 5:
      await robot.set_wheel_speeds(0,0)
      if ROTATION_DIR == "right":
        await robot.turn_right(3)
      else:
        await robot.turn_left(3)
      await robot.set_wheel_speeds(SPEED, SPEED)
    elif side_proximity >= 10:
      await robot.set_wheel_speeds(0, 0)
      if ROTATION_DIR == "right":
        await robot.turn_left(3)
      else:
        await robot.turn_right(3)
      await robot.set_wheel_speeds(SPEED, SPEED)




# --------------------------------------------------------
# Implement sweep such that the robot:
#     Checks if it has reached its final destination with
#         checkPositionArrived()
#     If the robot did reach its destination, stop, set
#         lights to green, and play a happy tune.
#     Else, if the robot's front proximity to a wall is <= 10 units,
#         stop, turn 90 degrees, move forwards by ROBOT_MOVE_DISTANCE,
#         turn 90 degrees again, and start again.
# --------------------------------------------------------

async def sweep(robot): # Change tolerance for sweep and changed the baby steps
    global HAS_COLLIDED, HAS_EXPLORED, HAS_SWEPT, SENSOR2CHECK
    global ROTATION_DIR, CORNERS, DESTINATION, ARRIVAL_THRESHOLD
    global SPEED, ROBOT_MOVE_DISTANCE, FINAL_D
  
    readings = (await robot.get_ir_proximity()).sensors
    front_proximity = 4095/(readings[3] + 1)
    side_proximity = 4095/(readings[SENSOR2CHECK] + 1)
  
    pos = await robot.get_position()
    current_position = (pos.x, pos.y)
    if checkPositionArrived(current_position, DESTINATION, ARRIVAL_THRESHOLD):
      await robot.set_wheel_speeds(0,0)
      await robot.set_lights_spin_rgb(0, 255, 0)
      await robot.set_lights_rgb(0, 255, 0)
      await robot.play_note(Note.C5, 0.5)
      await robot.play_note(Note.E5, 0.5)
      await robot.play_note(Note.G5, 0.5)
      await robot.play_note(Note.C6, 1.0)
      HAS_SWEPT = True
      FINAL_D = True
    else:
      if front_proximity <= 10:

        turning = turn(ROTATION_DIR)
        if turning == "right":
          await robot.turn_right(90)
        else:
          await robot.turn_left(90)
          
        readings = (await robot.get_ir_proximity()).sensors
        front_proximity = 4095/(readings[3] + 1)
      
        if front_proximity < ROBOT_MOVE_DISTANCE:
          await robot.move(front_proximity/3)
        else:
          await robot.move(ROBOT_MOVE_DISTANCE)
          
        if turning == "right":
          await robot.turn_right(90)
        else:
          await robot.turn_left(90)
          
        await robot.set_wheel_speeds(SPEED,SPEED)

        

# start the robot
robot.play()
