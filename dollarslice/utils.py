import inspect
from typing import get_type_hints

def describe_function(fn):
    sig = inspect.signature(fn)
    hints = get_type_hints(fn)
    name = fn.__name__
    params = {}
    for name_, param in sig.parameters.items():
        param_type = hints.get(name_, str(param.annotation)) if param.annotation != inspect._empty else "Any"
        params[name_] = str(param_type)
    return_type = hints.get("return", sig.return_annotation)
    return_type = str(return_type) if return_type != inspect._empty else "None"
    docstring = inspect.getdoc(fn) or ""
    return name, params, return_type, docstring

def format_for_openai_tool(description_tuple):
    name, params, return_type, docstring = description_tuple
    properties = {}
    required = []
    for param_name, param_type in params.items():
        required.append(param_name)
        if "int" in param_type or "float" in param_type or "number" in param_type:
            t = "number"
        elif "str" in param_type:
            t = "string"
        else:
            t = "string"
        properties[param_name] = {"type": t}
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": docstring+", returns a "+return_type,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    }

def func_to_tool_json(x):
    return format_for_openai_tool(describe_function(x))

def func_to_one_liner(x):
    name, params, _, docstring = describe_function(x)
    return name+str(params)+' -> '+docstring

def func_map(x):
    return x.__name__,x
