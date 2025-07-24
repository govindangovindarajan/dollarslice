import os
import pickle
import json
from datetime import datetime

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    
    @staticmethod
    def colored(text, color):
        return f"{color}{text}{Colors.RESET}"

def list_tasks():
    """List all available problem directories in .dollar_slice"""
    base_dir = os.environ.get("DOLLAR_SLICE_SAVE_LOC", ".dollar_slice")
    if not os.path.exists(base_dir):
        return []
    
    try:
        tasks = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
        return tasks
    except (OSError, PermissionError):
        return []

def list_task_files(task_id: str):
    """List all pickle files for a specific problem with timestamps"""
    base_dir = os.environ.get("DOLLAR_SLICE_SAVE_LOC", ".dollar_slice")
    task_dir = os.path.join(base_dir, task_id)
    
    if not os.path.exists(task_dir):
        return []
    
    files = []
    try:
        for f in os.listdir(task_dir):
            if f.endswith('.pkl'):
                file_path = os.path.join(task_dir, f)
                mtime = os.path.getmtime(file_path)
                timestamp = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                files.append((f[:-4], timestamp))
    except (OSError, PermissionError):
        return []
    
    # Sort by timestamp (newest first)
    files.sort(key=lambda x: x[1], reverse=True)
    return files


def interactive_mode():
    """Interactive mode for browsing and viewing problem data"""
    # Fast check - exit immediately if no problems
    problems = list_tasks()
    if not problems:
        print(Colors.colored("No problems available", Colors.RED))
        return
    
    while True:
        print(Colors.colored("Saved Solutions:", Colors.GREEN + Colors.BOLD))
        for i, problem in enumerate(problems, 1):
            print(f"{i}. {Colors.colored(problem, Colors.CYAN)}")
        
        try:
            choice = int(input("Select problem number: ")) - 1
            if 0 <= choice < len(problems):
                selected_problem = problems[choice]
                files = list_task_files(selected_problem)
                
                if not files:
                    print(Colors.colored(f"No files found for problem: {selected_problem}", Colors.RED))
                    continue
                
                print(f"\n{Colors.colored(f'Files for {selected_problem}:', Colors.GREEN + Colors.BOLD)}")
                for i, (file_id, timestamp) in enumerate(files, 1):
                    print(f"{i}. {Colors.colored(file_id, Colors.CYAN)} {Colors.colored(f'({timestamp})', Colors.DIM)}")
                
                file_choice = int(input("Select file number: ")) - 1
                if 0 <= file_choice < len(files):
                    load_and_print(selected_problem, files[file_choice][0])
                else:
                    print(Colors.colored("Invalid file selection", Colors.RED))
            else:
                print(Colors.colored("Invalid problem selection", Colors.RED))
        except KeyboardInterrupt:
            print()  # Print newline before exit
            break
        except ValueError:
            print(Colors.colored("Please enter a valid number", Colors.RED))
        
        # Refresh problems list for next iteration
        problems = list_tasks()

def load_and_print(task_id: str, id: str):
    base_dir = os.environ.get("DOLLAR_SLICE_SAVE_LOC", ".dollar_slice")
    file_path = os.path.join(base_dir, task_id, f"{id}.pkl")
    
    if not os.path.isfile(file_path):
        print(Colors.colored(f"File not found: {file_path}", Colors.RED))
        return

    try:
        # Get file timestamp
        mtime = os.path.getmtime(file_path)
        timestamp = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

        with open(file_path, "rb") as f:
            data = pickle.load(f)

        # Print header info
        print(f"\n{Colors.colored('=' * 60, Colors.BLUE)}")
        print(f"{Colors.colored('Task ID:', Colors.GREEN + Colors.BOLD)} {data['task_id']}")
        print(f"{Colors.colored('ID:', Colors.CYAN + Colors.BOLD)} {data['id']}")
        print(f"{Colors.colored('Timestamp:', Colors.MAGENTA + Colors.BOLD)} {timestamp}")
        print(f"{Colors.colored('Task:', Colors.YELLOW + Colors.BOLD)} {data['task']}")
        print(f"{Colors.colored('=' * 60, Colors.BLUE)}")
        
        # Print inputs
        print(f"\n{Colors.colored('INPUTS:', Colors.MAGENTA + Colors.BOLD)}")
        print(format_data(data['inputs']))
        
        # Print functions
        print(f"\n{Colors.colored('FUNCTIONS:', Colors.BLUE + Colors.BOLD)}")
        print(format_data(data['functions']))
        
        # Print steps
        print_steps(data['steps'])
    except (OSError, PermissionError, pickle.PickleError) as e:
        print(Colors.colored(f"Error loading file: {e}", Colors.RED))

