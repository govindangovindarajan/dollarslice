import copy
import os
import pickle
import uuid
from datetime import datetime

from .utils import func_map, describe_function

def final_answer(func):
    func._is_final_answer = True
    return func

def solution_already_baked(name) -> bool:
    return False

def execute_baked_solution(task : str,inputs : dict, functions : list, llms : list,*args, **kwargs) -> tuple[str,str]:
    return 'Oh','Pizza'

def save_steps(task_id: str, id: str, task: str, inputs: dict, functions: list, steps: list):
    base_dir = os.environ.get("DOLLAR_SLICE_SAVE_LOC",'.dollar_slice')
    os.makedirs(base_dir, exist_ok=True)
    task_dir = os.path.join(base_dir, task_id)
    os.makedirs(task_dir, exist_ok=True)
    file_path = os.path.join(task_dir, f"{id}.pkl")
    with open(file_path, "wb") as f:
        pickle.dump({
            "task_id": task_id,
            "id": id,
            "task": task,
            "inputs": inputs,
            "functions": [describe_function(f) for f in functions],
            "steps": steps
        }, f)

def solve(task_id : str, task : str,inputs : dict, functions : list, llm_call, save=False,*args, **kwargs) -> tuple[str,str]:
    id = uuid.uuid4().hex
    if solution_already_baked(task):
        return execute_baked_solution(task,inputs,functions,llm_call,args,kwargs)
    final_result,answer_generated,steps = blind_solve(task,inputs,functions,llm_call)
    if save:
        save_steps(task_id, id,task,inputs,functions,steps)
    return final_result,answer_generated

def is_final_answer_function(function):
    return getattr(function, '_is_final_answer', False)


def filter_final_functions(functions):
    return [f for f in functions if is_final_answer_function(f)]

def blind_solve(task : str,inputs : dict, functions : list, llm_call,*args, **kwargs) -> tuple[str,str]:

    for key in inputs:
        task = task.replace('{'+key+'}', inputs[key])
    function_map = dict([func_map(f) for f in functions])
    messages = [{'role':'user','content':task}]
    calls_so_far = 1
    call_limit = kwargs.get('call_limit',10)
    answer_generated = False
    final_result = None
    function_results = []
    steps = []
    while calls_so_far <= call_limit and not answer_generated:
        input_functions = functions
        messages,tool_results,metrics = llm_call(messages=messages,functions=input_functions,function_results=function_results)
        steps += [('llm',copy.deepcopy(messages),[describe_function(f) for f in input_functions],([],tool_results,metrics))]
        function_results = []
        if tool_results:
            for name,args,id in tool_results:
                start = datetime.now()
                function = function_map[name]
                tool_output = function(**args)
                end = datetime.now()
                steps += [('function',name,args,tool_output,{"start_time":start,"end_time":end})]
                function_results += [{"id":id,"name":name,"output":tool_output,"arguments":args}]
                if is_final_answer_function(function):
                    answer_generated = True
                    final_result = tool_output
                    break
        calls_so_far += 1

    return final_result,answer_generated,steps