import sys
import io
import contextlib
import signal
import time
from threading import Thread
import queue
import traceback
import json

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Code execution timed out")

def run_test_cases(code, function_name, test_cases, timeout=5):
    """Run code against test cases and return results"""
    results = []
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases):
        result = {
            'test_number': i + 1,
            'description': test_case.get('description', f'Test {i + 1}'),
            'input': test_case['input'],
            'expected': test_case['expected'],
            'actual': None,
            'passed': False,
            'error': None,
            'execution_time': 0
        }
        
        try:
            start_time = time.time()
            actual_result = execute_function_with_test(code, function_name, test_case['input'], timeout)
            execution_time = time.time() - start_time
            
            result['execution_time'] = round(execution_time * 1000, 2)  # Convert to milliseconds
            
            if actual_result['success']:
                result['actual'] = actual_result['output']
                
                # Compare results (handle floating point precision)
                if isinstance(test_case['expected'], float) and isinstance(actual_result['output'], (int, float)):
                    result['passed'] = abs(float(actual_result['output']) - test_case['expected']) < 1e-9
                else:
                    result['passed'] = actual_result['output'] == test_case['expected']
                
                if result['passed']:
                    passed += 1
            else:
                result['error'] = actual_result['error']
                result['actual'] = f"Error: {actual_result['error']}"
                
        except Exception as e:
            result['error'] = str(e)
            result['actual'] = f"Exception: {str(e)}"
        
        results.append(result)
    
    return {
        'results': results,
        'passed': passed,
        'total': total,
        'success_rate': (passed / total * 100) if total > 0 else 0
    }

def execute_function_with_test(code, function_name, test_input, timeout=5):
    """Execute a specific function with given input"""
    result_queue = queue.Queue()
    
    def run_code():
        try:
            # Create a restricted environment
            restricted_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'abs': abs,
                    'max': max,
                    'min': min,
                    'sum': sum,
                    'sorted': sorted,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'bool': bool,
                    'type': type,
                    'isinstance': isinstance,
                    'hasattr': hasattr,
                    'getattr': getattr,
                    'setattr': setattr,
                    'round': round,
                    'pow': pow,
                    'divmod': divmod,
                    'ord': ord,
                    'chr': chr,
                    'bin': bin,
                    'hex': hex,
                    'oct': oct,
                    'all': all,
                    'any': any,
                    'reversed': reversed,
                }
            }
            
            # Create local namespace
            local_namespace = {}
            
            # Execute the code to define functions
            exec(code, restricted_globals, local_namespace)
            
            # Check if the required function exists
            if function_name not in local_namespace:
                result_queue.put({
                    'success': False,
                    'output': None,
                    'error': f'Function "{function_name}" not found. Make sure you define a function with this exact name.'
                })
                return
            
            # Get the function
            func = local_namespace[function_name]
            
            # Call the function with test input
            if isinstance(test_input, list):
                if len(test_input) == 0:
                    # No arguments
                    output = func()
                else:
                    # Unpack arguments
                    output = func(*test_input)
            else:
                # Single argument
                output = func(test_input)
            
            result_queue.put({
                'success': True,
                'output': output,
                'error': None
            })
            
        except TypeError as e:
            if "takes" in str(e) and "positional argument" in str(e):
                result_queue.put({
                    'success': False,
                    'output': None,
                    'error': f'Function signature mismatch: {str(e)}'
                })
            else:
                result_queue.put({
                    'success': False,
                    'output': None,
                    'error': f'Type Error: {str(e)}'
                })
        except Exception as e:
            result_queue.put({
                'success': False,
                'output': None,
                'error': f'{type(e).__name__}: {str(e)}'
            })
    
    # Run code in a separate thread
    thread = Thread(target=run_code)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        return {
            'success': False,
            'output': None,
            'error': 'Function execution timed out'
        }
    
    try:
        return result_queue.get_nowait()
    except queue.Empty:
        return {
            'success': False,
            'output': None,
            'error': 'Unknown execution error'
        }

