"""
Data loading utilities for various file formats.
Supports CSV, JSON, Excel, and Parquet files.
"""

import pandas as pd
import json
import io
from typing import Union, Optional, Dict, Any


def detect_file_type(filename: str) -> str:
    """
    Detect file type from extension.
    
    Args:
        filename: Name of the uploaded file
        
    Returns:
        File type string: 'csv', 'json', 'excel', 'parquet', or 'unknown'
    """
    if not filename:
        return 'unknown'
    
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.csv'):
        return 'csv'
    elif filename_lower.endswith(('.json', '.jsonl')):
        return 'json'
    elif filename_lower.endswith(('.xlsx', '.xls')):
        return 'excel'
    elif filename_lower.endswith('.parquet'):
        return 'parquet'
    else:
        return 'unknown'


def load_data(file, filename: str) -> Dict[str, Any]:
    """
    Load data from uploaded file based on file type.
    
    Args:
        file: Uploaded file object (Streamlit UploadedFile)
        filename: Name of the uploaded file
        
    Returns:
        Dictionary containing:
            - 'data': Loaded data (DataFrame or dict/list)
            - 'type': Data type ('dataframe' or 'raw')
            - 'file_type': Original file type
            - 'error': Error message if loading failed
    """
    file_type = detect_file_type(filename)
    
    try:
        if file_type == 'csv':
            # Read CSV file
            file.seek(0)  # Reset file pointer
            df = pd.read_csv(file)
            return {
                'data': df,
                'type': 'dataframe',
                'file_type': 'csv',
                'error': None
            }
            
        elif file_type == 'json':
            # Read JSON file
            file.seek(0)
            content = file.read()
            
            # Try to parse as JSON
            try:
                json_data = json.loads(content.decode('utf-8'))
                
                # Try to convert to DataFrame if it's a list of dicts or dict with list values
                if isinstance(json_data, list) and len(json_data) > 0:
                    if isinstance(json_data[0], dict):
                        df = pd.DataFrame(json_data)
                        return {
                            'data': df,
                            'type': 'dataframe',
                            'file_type': 'json',
                            'error': None
                        }
                
                # Return raw JSON if not convertible
                return {
                    'data': json_data,
                    'type': 'raw',
                    'file_type': 'json',
                    'error': None
                }
            except json.JSONDecodeError:
                # Try reading as JSONL (one JSON per line)
                file.seek(0)
                lines = content.decode('utf-8').strip().split('\n')
                json_list = [json.loads(line) for line in lines if line.strip()]
                if json_list and isinstance(json_list[0], dict):
                    df = pd.DataFrame(json_list)
                    return {
                        'data': df,
                        'type': 'dataframe',
                        'file_type': 'json',
                        'error': None
                    }
                else:
                    return {
                        'data': None,
                        'type': 'raw',
                        'file_type': 'json',
                        'error': 'Could not parse JSON file'
                    }
                    
        elif file_type == 'excel':
            # Read Excel file
            file.seek(0)
            df = pd.read_excel(file, engine='openpyxl')
            return {
                'data': df,
                'type': 'dataframe',
                'file_type': 'excel',
                'error': None
            }
            
        elif file_type == 'parquet':
            # Read Parquet file
            file.seek(0)
            df = pd.read_parquet(file)
            return {
                'data': df,
                'type': 'dataframe',
                'file_type': 'parquet',
                'error': None
            }
            
        else:
            return {
                'data': None,
                'type': 'raw',
                'file_type': file_type,
                'error': f'Unsupported file type: {file_type}'
            }
            
    except Exception as e:
        return {
            'data': None,
            'type': 'raw',
            'file_type': file_type,
            'error': f'Error loading file: {str(e)}'
        }


def get_data_info(data: Union[pd.DataFrame, Any]) -> Dict[str, Any]:
    """
    Get information about the loaded data.
    
    Args:
        data: Loaded data (DataFrame or other)
        
    Returns:
        Dictionary with data information
    """
    if isinstance(data, pd.DataFrame):
        return {
            'type': 'DataFrame',
            'shape': data.shape,
            'columns': list(data.columns),
            'dtypes': data.dtypes.to_dict(),
            'memory_usage': f"{data.memory_usage(deep=True).sum() / 1024:.2f} KB",
            'null_counts': data.isnull().sum().to_dict(),
            'sample': data.head(10).to_dict('records')
        }
    else:
        return {
            'type': type(data).__name__,
            'shape': None,
            'columns': None,
            'dtypes': None,
            'memory_usage': None,
            'null_counts': None,
            'sample': str(data)[:500] if data else None
        }
