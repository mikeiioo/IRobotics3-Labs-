from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, hand_over, Color, Robot, Root, Create3
from irobot_edu_sdk.music import Note
from collections import deque

# robot is the instance of the robot that will allow us to call its methods and to define events with the @event decorator.
robot = Create3(Bluetooth("AVINASH-BOT"))  # Will connect to the first robot found.

# === FLAG VARIABLES
HAS_COLLIDED = False
HAS_ARRIVED = False

# === MAZE DICTIONARY
N_X_CELLS = 3 # Size of maze (x dimension)
N_Y_CELLS = 3 # Size of maze (y dimension)
CELL_DIM = 50


# === DEFINING ORIGIN AND DESTINATION
PREV_CELL = None
START = (1,0)
CURR_CELL = START
DESTINATION = (2,2)
'''
MAZE_DICT[CURR_CELL]["visited"] = True
'''

# === PROXIMITY TOLERANCES
WALL_THRESHOLD = 80

# ==========================================================
# FAIL SAFE MECHANISMS

# EITHER BUTTON
@event(robot.when_touched, [True, True])  # User buttons: [(.), (..)]
async def when_either_button_touched(robot):
    global HAS_COLLIDED 
    HAS_COLLIDED = True

# EITHER BUMPER
@event(robot.when_bumped, [True, True])  # [left, right]
async def when_either_bumped(robot):
    global HAS_COLLIDED 
    HAS_COLLIDED = True

# ==========================================================
# Helper Functions

def createMazeDict(nXCells, nYCells, cellDim):
    mazeDict = {}
    for t in range(nXCells):
        for b in range(nYCells):
            mazeDict[(t, b)] = {'position': (t*cellDim, b*cellDim), 'neighbors': [], 'visited': False, 'cost': 0}
    return mazeDict

def addAllNeighbors(mazeDict, nXCells, nYCells):
    for currPos, currPosDict in mazeDict.items():
        t, b = currPos
        if (t-1, b) in mazeDict:
            currPosDict['neighbors'].append((t-1, b))
        if (t, b+1) in mazeDict:
            currPosDict['neighbors'].append((t, b+1))
        if (t+1, b) in mazeDict:
            currPosDict['neighbors'].append((t+1, b))
        if (t, b-1) in mazeDict:
            currPosDict['neighbors'].append((t, b-1))
    return mazeDict

def getRobotOrientation(heading):
    while heading > 360:
        heading -= 360
    if 0 <= heading <= 45 or 315 < heading <= 360:
        return "E"
    elif 45 < heading <= 135:
        return "N"
    elif 135 < heading <= 225:
        return "W"
    elif 225 < heading <= 315:
        return "S"

def getPotentialNeighbors(currentCell, direction):
    (t, b) = currentCell
    if direction == "N":
        return [(t-1, b), (t, b+1), (t+1, b), (t, b-1)]
    elif direction == "S":
        return [(t+1, b), (t, b-1), (t-1, b), (t, b+1)]
    elif direction == "E":
        return [(t, b+1), (t+1, b), (t, b-1), (t-1, b)]
    elif direction == "W":
        return [(t, b-1), (t-1, b), (t, b+1), (t+1, b)]

def isValidCell(cellIndices, nXCells, nYCells):
    (x, y) = cellIndices
    if 0 <= x < nXCells and 0 <= y < nYCells:
        return True
    else:
        return False
    
def getWallConfiguration(IR0, IR3, IR6, threshold):
    wList = []
    if 4095/(IR0+1) >= threshold:
        wList.append(False)
    else:
        wList.append(True)
    if 4095/(IR3+1) >= threshold:
        wList.append(False)
    else:
        wList.append(True)
    if 4095/(IR6+1) >= threshold:
        wList.append(False)
    else:
        wList.append(True)
    return wList

def getNavigableNeighbors(wallsAroundCell, potentialNeighbors, prevCell, nXCells, nYCells):
    if not prevCell == None:
        nList = [prevCell]
    else:
        nList = []
    for t, b in enumerate(wallsAroundCell):
        if not b and isValidCell(potentialNeighbors[t], nXCells, nYCells):
            nList.append(potentialNeighbors[t])
    return nList

def updateMazeNeighbors(mazeDict, currentCell, navNeighbors):
    for cell, cellDict in mazeDict.items():
        if currentCell in cellDict["neighbors"]:
            if cell not in navNeighbors:
                index = cellDict["neighbors"].index(currentCell)
                del cellDict["neighbors"][index]           
    mazeDict[currentCell]["neighbors"] = navNeighbors
    return mazeDict

