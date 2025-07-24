import os
import json
import httpx
from datetime import datetime
from typing import TypedDict, List, Callable, Any, Dict

from .utils import func_to_tool_json, func_to_one_liner

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class FunctionResult(TypedDict):
    id: str
    name: str
    output: Any
    arguments: Dict

class CallMetrics(TypedDict):
    total_tokens: int
    start_time: datetime
    end_time: datetime

LLMCall = Callable[[List, List[Callable], List[FunctionResult]], tuple[list, list, CallMetrics]]

def make_llm_call(messages: List[Dict], functions: List = None) -> Dict:
    """Auto-detect provider from env vars and make LLM call"""
    if os.getenv('OPENAI_API_KEY'):
        return openai_call(messages, functions)
    elif os.getenv('GROQ_API_KEY'):  
        return groq_call(messages, functions)
    elif os.getenv('ANTHROPIC_API_KEY'):
        return anthropic_call(messages, functions)
    else:
        raise ValueError("No API key found")

def openai_call(messages: List[Dict], functions: List = None) -> Dict:
    """Direct HTTP call to OpenAI API"""
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': model,
        'messages': messages,
        'temperature': 0
    }
    
    if functions:
        data['tools'] = functions
        data['tool_choice'] = 'auto'
    
    with httpx.Client() as client:
        response = client.post(
            f'{base_url}/chat/completions',
            headers=headers,
            json=data,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()

def groq_call(messages: List[Dict], functions: List = None) -> Dict:
    """Direct HTTP call to Groq API (OpenAI-compatible)"""
    api_key = os.getenv('GROQ_API_KEY')
    base_url = os.getenv('GROQ_BASE_URL', 'https://api.groq.com/openai/v1')
    model = os.getenv('GROQ_MODEL', 'llama3-8b-8192')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': model,
        'messages': messages,
        'temperature': 0
    }
    
    if functions:
        data['tools'] = functions
        data['tool_choice'] = 'auto'
    
    with httpx.Client() as client:
        response = client.post(
            f'{base_url}/chat/completions',
            headers=headers,
            json=data,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()

def anthropic_call(messages: List[Dict], functions: List = None) -> Dict:
    """Direct HTTP call to Anthropic API"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    base_url = os.getenv('ANTHROPIC_BASE_URL', 'https://api.anthropic.com/v1')
    model = os.getenv('ANTHROPIC_MODEL', 'claude-3-haiku-20240307')
    
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
    }
    
    # Convert OpenAI format to Anthropic format
    system_message = None
    anthropic_messages = []
    
    for msg in messages:
        if msg['role'] == 'system':
            system_message = msg['content']
        else:
            anthropic_messages.append(msg)
    
    data = {
        'model': model,
        'max_tokens': 1024,
        'messages': anthropic_messages
    }
    
    if system_message:
        data['system'] = system_message
    
    if functions:
        data['tools'] = functions
    
    with httpx.Client() as client:
        response = client.post(
            f'{base_url}/messages',
            headers=headers,
            json=data,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()

def create_simple_llm() -> LLMCall:
    def call(messages : List, functions : List[Callable], function_results : List[FunctionResult]) -> tuple[list,list,CallMetrics]:
        start = datetime.now()
        for function_result in function_results:
            function_output = function_result["output"]
            if type(function_output) not in (list,dict):
                formatted_output = str(function_output)
            else:
                formatted_output = json.dumps(function_output)
            message = {
                "tool_call_id": function_result["id"],
                "role": "tool",
                "name": function_result["name"],
                "content": formatted_output
            }
            messages += [message]
        tools = [func_to_tool_json(fn) for fn in functions]
        response = make_llm_call(messages, tools)
        response_message = response['choices'][0]['message']
        tool_calls = response_message.get('tool_calls')
        updated_messages = messages
        if response_message:
            updated_messages += [response_message]
        tool_results = []
        if tool_calls:
            for tool_call in tool_calls:
                tool_results+=[(tool_call['function']['name'],json.loads(tool_call['function']['arguments']),tool_call['id'])]
        end = datetime.now()
        call_metrics: CallMetrics = {
            "total_tokens": response['usage']['total_tokens'],
            "start_time": start,
            "end_time": end
        }
        return updated_messages,tool_results,call_metrics
    return call

def create_from_ollama(model, url="http://localhost:11434/api/generate") -> LLMCall:
    def call(messages: List, functions: List[Callable], function_results: List[FunctionResult]) -> tuple[list, list, CallMetrics]:
        start = datetime.now()
        
        user_query = None
        tool_calls = []
        for message in messages:
            if message['role'] == 'user':
                user_query = message['content']
            if message['role'] == 'tool':
                tool_calls.append(f"{len(tool_calls)+1} {message['name']}{message.get('arguments', '')} -> {message['content']}")
        
        for function_result in function_results:
            function_output = function_result["output"]
            formatted_output = str(function_output) if type(function_output) not in (list, dict) else json.dumps(function_output)
            tool_calls.append(f"{len(tool_calls)+1} {function_result['name']}{function_result.get('arguments', '')} -> {formatted_output}")
        
        prompt = f"""### User: {user_query}

### System:

Previous function calls:
{chr(10).join(tool_calls)}

Produce JSON OUTPUT ONLY! Adhere to this format {{"name": "function_name", "arguments":{{"argument_name": "argument_value"}}}} The following functions are available to you:
{chr(10).join([func_to_one_liner(function) for function in functions])}"""
        
        data = {
            "model": model,
            "raw": True,
            "prompt": prompt,
            "options": {'temperature': 0.1},
            "stream": False,
            "format": "json"
        }
        
        with httpx.Client() as client:
            http_response = client.post(url, json=data, timeout=30.0)
        raw_input = http_response.json()['response']
        
        decoder = json.JSONDecoder()
        try:
            response, _ = decoder.raw_decode(raw_input, raw_input.find('{'))
        except (json.JSONDecodeError, ValueError):
            start_idx = raw_input.find('{')
            end_idx = raw_input.rfind('}') + 1
            response = json.loads(raw_input[start_idx:end_idx])
        tool_results = [(response['name'], response['arguments'], 'ollama_call')]
        
        end = datetime.now()
        call_metrics: CallMetrics = {
            "total_tokens": 0,
            "start_time": start,
            "end_time": end
        }
        
        return messages, tool_results, call_metrics
    
    return call