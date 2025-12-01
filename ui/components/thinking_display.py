"""
Thinking Display Component
Renders the "Show Thinking" dropdown similar to ChatGPT/Gemini
"""

import streamlit as st
from typing import List, Dict, Any

def render_thinking_process(thinking_steps: List[Dict[str, Any]]):
    """
    Renders an expandable "Show Thinking" section with internal reasoning steps.
    
    Args:
        thinking_steps: List of thinking steps from the reasoning agent
        
    Example structure:
        [
            {
                "step": "Image Analysis",
                "details": "Retrieved 5 matching images",
                "data": [{"class": "Forest", "confidence": "95.2%", ...}]
            },
            ...
        ]
    """
    if not thinking_steps:
        return
    
    with st.expander("Show Thinking", expanded=False):
        st.markdown("""
            <style>
            .thinking-container {
                background-color: #f8f9fa;
                border-left: 3px solid #6c757d;
                padding: 10px 15px;
                margin: 10px 0;
                border-radius: 5px;
            }
            .thinking-step-title {
                font-weight: 600;
                color: #495057;
                margin-bottom: 5px;
            }
            .thinking-step-details {
                color: #6c757d;
                font-size: 0.9em;
                margin-bottom: 8px;
            }
            .thinking-data {
                background-color: #ffffff;
                padding: 8px;
                border-radius: 3px;
                margin-top: 5px;
                font-size: 0.85em;
            }
            </style>
        """, unsafe_allow_html=True)
        
        for i, step in enumerate(thinking_steps, 1):
            step_name = step.get('step', 'Unknown Step')
            details = step.get('details', '')
            data = step.get('data', None)
            
            st.markdown(f"""
                <div class="thinking-container">
                    <div class="thinking-step-title">
                        {i}. {step_name}
                    </div>
                    <div class="thinking-step-details">
                        {details}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Display data if present
            if data:
                if isinstance(data, list):
                    # Multiple items (e.g., images, documents)
                    for item in data:
                        st.json(item, expanded=False)
                elif isinstance(data, dict):
                    # Single item (e.g., Wikipedia info)
                    st.json(data, expanded=False)
        
        st.markdown("---")
        st.caption("This shows the internal reasoning process used to generate the response.")


def render_thinking_process_simple(thinking_steps: List[Dict[str, Any]]):
    """
    Simple version without custom CSS for faster rendering.
    """
    if not thinking_steps:
        return
    
    with st.expander("Show Thinking", expanded=False):
        for i, step in enumerate(thinking_steps, 1):
            st.markdown(f"**{i}. {step.get('step', 'Unknown')}**")
            st.caption(step.get('details', ''))
            
            data = step.get('data', None)
            if data:
                with st.container():
                    st.json(data, expanded=False)
            
            if i < len(thinking_steps):
                st.markdown("")  # Spacing


