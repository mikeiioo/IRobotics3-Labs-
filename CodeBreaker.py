#Michael Abraham
#GTID: 903982906


from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, hand_over, Color, Robot, Root, Create3
from irobot_edu_sdk.music import Note

robot = Root(Bluetooth())  # Will connect to the first robot found.

CORRECT_CODE = "341124"
current_code = ""

# LEFT BUTTON
@event(robot.when_touched, [True, False])  # User buttons: [(.), (..)]
async def when_left_button_touched(robot):
    global current_code  
    current_code += "1"
    await robot.play_note(Note.C5, 1)
    await checkUserCode(robot)



# RIGHT BUTTON
@event(robot.when_touched, [False, True])  # User buttons: [(.), (..)]
async def when_right_button_touched(robot):
    global current_code
    current_code += "2"
    await robot.play_note(Note.D5, 1)
    await checkUserCode(robot)


# LEFT BUMP
@event(robot.when_bumped, [True, False])  # [left, right]
async def when_left_bumped(robot):
    global current_code
    current_code += "3"
    await robot.play_note(Note.E5, 1)
    await checkUserCode(robot)


# RIGHT BUMP
@event(robot.when_bumped, [False, True])  # [left, right]
async def when_right_bumped(robot):
    global current_code
    current_code += "4"
    await robot.play_note(Note.F5, 1)
    await checkUserCode(robot)


async def checkUserCode(robot):
    global current_code

    print(current_code)
    
    if current_code == CORRECT_CODE:
        await robot.play_note(Note.C5, 1)
        await robot.play_note(Note.D5, 1)
        await robot.play_note(Note.E5, 1)
        await robot.play_note(Note.G6, 1)
        await robot.set_lights_rgb(0, 255, 0)  
        await robot.set_wheel_speeds(10,-10) 
        await robot.wait(10)  
        await robot.set_wheel_speeds(0,0)
        await robot.set_lights_rgb(0, 0, 255) 
        current_code = "" 
    elif len(current_code) == len(CORRECT_CODE):
        current_code = ""  
        await robot.play_note(Note.A5, 1)
        await robot.set_lights_rgb(255, 0, 0)
        await robot.wait(2)  
        await robot.set_lights_rgb(0, 0, 255)  



@event(robot.when_play)
async def play(robot):
    print("Succesfully Installed")
    await robot.set_lights_rgb(0, 0, 255)  


robot.play()

  
