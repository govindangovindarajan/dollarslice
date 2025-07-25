from dollarslice import solve, final_answer, create_simple_llm
import os

def get_boxes() -> list[str]:
    '''Get all visible boxes'''
    return ["box1","box2","box3","box4"]

def check_box(box : str) -> str:
    '''Check contents of the box'''
    d = {"box1":"EMPTY","box2":"EMPTY","box3":"EMPTY","box4":"box5","box5":"sandwich",}
    return d.get(box)

@final_answer
def answer_box(box: str,reason: str):
    '''Give the final answer to the question, pick a single box'''
    return (box,reason)

result,_ = solve(
    task_id="hungry_2box_problem",
    task="I'm {feeling}, which box should I pick",
    inputs={"feeling":"hungry"},
    functions=[get_boxes,check_box,answer_box],
    llm_call=create_simple_llm(),
    save=True
)

print(result)