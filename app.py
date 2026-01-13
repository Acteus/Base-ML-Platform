"""
ML Base Platform - Main Streamlit Application
A platform for uploading data and executing custom Python algorithms.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_data, get_data_info, detect_file_type
from utils.code_executor import execute_code
from utils.visualizer import display_results, display_data_preview
from utils.parameter_parser import detect_parameters, update_code_with_parameters, has_adjustable_parameters

# Page configuration
st.set_page_config(
    page_title="ML Base Platform",
    page_icon="ML",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .parameter-section {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'data_info' not in st.session_state:
    st.session_state.data_info = None
if 'execution_result' not in st.session_state:
    st.session_state.execution_result = None
if 'current_code' not in st.session_state:
    st.session_state.current_code = """# Write your algorithm here
# The data is available as 'df' (pandas DataFrame)
# Common libraries are pre-imported: pd, np, plt, sns, sklearn

# Example: Basic data exploration
print(f"Data shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print("\\nFirst few rows:")
print(df.head())

# Example: Simple analysis
if len(df.columns) > 0:
    print(f"\\nSummary statistics:")
    print(df.describe())

# Tip: Add parameters like these to get interactive sliders:
# learning_rate = 0.01
# n_clusters = 3
# test_size = 0.2
"""
if 'show_sliders' not in st.session_state:
    st.session_state.show_sliders = False
if 'param_values' not in st.session_state:
    st.session_state.param_values = {}


def render_parameter_sliders(code: str) -> dict:
    """
    Render parameter sliders and return updated values.
    
    Args:
        code: Current Python code
        
    Returns:
        Dictionary of updated parameter values
    """
    parameters = detect_parameters(code)
    
    if not parameters:
        return {}
    
    updated_values = {}
    
    st.markdown("#### Parameter Tuning")
    st.caption("Drag sliders to adjust parameters. Code will update automatically.")
    
    # Create columns for better layout (2 sliders per row)
    for i in range(0, len(parameters), 2):
        cols = st.columns(2)
        
        for j, col in enumerate(cols):
            if i + j < len(parameters):
                param = parameters[i + j]
                with col:
                    # Create a unique key for each slider
                    slider_key = f"param_{param.name}"
                    
                    # Get current value from session state or use detected value
                    current_val = st.session_state.param_values.get(param.name, param.value)
                    
                    if param.param_type == 'int':
                        new_value = st.slider(
                            f"`{param.name}`",
                            min_value=int(param.min_value),
                            max_value=int(param.max_value),
                            value=int(current_val),
                            step=int(param.step),
                            key=slider_key,
                            help=f"Line {param.line_number}: {param.original_text}"
                        )
                    else:
                        new_value = st.slider(
                            f"`{param.name}`",
                            min_value=float(param.min_value),
                            max_value=float(param.max_value),
                            value=float(current_val),
                            step=float(param.step),
                            key=slider_key,
                            format="%.4f" if param.step < 0.01 else "%.2f",
                            help=f"Line {param.line_number}: {param.original_text}"
                        )
                    
                    updated_values[param.name] = new_value
    
    return updated_values


def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">ML Base Platform</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("Data Upload")
        st.markdown("Upload your data file to get started.")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['csv', 'json', 'xlsx', 'xls', 'parquet'],
            help="Supported formats: CSV, JSON, Excel, Parquet"
        )
        
        if uploaded_file is not None:
            st.success(f"File uploaded: {uploaded_file.name}")
            file_type = detect_file_type(uploaded_file.name)
            st.info(f"File type: {file_type.upper()}")
            
            # Load data
            with st.spinner("Loading data..."):
                load_result = load_data(uploaded_file, uploaded_file.name)
                
                if load_result['error']:
                    st.error(f"Error loading file: {load_result['error']}")
                    st.session_state.uploaded_data = None
                    st.session_state.data_info = None
                else:
                    st.session_state.uploaded_data = load_result['data']
                    st.session_state.data_info = get_data_info(load_result['data'])
                    st.success("Data loaded successfully!")
        
        st.markdown("---")
        st.markdown("### Tips")
        st.markdown("""
        - Data is available as `df` in your code
        - Pre-imported: `pd`, `np`, `plt`, `sns`, `sklearn`
        - Use `plt.show()` or return figure objects for visualizations
        - Parameters like `learning_rate`, `n_clusters`, etc. get auto-detected sliders
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Data Preview")
        if st.session_state.uploaded_data is not None:
            display_data_preview(st.session_state.data_info)
        else:
            st.info("Please upload a data file from the sidebar to get started.")
    
    with col2:
        st.header("Algorithm Editor")
        
        if st.session_state.uploaded_data is None:
            st.warning("Please upload data first before writing algorithms.")
            code_input = st.text_area(
                "Python Code",
                value=st.session_state.current_code,
                height=300,
                disabled=True
            )
        else:
            # Code text area
            code_input = st.text_area(
                "Python Code",
                value=st.session_state.current_code,
                height=300,
                help="Write your Python algorithm here. Data is available as 'df'.",
                key="code_editor"
            )
            
            # Update session state if code changed manually
            if code_input != st.session_state.current_code:
                st.session_state.current_code = code_input
                # Reset param values when code changes significantly
                st.session_state.param_values = {}
            
            # Check for adjustable parameters
            has_params = has_adjustable_parameters(code_input)
            
            # Toggle for showing parameter sliders
            if has_params:
                st.session_state.show_sliders = st.toggle(
                    "Show Parameter Sliders",
                    value=st.session_state.show_sliders,
                    help="Enable interactive sliders to tune numeric parameters in your code"
                )
                
                # Render parameter sliders if enabled
                if st.session_state.show_sliders:
                    with st.container():
                        updated_params = render_parameter_sliders(code_input)
                        
                        # Check if any parameter changed
                        params_changed = False
                        for name, value in updated_params.items():
                            if st.session_state.param_values.get(name) != value:
                                params_changed = True
                                st.session_state.param_values[name] = value
                        
                        # Update code if parameters changed
                        if params_changed and updated_params:
                            new_code = update_code_with_parameters(code_input, updated_params)
                            st.session_state.current_code = new_code
                            st.rerun()
            
            # Action buttons
            col_run, col_clear = st.columns([1, 1])
            
            with col_run:
                run_button = st.button("Run Algorithm", type="primary", use_container_width=True)
            
            with col_clear:
                if st.button("Clear Results", use_container_width=True):
                    st.session_state.execution_result = None
                    st.rerun()
            
            if run_button:
                if not code_input.strip():
                    st.warning("Please enter some code to execute.")
                else:
                    with st.spinner("Executing algorithm..."):
                        execution_result = execute_code(
                            code=code_input,
                            data=st.session_state.uploaded_data,
                            timeout=30
                        )
                        st.session_state.execution_result = execution_result
    
    # Results section
    if st.session_state.execution_result is not None:
        st.markdown("---")
        st.header("Results")
        display_results(
            st.session_state.execution_result,
            data=st.session_state.uploaded_data
        )


if __name__ == "__main__":
    main()
