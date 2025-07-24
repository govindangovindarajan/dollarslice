from dollarslice import solve, final_answer, create_simple_llm
from glob import glob
import os

def get_boxes() -> list[str]:
    '''Get all potential boxes'''
    return ['box1', 'box2', 'box3']

def check_box(box : str) -> str:
    '''Check contents of the box'''
    boxes = {
        'box1': 'apple',
        'box2': 'sandwich', 
        'box3': 'water'
    }
    return boxes.get(box, 'empty')

@final_answer
def answer_box(box: str,reason: str):
    '''Give the final answer to the question, pick a single box'''
    return (box,reason)

result,_ = solve(
    task_id="hungry_box_problem",
    task="I'm {feeling}, which box should I pick",
    inputs={"feeling":"hungry"},
    functions=[get_boxes,check_box,answer_box],
    llm_call=create_simple_llm(),
    save=True
)

print(result)