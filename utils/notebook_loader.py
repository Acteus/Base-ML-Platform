"""
Jupyter Notebook (.ipynb) loader and parser utilities.
Extracts code cells, markdown cells, and metadata from notebooks.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class NotebookCell:
    """Represents a cell from a Jupyter notebook."""
    cell_type: str  # 'code', 'markdown', 'raw'
    source: str     # Cell content
    index: int      # Cell position in notebook
    outputs: List[Any] = None
    execution_count: Optional[int] = None
    
    def __post_init__(self):
        if self.outputs is None:
            self.outputs = []


@dataclass 
class NotebookInfo:
    """Contains parsed notebook information."""
    cells: List[NotebookCell]
    metadata: Dict[str, Any]
    kernel_name: str
    language: str
    nbformat: int
    nbformat_minor: int
    code_cells_count: int
    markdown_cells_count: int
    
    
def parse_notebook(file) -> Dict[str, Any]:
    """
    Parse a Jupyter notebook file.
    
    Args:
        file: Uploaded file object or file path
        
    Returns:
        Dictionary containing:
            - 'success': Boolean indicating if parsing succeeded
            - 'notebook_info': NotebookInfo object with parsed data
            - 'error': Error message if parsing failed
    """
    try:
        # Read the notebook content
        if hasattr(file, 'seek'):
            file.seek(0)
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
        else:
            # Assume it's a file path
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # Parse JSON
        notebook = json.loads(content)
        
        # Extract cells
        cells = []
        code_count = 0
        markdown_count = 0
        
        raw_cells = notebook.get('cells', [])
        
        for idx, cell in enumerate(raw_cells):
            cell_type = cell.get('cell_type', 'code')
            
            # Join source lines if it's a list
            source = cell.get('source', [])
            if isinstance(source, list):
                source = ''.join(source)
            
            # Get outputs for code cells
            outputs = cell.get('outputs', [])
            execution_count = cell.get('execution_count')
            
            notebook_cell = NotebookCell(
                cell_type=cell_type,
                source=source,
                index=idx,
                outputs=outputs,
                execution_count=execution_count
            )
            cells.append(notebook_cell)
            
            if cell_type == 'code':
                code_count += 1
            elif cell_type == 'markdown':
                markdown_count += 1
        
        # Extract metadata
        metadata = notebook.get('metadata', {})
        kernelspec = metadata.get('kernelspec', {})
        language_info = metadata.get('language_info', {})
        
        notebook_info = NotebookInfo(
            cells=cells,
            metadata=metadata,
            kernel_name=kernelspec.get('display_name', 'Unknown'),
            language=language_info.get('name', kernelspec.get('language', 'python')),
            nbformat=notebook.get('nbformat', 4),
            nbformat_minor=notebook.get('nbformat_minor', 0),
            code_cells_count=code_count,
            markdown_cells_count=markdown_count
        )
        
        return {
            'success': True,
            'notebook_info': notebook_info,
            'error': None
        }
        
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'notebook_info': None,
            'error': f'Invalid notebook format: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'notebook_info': None,
            'error': f'Error parsing notebook: {str(e)}'
        }


def extract_all_code(notebook_info: NotebookInfo, include_comments: bool = True) -> str:
    """
    Extract all code cells from notebook and combine them.
    
    Args:
        notebook_info: Parsed NotebookInfo object
        include_comments: If True, add cell index comments between cells
        
    Returns:
        Combined code string from all code cells
    """
    code_parts = []
    
    for cell in notebook_info.cells:
        if cell.cell_type == 'code':
            source = cell.source.strip()
            if source:  # Skip empty cells
                if include_comments:
                    code_parts.append(f"# --- Cell {cell.index + 1} ---")
                code_parts.append(source)
    
    return '\n\n'.join(code_parts)


def extract_code_cell(notebook_info: NotebookInfo, cell_index: int) -> Optional[str]:
    """
    Extract code from a specific cell.
    
    Args:
        notebook_info: Parsed NotebookInfo object
        cell_index: Index of the cell to extract
        
    Returns:
        Code string or None if cell doesn't exist or isn't a code cell
    """
    for cell in notebook_info.cells:
        if cell.index == cell_index and cell.cell_type == 'code':
            return cell.source
    return None


def get_code_cells(notebook_info: NotebookInfo) -> List[NotebookCell]:
    """
    Get only the code cells from a notebook.
    
    Args:
        notebook_info: Parsed NotebookInfo object
        
    Returns:
        List of code cells
    """
    return [cell for cell in notebook_info.cells if cell.cell_type == 'code']


def extract_cell_range(
    notebook_info: NotebookInfo, 
    start_index: int, 
    end_index: int,
    include_comments: bool = True
) -> str:
    """
    Extract code from a range of cells.
    
    Args:
        notebook_info: Parsed NotebookInfo object
        start_index: Starting cell index (inclusive)
        end_index: Ending cell index (inclusive)
        include_comments: If True, add cell separators
        
    Returns:
        Combined code string
    """
    code_parts = []
    
    for cell in notebook_info.cells:
        if start_index <= cell.index <= end_index and cell.cell_type == 'code':
            source = cell.source.strip()
            if source:
                if include_comments:
                    code_parts.append(f"# --- Cell {cell.index + 1} ---")
                code_parts.append(source)
    
    return '\n\n'.join(code_parts)


def get_notebook_summary(notebook_info: NotebookInfo) -> Dict[str, Any]:
    """
    Get a summary of the notebook contents.
    
    Args:
        notebook_info: Parsed NotebookInfo object
        
    Returns:
        Dictionary with notebook summary
    """
    total_code_lines = sum(
        len(cell.source.split('\n')) 
        for cell in notebook_info.cells 
        if cell.cell_type == 'code'
    )
    
    executed_cells = sum(
        1 for cell in notebook_info.cells 
        if cell.cell_type == 'code' and cell.execution_count is not None
    )
    
    return {
        'kernel': notebook_info.kernel_name,
        'language': notebook_info.language,
        'total_cells': len(notebook_info.cells),
        'code_cells': notebook_info.code_cells_count,
        'markdown_cells': notebook_info.markdown_cells_count,
        'total_code_lines': total_code_lines,
        'executed_cells': executed_cells,
        'nbformat': f'{notebook_info.nbformat}.{notebook_info.nbformat_minor}'
    }
