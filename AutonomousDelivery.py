from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, hand_over, Color, Robot, Root, Create3
from irobot_edu_sdk.music import Note

import math as m

# robot is the instance of the robot that will allow us to call its methods and to define events with the @event decorator.
robot = Create3(Bluetooth("AVINASH-BOT"))  # Will connect to the first robot found.

HAS_COLLIDED = False
HAS_REALIGNED = False
HAS_FOUND_OBSTACLE = False
SENSOR2CHECK = 0
HAS_ARRIVED = False
DESTINATION = (0, 20)
ARRIVAL_THRESHOLD = 5
IR_ANGLES = [-65.3, -38.0, -20.0, -3.0, 14.25, 34.0, 65.3]

# Implementation for fail-safe robots
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

# ==========================================================

# Helper Functions
def getMinProxApproachAngle(readings):
    """Determine the closest object and its corresponding angle."""
    IR_ANGLES = [-65.3, -38.0, -20.0, -3.0, 14.25, 34.0, 65.3]

    min_proximity = float('inf')  
    closest_angle = 0

    for i in range(len(readings)):
        proximity = 4095 / (readings[i] + 1)  
        if proximity < min_proximity:        
            min_proximity = proximity
            closest_angle = IR_ANGLES[i]     

    min_proximity = round(min_proximity, 3)

    return (min_proximity, closest_angle)




def getCorrectionAngle(heading): #Works 

    correction_angle = 0-int(90-heading)

    return int(correction_angle)


def getAngleToDestination(currentPosition, destination):
    x1, y1 = currentPosition
    x2, y2 = destination

    dx = x2 - x1
    dy = y2 - y1

    angle_rad = m.atan2(dy, dx)

    angle_deg = m.degrees(angle_rad)

    angle_to_destination = 90 - angle_deg


    if angle_to_destination > 180:
        angle_to_destination -= 360
    elif angle_to_destination < -180:
        angle_to_destination += 360

    return int(angle_to_destination)

def checkPositionArrived(currentPosition, destination, threshold): #Works
    dx = destination[0] - currentPosition[0]
    dy = destination[1] - currentPosition[1]
    
    distance = m.sqrt(dx**2 + dy**2)


    return distance <= threshold


# === REALIGNMENT BEHAVIOR
async def realignRobot(robot):
    global HAS_REALIGNED
    pos = await robot.get_position()
     

    correction_angle = getCorrectionAngle(pos.heading)
    print(f"This is the correction angle: {correction_angle}")
    pos = await robot.get_position()
    destination = DESTINATION

    angle_to_destination = getAngleToDestination((pos.x, pos.y), destination)
    print(f"This is the atd: {angle_to_destination}")

    await robot.turn_right(correction_angle)
    await robot.turn_right(angle_to_destination)
    HAS_REALIGNED = True


# === MOVE TO GOAL
async def moveTowardGoal(robot):
    global SENSOR2CHECK, HAS_FOUND_OBSTACLE

    readings = (await robot.get_ir_proximity()).sensors  

    closest_distance, closest_angle = getMinProxApproachAngle(readings)

    if closest_distance <= 20:
        print("UH OH OBJECT DETECTED")
        await robot.set_wheel_speeds(0, 0)
        if closest_angle < 0:
            await robot.turn_right(90+closest_angle)
            SENSOR2CHECK = 0
        else:
            await robot.turn_left(90-closest_angle)
            SENSOR2CHECK = 6
            
        print("turned to perp")
        HAS_FOUND_OBSTACLE = True 
            
    else:
        await robot.set_wheel_speeds(15, 15)

# === FOLLOW OBSTACLE
async def followObstacle(robot):
##"""
##    global SENSOR2CHECK
##    
##    await robot.set_wheel_speeds(15, 15)
##
##    fPass = True
##
##    while fPass:
##        readings = (await robot.get_ir_proximity()).sensors
##        proximity = 4095 / (readings[SENSOR2CHECK] + 1)  
##        if proximity >= 100:
##            print("we ready to move on boi")
##            await robot.move(30)
##            fPass = False
##            continue
##        if proximity < 20:
##            if SENSOR2CHECK == 0:
##                print("turning by 3 to reline")
##                await robot.turn_right(3)
##                await robot.set_wheel_speeds(15, 15)
##            elif SENSOR2CHECK == 6:
##                print("turning by 3 to reline")
##                await robot.turn_left(3)
##                await robot.set_wheel_speeds(15, 15)
##"""
#-------
    global SENSOR2CHECK, HAS_FOUND_OBSTACLE, HAS_REALIGNED
    



        
    readings = (await robot.get_ir_proximity()).sensors
    proximity = 4095 / (readings[SENSOR2CHECK] + 1)  
    if proximity >= 100:
        print("we ready to move on boi")
        await robot.set_wheel_speeds(0, 0)
        await robot.move(30)
        HAS_FOUND_OBSTACLE = False
        HAS_REALIGNED = False
    elif proximity < 20:
        if SENSOR2CHECK == 0:
            print("turning by 3 to reline")
            await robot.turn_right(3)
            await robot.set_wheel_speeds(15, 15)
        elif SENSOR2CHECK == 6:
            print("turning by 3 to reline")
            await robot.turn_left(3)
            await robot.set_wheel_speeds(15, 15)
    else:
        await robot.set_wheel_speeds(15, 15)
            

#-----
        

# ==========================================================

# Main function

@event(robot.when_play)
async def makeDelivery(robot):
    global HAS_ARRIVED, HAS_COLLIDED, HAS_REALIGNED, HAS_FOUND_OBSTACLE
    global DESTINATION, ARRIVAL_THRESHOLD
    await robot.reset_navigation()
    
    # Loop to manage the navigation process
    while not ROBOT_TOUCHED:
        # Check if the robot has arrived at the destination
        pos = await robot.get_position()  
        if checkPositionArrived((pos.x, pos.y), DESTINATION, ARRIVAL_THRESHOLD):
            HAS_ARRIVED = True
            await robot.set_wheel_speeds(0,0)
            await robot.set_lights_spin_rgb(0, 255, 0)  # Visual indicator of success
            print("Destination reached!")
            break

        # Realignment step if necessary
        if not HAS_REALIGNED:
            await realignRobot(robot)
            print("Robot realigned to face destination.")

        # Move toward the goal
        if not HAS_FOUND_OBSTACLE:
            await moveTowardGoal(robot)


        # Handle obstacle navigation
        if HAS_FOUND_OBSTACLE:
            await followObstacle(robot)
            print("Robot escaped")
 



    print("Navigation loop completed.")

    if ROBOT_TOUCHED:
        await robot.set_lights_rgb(255, 0, 0)
        await robot.set_wheel_speeds(0, 0)

# start the robot
robot.play()