def format_data(data):
    """Format data structures for readable display"""
    if isinstance(data, dict):
        if not data:
            return Colors.colored("  (empty)", Colors.DIM)
        result = ""
        for key, value in data.items():
            result += f"  {Colors.colored(str(key), Colors.CYAN)}: {str(value)}\n"
        return result.rstrip()
    elif isinstance(data, list):
        if not data:
            return Colors.colored("  (empty)", Colors.DIM)
        result = ""
        for i, item in enumerate(data):
            if isinstance(item, (tuple, list)) and len(item) >= 4:
                # Function signature format: name, params, ret_type, desc
                name, params, ret_type, desc = item[:4]
                result += f"  {Colors.colored(name, Colors.BOLD)}({params}) -> {ret_type}\n"
                result += f"    {Colors.colored(desc, Colors.DIM)}\n"
            else:
                result += f"  {i+1}. {str(item)}\n"
        return result.rstrip()
    else:
        return f"  {str(data)}"

def print_steps(steps):
    for idx, step in enumerate(steps):
        step_type = step[0]
        print(f"\n{Colors.colored('─' * 60, Colors.MAGENTA)}")
        print(f"{Colors.colored(f'Step {idx + 1}: {step_type.upper()}', Colors.MAGENTA + Colors.BOLD)}")
        print(f"{Colors.colored('─' * 60, Colors.MAGENTA)}")

        if step_type == "llm":
            messages, functions, trace = step[1:]
            
            print(f"\n{Colors.colored('LLM Messages:', Colors.CYAN + Colors.BOLD)}")
            for msg in messages:
                role = msg.get("role", "system")
                content = msg.get("content", "")
                tool_calls = msg.get("tool_calls", [])
                
                role_color = Colors.GREEN if role == "user" else Colors.BLUE if role == "assistant" else Colors.YELLOW
                print(f"{Colors.colored(f'({role}):', role_color + Colors.BOLD)} {content}")
                
                if tool_calls:
                    for t in tool_calls:
                        func_name = t['function']['name']
                        func_args = t['function']['arguments']
                        print(f"  {Colors.colored('Tool Call:', Colors.DIM)} [{func_name}] {func_args}")

            print(f"\n{Colors.colored('Function Signatures:', Colors.GREEN + Colors.BOLD)}")
            for func in functions:
                name, params, ret_type, desc = func
                print(f"  {Colors.colored(name, Colors.BOLD)}({params}) -> {ret_type}")
                print(f"    {Colors.colored(desc, Colors.DIM)}")

            print(f"\n{Colors.colored('Trace Info:', Colors.YELLOW + Colors.BOLD)}")
            print(format_data(trace))

        elif step_type == "function":
            _, name, args, result, trace = step
            
            print(f"\n{Colors.colored(f'Function Call: {name}', Colors.BLUE + Colors.BOLD)}")
            
            if args:
                print(f"{Colors.colored('Arguments:', Colors.CYAN)}")
                for k, v in args.items():
                    print(f"  {Colors.colored(k, Colors.CYAN)}: {str(v)}")
            
            print(f"\n{Colors.colored('Returned:', Colors.GREEN + Colors.BOLD)} {result}")
            
            if trace and 'start_time' in trace and 'end_time' in trace:
                print(f"{Colors.colored('Timing:', Colors.DIM)} {trace['start_time']} → {trace['end_time']}")
        else:
            print(format_data(step))

def main():
    """Main function - always starts in interactive mode"""
    interactive_mode()

if __name__ == "__main__":
    main()