"""
Parameter parser for detecting adjustable numeric values in Python code.
"""

import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class Parameter:
    """Represents a detected parameter in code."""
    name: str
    value: float
    line_number: int
    original_text: str
    param_type: str  # 'int' or 'float'
    min_value: float = None
    max_value: float = None
    step: float = None
    
    def __post_init__(self):
        """Set default min/max/step based on value and type."""
        if self.min_value is None:
            if self.param_type == 'int':
                self.min_value = max(0, int(self.value) - 100)
            else:
                # For floats, scale based on magnitude
                if abs(self.value) < 1:
                    self.min_value = 0.0
                else:
                    self.min_value = 0.0
        
        if self.max_value is None:
            if self.param_type == 'int':
                self.max_value = max(int(self.value) + 100, int(self.value) * 3)
            else:
                if abs(self.value) < 1:
                    self.max_value = 1.0
                elif abs(self.value) < 10:
                    self.max_value = self.value * 5
                else:
                    self.max_value = self.value * 3
        
        if self.step is None:
            if self.param_type == 'int':
                self.step = 1
            else:
                # Determine step based on value magnitude
                if abs(self.value) < 0.01:
                    self.step = 0.001
                elif abs(self.value) < 0.1:
                    self.step = 0.01
                elif abs(self.value) < 1:
                    self.step = 0.05
                else:
                    self.step = 0.1


# Common ML/data science parameter patterns
PARAMETER_PATTERNS = [
    # Learning rate, alpha, beta, gamma, etc.
    r'^(\s*)([a-z_]*(?:rate|alpha|beta|gamma|epsilon|lambda|eta|momentum|decay))\s*=\s*([0-9]*\.?[0-9]+)',
    # n_xxx parameters (n_clusters, n_estimators, n_neighbors, etc.)
    r'^(\s*)(n_[a-z_]+)\s*=\s*([0-9]+)',
    # max_xxx parameters (max_depth, max_iter, max_features, etc.)
    r'^(\s*)(max_[a-z_]+)\s*=\s*([0-9]+)',
    # min_xxx parameters
    r'^(\s*)(min_[a-z_]+)\s*=\s*([0-9]*\.?[0-9]+)',
    # Common numeric parameters
    r'^(\s*)(epochs?|iterations?|batch_size|hidden_size|num_layers|dropout|threshold|tolerance|k|C|degree)\s*=\s*([0-9]*\.?[0-9]+)',
    # test_size, train_size, split ratios
    r'^(\s*)(test_size|train_size|validation_size|split_ratio|ratio)\s*=\s*([0-9]*\.?[0-9]+)',
    # Random state, seed
    r'^(\s*)(random_state|seed)\s*=\s*([0-9]+)',
    # Generic xxx_size, xxx_count patterns
    r'^(\s*)([a-z_]*(?:_size|_count|_num|_rate|_ratio|_factor|_weight))\s*=\s*([0-9]*\.?[0-9]+)',
]


def detect_parameters(code: str) -> List[Parameter]:
    """
    Detect adjustable numeric parameters in Python code.
    
    Args:
        code: Python code string
        
    Returns:
        List of Parameter objects
    """
    parameters = []
    lines = code.split('\n')
    seen_names = set()
    
    for line_num, line in enumerate(lines, 1):
        # Skip comments and empty lines
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        
        for pattern in PARAMETER_PATTERNS:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                indent, name, value_str = match.groups()
                
                # Skip if we've already seen this parameter name
                if name in seen_names:
                    continue
                seen_names.add(name)
                
                # Determine type
                if '.' in value_str:
                    param_type = 'float'
                    value = float(value_str)
                else:
                    param_type = 'int'
                    value = int(value_str)
                
                # Create the original text for replacement
                original_text = f"{name} = {value_str}"
                
                param = Parameter(
                    name=name,
                    value=value,
                    line_number=line_num,
                    original_text=original_text,
                    param_type=param_type
                )
                
                # Override defaults for specific parameter types
                param = apply_parameter_hints(param)
                
                parameters.append(param)
                break
    
    return parameters


def apply_parameter_hints(param: Parameter) -> Parameter:
    """
    Apply sensible defaults based on parameter name patterns.
    """
    name_lower = param.name.lower()
    
    # Learning rates and small decimals
    if any(x in name_lower for x in ['rate', 'alpha', 'eta', 'epsilon']):
        param.min_value = 0.0001
        param.max_value = 1.0
        param.step = 0.0001 if param.value < 0.01 else 0.001
    
    # Dropout, ratios (0-1 range)
    elif any(x in name_lower for x in ['dropout', 'ratio', 'size']) and param.value <= 1:
        param.min_value = 0.0
        param.max_value = 1.0
        param.step = 0.05
    
    # Iterations, epochs, batch sizes
    elif any(x in name_lower for x in ['epoch', 'iteration', 'batch']):
        param.min_value = 1
        param.max_value = max(1000, int(param.value) * 5)
        param.step = 1 if param.value < 100 else 10
    
    # Tree depth, layers
    elif any(x in name_lower for x in ['depth', 'layer', 'level']):
        param.min_value = 1
        param.max_value = 50
        param.step = 1
    
    # Number of clusters, neighbors, estimators
    elif name_lower.startswith('n_') or name_lower.startswith('num_'):
        param.min_value = 1
        param.max_value = max(100, int(param.value) * 5)
        param.step = 1
    
    # Random state / seed
    elif any(x in name_lower for x in ['random', 'seed']):
        param.min_value = 0
        param.max_value = 9999
        param.step = 1
    
    # Regularization (C, lambda)
    elif name_lower in ['c', 'lambda', 'lambda_']:
        param.min_value = 0.001
        param.max_value = 100.0
        param.step = 0.1
    
    # Momentum, decay, beta
    elif any(x in name_lower for x in ['momentum', 'decay', 'beta', 'gamma']):
        param.min_value = 0.0
        param.max_value = 1.0
        param.step = 0.01
    
    return param


def update_code_with_parameters(code: str, parameters: Dict[str, Any]) -> str:
    """
    Update code with new parameter values.
    
    Args:
        code: Original Python code
        parameters: Dictionary of {param_name: new_value}
        
    Returns:
        Updated code string
    """
    lines = code.split('\n')
    
    for param_name, new_value in parameters.items():
        for i, line in enumerate(lines):
            # Match assignment pattern for this parameter
            pattern = rf'^(\s*)({re.escape(param_name)})\s*=\s*([0-9]*\.?[0-9]+)'
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                indent = match.group(1)
                # Format the new value appropriately
                if isinstance(new_value, float):
                    if new_value == int(new_value):
                        value_str = str(int(new_value))
                    else:
                        value_str = f"{new_value:.6f}".rstrip('0').rstrip('.')
                else:
                    value_str = str(int(new_value))
                
                lines[i] = f"{indent}{param_name} = {value_str}"
                break
    
    return '\n'.join(lines)


def has_adjustable_parameters(code: str) -> bool:
    """
    Quick check if code has any adjustable parameters.
    
    Args:
        code: Python code string
        
    Returns:
        True if parameters were detected
    """
    return len(detect_parameters(code)) > 0
