"""
Sat-Sight Professional UI
A clean, modern interface for satellite image analysis and environmental queries.
"""

import streamlit as st
import os
import sys
from pathlib import Path
import tempfile
from datetime import datetime

# sat_sight is a package, so we need its parent directory in the path
project_root = Path(__file__).resolve().parent.parent  # sat_sight directory
parent_dir = project_root.parent  # GenAi_Project directory
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
os.chdir(project_root)

from sat_sight.core.workflow import run_workflow
from sat_sight.ui.components.thinking_display import render_thinking_process

st.set_page_config(
    page_title="Sat-Sight | Satellite Image Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Sat-Sight: Advanced multi-agent system for satellite image analysis and environmental queries."
    }
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .conversation-container {
        background-color: #f9fafb;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .message-user {
        background-color: #ffffff;
        border-left: 3px solid #3b82f6;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    .message-assistant {
        background-color: #f3f4f6;
        border-left: 3px solid #10b981;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    .agent-badge {
        background-color: #e5e7eb;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.875rem;
        color: #374151;
        display: inline-block;
        margin: 0.25rem;
    }
    .sidebar-section {
        background-color: #f9fafb;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }
    .example-query {
        background-color: #ffffff;
        padding: 0.75rem;
        border-radius: 4px;
        border: 1px solid #e5e7eb;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    .example-query:hover {
        border-color: #3b82f6;
        background-color: #eff6ff;
    }
    .info-box {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        font-weight: 500;
    }
    .image-gallery {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
    }
    .image-caption {
        font-size: 0.875rem;
        color: #6b7280;
        text-align: center;
        margin-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

with st.sidebar:
    st.markdown("### Sat-Sight Analysis System")
    st.markdown("---")
    
    st.markdown("#### Image Upload")
    uploaded_image = st.file_uploader(
        "Select satellite image",
        type=["jpg", "jpeg", "png"],
        help="Upload a satellite image for analysis",
        label_visibility="collapsed"
    )
    
    if uploaded_image:
        st.image(uploaded_image, use_column_width=True)
        st.caption(f"File: {uploaded_image.name}")
    
    st.markdown("---")
    
    st.markdown("#### System Capabilities")
    capabilities = {
        "Image Analysis": "CLIP-based satellite image classification and retrieval",
        "Knowledge Base": "Vector search across 5000+ environmental documents",
        "Web Search": "Real-time information via Tavily API",
        "Multi-Agent": "Coordinated workflow with 13 specialized agents"
    }
    
    for cap, desc in capabilities.items():
        with st.expander(cap):
            st.caption(desc)
    
    st.markdown("---")
    
    st.markdown("#### Example Queries")
    
    if st.button("Show me forests", use_container_width=True, key="ex1"):
        st.session_state.example_query = "Show me forests"
        st.rerun()
    
    if st.button("Environmental impacts of deforestation", use_container_width=True, key="ex2"):
        st.session_state.example_query = "What are the environmental impacts of deforestation?"
        st.rerun()
    
    if st.button("Analyze agricultural image", use_container_width=True, key="ex3"):
        st.session_state.example_query = "Analyze this agricultural land use"
        st.rerun()
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("New Session", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.rerun()

st.markdown('<div class="main-header">Sat-Sight</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Advanced Satellite Image Analysis & Environmental Intelligence</div>', unsafe_allow_html=True)

if len(st.session_state.messages) == 0:
    st.markdown("""
        <div class="info-box">
            <strong>Welcome to Sat-Sight</strong><br>
            Ask questions about satellite imagery, land use patterns, environmental changes, or any related topic.
            Upload an image for analysis or start with a text query.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### Quick Start Examples")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Image Analysis**")
        st.markdown("- What land cover is shown?")
        st.markdown("- Classify this satellite image")
        st.markdown("- Describe visible features")
    
    with col2:
        st.markdown("**Environmental Queries**")
        st.markdown("- Deforestation impacts")
        st.markdown("- Climate change effects")
        st.markdown("- Biodiversity loss causes")
    
    with col3:
        st.markdown("**Real-Time Search**")
        st.markdown("- Latest forest monitoring")
        st.markdown("- Recent conservation news")
        st.markdown("- Current satellite data")

for idx, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        with st.container():
            st.markdown(f'<div class="message-user"><strong>You</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
    else:
        with st.container():
            st.markdown(f'<div class="message-assistant"><strong>Sat-Sight</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
            
            if "images" in message and message["images"]:
                st.markdown("#### Retrieved Images")
                cols = st.columns(min(3, len(message["images"])))
                for i, img_data in enumerate(message["images"][:6]):
                    with cols[i % 3]:
                        img_path = img_data.get("image_path", "")
                        if os.path.exists(img_path):
                            st.image(img_path, use_column_width=True)
                            if "label" in img_data:
                                st.caption(f"{img_data['label']} (Score: {img_data.get('score', 'N/A')})")
                        else:
                            st.caption(f"Image: {img_data.get('label', 'Unknown')}")
            
            if "thinking" in message:
                render_thinking_process(message["thinking"])

if "example_query" in st.session_state:
    prompt = st.session_state.example_query
    del st.session_state.example_query
else:
    prompt = st.chat_input("Ask about satellite images or environmental topics...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.container():
        st.markdown(f'<div class="message-user"><strong>You</strong><br>{prompt}</div>', unsafe_allow_html=True)
    
    image_path = ""
    if uploaded_image:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_image.name)[1]) as tmp:
            tmp.write(uploaded_image.getbuffer())
            image_path = tmp.name
    
    query_type = "Text Query"
    if image_path:
        query_type = "Image Analysis"
    elif any(kw in prompt.lower() for kw in ["latest", "recent", "news", "current"]):
        query_type = "Web Search"
    
    with st.container():
        st.markdown(f'<div class="info-box">Processing: {query_type}</div>', unsafe_allow_html=True)
        
        with st.spinner("Analyzing..."):
            try:
                response, final_state = run_workflow(
                    query=prompt,
                    image_path=image_path,
                    user_id=st.session_state.session_id
                )
                
                thinking_process = final_state.get("thinking_process", [])
                retrieved_images = []
                
                if final_state.get("retrieved_image_metadata"):
                    metadata_list = final_state["retrieved_image_metadata"]
                    distances = final_state.get("retrieved_image_distances", [])
                    
                    for i, metadata in enumerate(metadata_list[:6]):
                        img_info = {
                            "image_path": metadata.get("image_path", ""),
                            "label": metadata.get("label", "Unknown"),
                            "score": f"{1 - distances[i]:.3f}" if i < len(distances) else "N/A"
                        }
                        retrieved_images.append(img_info)
                
                st.markdown(f'<div class="message-assistant"><strong>Sat-Sight</strong><br>{response}</div>', unsafe_allow_html=True)
                
                if retrieved_images:
                    st.markdown("#### Retrieved Images")
                    cols = st.columns(min(3, len(retrieved_images)))
                    for i, img_data in enumerate(retrieved_images):
                        with cols[i % 3]:
                            img_path = img_data.get("image_path", "")
                            if os.path.exists(img_path):
                                st.image(img_path, use_column_width=True)
                                st.caption(f"{img_data['label']} (Score: {img_data.get('score', 'N/A')})")
                            else:
                                st.caption(f"Image: {img_data.get('label', 'Unknown')}")
                
                if thinking_process:
                    render_thinking_process(thinking_process)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "thinking": thinking_process,
                    "images": retrieved_images
                })
                
                if final_state.get("error_flag"):
                    st.markdown(f'<div class="warning-box">Note: {final_state.get("error_message", "Processing completed with warnings")}</div>', unsafe_allow_html=True)
                
            except Exception as e:
                error_msg = f"An error occurred during processing: {str(e)}"
                st.markdown(f'<div class="warning-box">{error_msg}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    if image_path and os.path.exists(image_path):
        try:
            os.unlink(image_path)
        except:
            pass
    
    st.rerun()

st.markdown("---")
st.caption(f"Session: {st.session_state.session_id} | Sat-Sight v1.0 | Multi-Agent Satellite Analysis System")