def execute_code_with_timeout(code, timeout=5):
    """Execute code with timeout protection for general code execution"""
    result_queue = queue.Queue()
    
    def run_code():
        try:
            # Capture stdout and stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = captured_output = io.StringIO()
            sys.stderr = captured_error = io.StringIO()
            
            # Create a restricted environment
            restricted_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'abs': abs,
                    'max': max,
                    'min': min,
                    'sum': sum,
                    'sorted': sorted,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'bool': bool,
                    'type': type,
                    'isinstance': isinstance,
                    'hasattr': hasattr,
                    'getattr': getattr,
                    'setattr': setattr,
                    'round': round,
                    'pow': pow,
                    'divmod': divmod,
                    'ord': ord,
                    'chr': chr,
                    'bin': bin,
                    'hex': hex,
                    'oct': oct,
                    'all': all,
                    'any': any,
                    'reversed': reversed,
                }
            }
            
            # Create local namespace
            local_namespace = {}
            
            # Execute the code
            exec(code, restricted_globals, local_namespace)
            
            # Get output and errors
            output = captured_output.getvalue()
            error_output = captured_error.getvalue()
            
            # Restore stdout and stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            # If there's an error, include it in the output
            if error_output:
                result_queue.put({
                    'success': False, 
                    'output': error_output, 
                    'error': 'Runtime Error'
                })
            else:
                # If no explicit output, show variable values
                if not output.strip():
                    # Look for variables that might contain results
                    result_vars = []
                    for var_name, var_value in local_namespace.items():
                        if not var_name.startswith('_') and var_value is not None:
                            result_vars.append(f"{var_name} = {repr(var_value)}")
                    
                    if result_vars:
                        output = "Variables created:\n" + "\n".join(result_vars)
                    else:
                        output = "Code executed successfully (no output or variables created)"
                
                result_queue.put({'success': True, 'output': output, 'error': None})
            
        except SyntaxError as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            result_queue.put({
                'success': False, 
                'output': f"Syntax Error on line {e.lineno}: {e.msg}", 
                'error': 'Syntax Error'
            })
        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            error_msg = f"{type(e).__name__}: {str(e)}"
            result_queue.put({
                'success': False, 
                'output': error_msg, 
                'error': type(e).__name__
            })
    
    # Run code in a separate thread
    thread = Thread(target=run_code)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        return {'success': False, 'output': 'Code execution timed out (5 seconds limit)', 'error': 'Timeout'}
    
    try:
        return result_queue.get_nowait()
    except queue.Empty:
        return {'success': False, 'output': 'Unknown error occurred', 'error': 'Unknown Error'}

def execute_code(code):
    """Main code execution function for general code testing"""
    if not code.strip():
        return {'success': False, 'output': 'No code provided', 'error': 'Empty Code'}
    
    # Check for dangerous imports/functions
    dangerous_patterns = [
        'import os', 'import sys', 'import subprocess', 'import socket',
        'import urllib', 'import requests', 'import shutil', 'import glob',
        'open(', 'file(', 'input(', 'raw_input(', '__import__',
        'eval(', 'compile(', 'exec('
    ]
    
    for pattern in dangerous_patterns:
        if pattern in code:
            return {
                'success': False, 
                'output': f'Restricted operation detected: {pattern}', 
                'error': f'Security: {pattern} not allowed'
            }
    
    return execute_code_with_timeout(code)

def test_code_with_cases(code, function_name, test_cases):
    """Test code against specific test cases"""
    if not code.strip():
        return {
            'success': False,
            'message': 'No code provided',
            'results': [],
            'passed': 0,
            'total': 0,
            'success_rate': 0
        }
    
    # Check for dangerous imports/functions
    dangerous_patterns = [
        'import os', 'import sys', 'import subprocess', 'import socket',
        'import urllib', 'import requests', 'import shutil', 'import glob',
        'open(', 'file(', 'input(', 'raw_input(', '__import__',
        'eval(', 'compile(', 'exec('
    ]
    
    for pattern in dangerous_patterns:
        if pattern in code:
            return {
                'success': False,
                'message': f'Restricted operation detected: {pattern}',
                'results': [],
                'passed': 0,
                'total': len(test_cases),
                'success_rate': 0
            }
    
    try:
        test_results = run_test_cases(code, function_name, test_cases)
        return {
            'success': True,
            'message': f'Tests completed: {test_results["passed"]}/{test_results["total"]} passed',
            'results': test_results['results'],
            'passed': test_results['passed'],
            'total': test_results['total'],
            'success_rate': test_results['success_rate']
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error running tests: {str(e)}',
            'results': [],
            'passed': 0,
            'total': len(test_cases),
            'success_rate': 0
        }
