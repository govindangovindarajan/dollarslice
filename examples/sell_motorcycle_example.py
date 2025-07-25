import os
from dollarslice import solve, final_answer, create_simple_llm

def max_price() -> str:
    '''Get the maximum price you can quote to sell your motorcycle'''
    return '605$'

def min_price() -> str:
    '''Get the minimum price you can quote to sell your motorcycle'''
    return '310$'

@final_answer
def final_answer(amount: int,reason: str):
    '''Give the final answer to the question, pick a reasonable price for the motorcycle'''
    return (amount,reason)

result,_ = solve(
    task_id="sell_motorcycle_problem",
    task="I want to sell my motorcycle, what price should I quote",
    inputs={},
    functions=[max_price,min_price,final_answer],
    llm_call=create_simple_llm(),
    save=True
)

print(result)
