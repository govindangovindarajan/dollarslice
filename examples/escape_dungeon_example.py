import os
from dollarslice import solve, final_answer, create_simple_llm
from typing import List

empty_spaces = 2
steps_taken_forward = 0
orientation = 0

def look_ahead() -> str:
    global steps_taken_forward, orientation, empty_spaces
    if steps_taken_forward == empty_spaces:
        if orientation != 1:
            return 'Wall'
        else:
            return 'Exit!'
    else:
        if orientation==0:
            return 'Empty Space'
        else:
            return 'Wall'

def move_forward() -> str:
    global steps_taken_forward, orientation, empty_spaces
    if orientation==0 and steps_taken_forward < empty_spaces:
        steps_taken_forward +=1
        return 'Moved one space forward'
    if orientation==1 and steps_taken_forward == empty_spaces:
        return 'You have escaped'
    return 'You bumped your face in the wall'

def turn_left() -> str:
    global orientation
    orientation = (orientation+1)%4
    return 'You turned left'

def turn_right() -> str:
    global orientation
    orientation = (orientation+3)%4
    return 'You turned right'

@final_answer
def final_answer(action_sequence: List[str], reason: str):
    '''IMPORTANT: Call this function to return the final action sequence. You MUST call this function with the exact sequence of action names once you have successfully escaped the dungeon. The action_sequence should be a list of strings containing the function names in order.'''
    return (action_sequence, reason)

result,_ = solve(
    task_id="dungeon_escape_problem",
    task="I am stuck in a 2D dungeon, I have to escape! Find the sequence of actions to escape and then call final_answer() with the list of action names. Example: final_answer(['look_ahead', 'move_forward', 'turn_left', 'move_forward'], 'explanation')",
    inputs={},
    functions=[look_ahead,move_forward,turn_left,turn_right,final_answer],
    llm_call=create_simple_llm(),
    save=True,
    call_limit=50
)
print(result)
