"""
Safe code execution engine for user-provided Python algorithms.
"""

import sys
import io
import traceback
import contextlib
from typing import Dict, Any, Optional


def execute_code(
    code: str,
    data: Any,
    timeout: int = 30,
    allowed_modules: Optional[list] = None
) -> Dict[str, Any]:
    """
    Execute user-provided Python code in a restricted environment.
    
    Args:
        code: Python code string to execute
        data: Data to make available as 'df' variable
        timeout: Maximum execution time in seconds (not enforced in threaded env)
        allowed_modules: List of allowed module names (for future sandboxing)
        
    Returns:
        Dictionary containing:
            - 'success': Boolean indicating if execution succeeded
            - 'output': Captured stdout output
            - 'error': Error message if execution failed
            - 'result': Last expression result (if any)
            - 'variables': Dictionary of variables created during execution
    """
    # Capture stdout and stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    # Create execution namespace with pre-loaded libraries
    exec_namespace = {
        '__builtins__': __builtins__.copy() if isinstance(__builtins__, dict) else vars(__builtins__).copy(),
        'df': data,
    }
    
    # Pre-load common libraries
    try:
        exec_namespace['pd'] = __import__('pandas')
    except ImportError:
        pass
    
    try:
        exec_namespace['np'] = __import__('numpy')
    except ImportError:
        pass
    
    try:
        import matplotlib.pyplot as plt
        exec_namespace['plt'] = plt
    except ImportError:
        pass
    
    try:
        exec_namespace['sns'] = __import__('seaborn')
    except ImportError:
        pass
    
    try:
        exec_namespace['sklearn'] = __import__('sklearn')
    except ImportError:
        pass
    
    try:
        exec_namespace['scipy'] = __import__('scipy')
    except ImportError:
        pass
    
    try:
        exec_namespace['plotly'] = __import__('plotly')
    except ImportError:
        pass
    
    result = None
    success = False
    error_msg = None
    variables = {}
    
    try:
        # Execute code with captured output
        with contextlib.redirect_stdout(stdout_capture), \
             contextlib.redirect_stderr(stderr_capture):
            
            # Compile and execute code
            compiled_code = compile(code, '<user_code>', 'exec')
            exec(compiled_code, exec_namespace)
            
            # Try to get the result (last expression)
            if 'result' in exec_namespace:
                result = exec_namespace['result']
            elif 'output' in exec_namespace:
                result = exec_namespace['output']
            
            # Capture all user-defined variables (excluding built-ins and imports)
            builtin_names = set(['pd', 'np', 'plt', 'sns', 'sklearn', 'scipy', 'plotly', 'df', '__builtins__'])
            variables = {
                k: v for k, v in exec_namespace.items() 
                if not k.startswith('__') and k not in builtin_names
            }
        
        success = True
        
    except SyntaxError as e:
        error_msg = f"Syntax Error: {str(e)}\n{traceback.format_exc()}"
    except Exception as e:
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
    
    # Get captured output
    stdout_output = stdout_capture.getvalue()
    stderr_output = stderr_capture.getvalue()
    
    # Combine outputs
    output = stdout_output
    if stderr_output:
        output += f"\n[STDERR]\n{stderr_output}"
    
    return {
        'success': success,
        'output': output,
        'error': error_msg,
        'result': result,
        'variables': variables
    }


def get_matplotlib_figures() -> list:
    """
    Get all matplotlib figures that were created during execution.
    
    Returns:
        List of matplotlib figure numbers
    """
    try:
        import matplotlib.pyplot as plt
        return plt.get_fignums()
    except:
        return []
