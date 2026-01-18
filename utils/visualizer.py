"""
Visualization utilities for displaying execution results.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from typing import Any, Dict, List
import io


def display_results(execution_result: Dict[str, Any], data: Any = None):
    """
    Display execution results in organized tabs.
    
    Args:
        execution_result: Result dictionary from code_executor
        data: Original or modified data (optional)
    """
    if not execution_result['success']:
        st.error("Execution Error")
        st.code(execution_result['error'], language='python')
        return
    
    # Create tabs for different result views
    tab1, tab2, tab3, tab4 = st.tabs(["Output", "Data", "Variables", "Visualizations"])
    
    with tab1:
        st.subheader("Console Output")
        if execution_result['output']:
            st.text(execution_result['output'])
        else:
            st.info("No output generated")
        
        if execution_result['result'] is not None:
            st.subheader("Result")
            display_value(execution_result['result'])
    
    with tab2:
        st.subheader("Data")
        if data is not None:
            if isinstance(data, pd.DataFrame):
                st.dataframe(data, use_container_width=True)
                st.write(f"Shape: {data.shape}")
                st.write("Column Info:")
                st.json(data.dtypes.to_dict())
            else:
                st.write("Data type:", type(data).__name__)
                st.json(data if isinstance(data, (dict, list)) else str(data))
        else:
            st.info("No data to display")
    
    with tab3:
        st.subheader("Variables")
        variables = execution_result.get('variables', {})
        if variables:
            for var_name, var_value in variables.items():
                with st.expander(var_name):
                    display_value(var_value)
        else:
            st.info("No variables created")
    
    with tab4:
        st.subheader("Visualizations")
        # Use captured figures from execution result (captured before plt.show() clears them)
        captured_figs = execution_result.get('figures', [])
        
        if captured_figs:
            for i, fig in enumerate(captured_figs):
                try:
                    st.pyplot(fig)
                except Exception as e:
                    st.warning(f"Could not render figure {i+1}: {str(e)}")
        else:
            # Fallback: try to get figures from plt directly (for non-notebook code)
            try:
                import matplotlib.pyplot as plt
                fig_nums = plt.get_fignums()
                if fig_nums:
                    for fig_num in fig_nums:
                        fig = plt.figure(fig_num)
                        st.pyplot(fig)
                else:
                    st.info("No visualizations generated. Use plt.show() or return figure objects.")
            except Exception as e:
                st.info(f"No visualizations available: {str(e)}")


def display_value(value: Any):
    """
    Display a value in the appropriate format.
    
    Args:
        value: Value to display
    """
    if isinstance(value, pd.DataFrame):
        st.dataframe(value, use_container_width=True)
        st.write(f"Shape: {value.shape}")
    elif isinstance(value, pd.Series):
        st.dataframe(value.to_frame(), use_container_width=True)
    elif isinstance(value, (list, tuple)):
        if len(value) > 0 and isinstance(value[0], (dict, list)):
            st.json(value)
        else:
            st.write(value)
    elif isinstance(value, dict):
        st.json(value)
    elif isinstance(value, (int, float, str, bool)):
        st.write(value)
    elif hasattr(value, '__module__') and 'matplotlib' in str(value.__module__):
        # Matplotlib figure
        st.pyplot(value)
    else:
        st.write(f"Type: {type(value).__name__}")
        st.write(str(value)[:1000])  # Limit display length


def display_data_preview(data_info: Dict[str, Any]):
    """
    Display data preview and information.
    
    Args:
        data_info: Data information dictionary from data_loader
    """
    st.subheader("Data Preview")
    
    if data_info['type'] == 'DataFrame':
        st.write(f"**Type:** {data_info['type']}")
        st.write(f"**Shape:** {data_info['shape'][0]} rows × {data_info['shape'][1]} columns")
        st.write(f"**Memory Usage:** {data_info['memory_usage']}")
        
        if data_info['columns']:
            st.write("**Columns:**")
            st.write(", ".join(data_info['columns']))
        
        # Display sample data
        if data_info['sample']:
            st.write("**Sample Data (first 10 rows):**")
            sample_df = pd.DataFrame(data_info['sample'])
            st.dataframe(sample_df, use_container_width=True)
        
        # Display null counts if any
        if data_info['null_counts'] and any(data_info['null_counts'].values()):
            st.write("**Missing Values:**")
            null_df = pd.DataFrame([
                {'Column': k, 'Null Count': v} 
                for k, v in data_info['null_counts'].items() 
                if v > 0
            ])
            st.dataframe(null_df, use_container_width=True)
    else:
        st.write(f"**Type:** {data_info['type']}")
        if data_info['sample']:
            st.write("**Preview:**")
            st.text(str(data_info['sample'])[:500])