def getNextCell(mazeDict, currentCell):
    lowestCost = 10000000000
    lowestCell = ()
    for t in mazeDict[currentCell]["neighbors"]:
        if mazeDict[t]['visited'] == False and mazeDict[t]['cost'] < lowestCost:
            lowestCost = mazeDict[t]['cost']
            lowestCell = t
    if lowestCell == ():
        for t in mazeDict[currentCell]["neighbors"]:
            if mazeDict[t]['cost'] < lowestCost:
                lowestCost = mazeDict[t]['cost']
                lowestCell = t
    return lowestCell

def checkCellArrived(currentCell, destination):
    if currentCell == destination:
        return True
    return False

def printMazeGrid(mazeDict, nXCells, nYCells, attribute):
    for y in range(nYCells - 1, -1, -1):
        row = '| '
        for x in range(nXCells):
            cell_value = mazeDict[(x, y)][attribute]
            row += '{} | '.format(cell_value)
        print(row[:-1])

def updateMazeCost(mazeDict, start, goal):
    for (i,j) in mazeDict.keys():
        mazeDict[(i,j)]["flooded"] = False

    queue = deque([goal])
    mazeDict[goal]['cost'] = 0
    mazeDict[goal]['flooded'] = True

    while queue:
        current = queue.popleft()
        current_cost = mazeDict[current]['cost']

        for neighbor in mazeDict[current]['neighbors']:
            if not mazeDict[neighbor]['flooded']:
                mazeDict[neighbor]['flooded'] = True
                mazeDict[neighbor]['cost'] = current_cost + 1
                queue.append(neighbor)

    return mazeDict

# === BUILD MAZE DICTIONARY

MAZE_DICT = createMazeDict(N_X_CELLS, N_Y_CELLS, CELL_DIM)
MAZE_DICT = addAllNeighbors(MAZE_DICT, N_X_CELLS, N_Y_CELLS)



# ==========================================================
# EXPLORATION AND NAVIGATION

# === EXPLORE MAZE
async def navigateToNextCell(robot, nextCell, orientation):
    global MAZE_DICT, PREV_CELL, CURR_CELL, CELL_DIM

    neighborList = getPotentialNeighbors(CURR_CELL, orientation)
    nextCellIndex = neighborList.index(nextCell)

# [left is 0, front is 1, right is 2, back is 3]
    if nextCellIndex == 0:
        await robot.turn_left(90)
        await robot.move(CELL_DIM)
    elif nextCellIndex == 1:
        await robot.move(CELL_DIM)
    elif nextCellIndex == 2:
        await robot.turn_right(90)
        await robot.move(CELL_DIM)
    elif nextCellIndex == 3:
        await robot.turn_right(180)
        await robot.move(CELL_DIM)

    MAZE_DICT[CURR_CELL]["visited"] = True
    PREV_CELL = CURR_CELL
    CURR_CELL = nextCell
    

@event(robot.when_play)
async def navigateMaze(robot):
    global HAS_COLLIDED, HAS_ARRIVED
    global PREV_CELL, CURR_CELL, START, DESTINATION
    global MAZE_DICT, N_X_CELLS, N_Y_CELLS, CELL_DIM, WALL_THRESHOLD

    await robot.reset_navigation()
    
    while HAS_COLLIDED == False:
        
        IR = (await robot.get_ir_proximity()).sensors
        pos = await robot.get_position()

        if checkCellArrived(CURR_CELL, DESTINATION):
            await robot.set_wheel_speeds(0,0)
            await robot.set_lights_spin_rgb(0, 255, 0)
            break

#_________________(THE MAIN)_________________________________________________________

        orientation = getRobotOrientation(pos.heading)
        
        potentialNeighbors = getPotentialNeighbors(CURR_CELL, orientation)

        wallsAroundCell = getWallConfiguration(IR[0], IR[3], IR[6], WALL_THRESHOLD)

        navNeighbors = getNavigableNeighbors(wallsAroundCell, potentialNeighbors, PREV_CELL, N_X_CELLS, N_Y_CELLS)

        MAZE_DICT = updateMazeNeighbors(MAZE_DICT, CURR_CELL, navNeighbors)

        MAZE_DICT = updateMazeCost(MAZE_DICT, START, DESTINATION)

        nextCell = getNextCell(MAZE_DICT, CURR_CELL)
        
        await navigateToNextCell(robot, nextCell, orientation)
#_____________________________________________________________________________________
        
        if HAS_COLLIDED == True:
            await robot.set_wheel_speeds(0,0)
            await robot.set_lights_rgb(255, 0, 0)
        

robot.play()
