# ui/app.py
import streamlit as st
import os
import sys
import logging
from pathlib import Path
import tempfile

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sat_sight.core.workflow import run_workflow # Import the run_workflow function from your core module

# Set up logging (optional, Streamlit has its own)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="Sat-Sight: Agentic Satellite QA", 
    layout="wide",
    page_icon="🛰️"
)

st.title("🛰️ Sat-Sight: Agentic Satellite QA")
st.markdown("""
    Ask questions about satellite images and environmental topics using our multi-agent AI system.
    
    **Capabilities:**
    - 🖼️ Analyze satellite imagery and land cover
    - 🌐 Search real-time web information
    - 📚 Retrieve knowledge from environmental databases
    - 🤖 Multi-agent reasoning with vision, text, and web search
""")

# --- Initialize Session State for Conversation History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat Messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Sidebar for Image Upload and Controls ---
with st.sidebar:
    st.header("📁 Image Upload")
    uploaded_image = st.file_uploader(
        "Upload a satellite image (optional)", 
        type=["jpg", "jpeg", "png"], 
        key="sidebar_uploader",
        help="Upload a satellite image for analysis"
    )
    
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
    
    st.divider()
    
    st.header("ℹ️ System Info")
    st.markdown("""
        **Active Agents:**
        - 🧠 Planner (routing)
        - 👁️ Vision (image analysis)
        - 📖 Text Retrieval
        - 🔍 Web Search (Tavily)
        - 🤔 Reasoning
        - 📝 Memory (episodic + long-term)
    """)
    
    st.divider()
    
    st.header("💡 Example Queries")
    
    examples = {
        "Image Analysis": [
            "What type of land use is shown in this image?",
            "Is this area at risk of deforestation?",
            "Describe the characteristics of this region"
        ],
        "Knowledge": [
            "What are the main drivers of deforestation?",
            "Explain the environmental impacts of urbanization"
        ],
        "Real-time": [
            "Find recent satellite monitoring reports about deforestation",
            "What are the latest developments in forest conservation?"
        ]
    }
    
    for category, queries in examples.items():
        with st.expander(f"{category}"):
            for query in queries:
                st.caption(f"• {query}")
    
    st.divider()
    
    # Clear conversation button
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Main Chat Input ---
if prompt := st.chat_input("Ask about satellite images or environmental topics..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Show image context if available
    if uploaded_image is not None:
        with st.chat_message("user"):
            st.caption("📷 Analyzing uploaded image...")

    # Determine if an image is available
    image_path_to_use = ""
    if uploaded_image is not None:
        # Save the uploaded image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_image.name)[1]) as tmp_file:
            tmp_file.write(uploaded_image.getbuffer())
            image_path_to_use = tmp_file.name
    # If no image is uploaded, image_path_to_use remains an empty string

    # --- Prepare Input for Backend ---
    # Let the backend planner decide the agent flow
    query_lower = prompt.lower()
    
    # Determine agent flow description for UI display
    if image_path_to_use:
        agent_flow_description = "🖼️ Image Analysis + Multi-Source Retrieval"
    elif any(kw in query_lower for kw in ["recent", "latest", "news", "current"]):
        agent_flow_description = "🌐 Web Search + Knowledge Retrieval"
    else:
        agent_flow_description = "📚 Text Knowledge Retrieval + Reasoning"
    
    initial_inputs = {
        "query": prompt,
        "image_path": image_path_to_use
    }
    
    logger.info(f"UI: Processing query '{prompt[:50]}...' with image: {bool(image_path_to_use)}")

    # --- Get Assistant Response from Backend ---
    with st.chat_message("assistant"):
        # Show which agent flow is being used
        st.info(f"Processing using: {agent_flow_description}")

        # Show a spinner while the backend processes
        with st.spinner("Thinking..."):
            try:
                response, final_state = run_workflow(initial_inputs["query"], initial_inputs["image_path"])
                st.markdown(response)
                
                # Optional: Show debug info (final state) if needed
                with st.expander("🔍 Debug Info (Final State)"):
                    st.json({
                        "agents_used": final_state.get("current_agent", "unknown"),
                        "retrieved_images": len(final_state.get("retrieved_image_metadata", [])),
                        "retrieved_texts": len(final_state.get("retrieved_text_chunks", [])),
                        "web_search": len(final_state.get("web_snippets", [])),
                        "confidence": final_state.get("confidence_score"),
                        "error": final_state.get("error_message")
                    })
                
                # Add assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"An error occurred: {e}"
                st.error(error_msg)
                logger.error(f"UI: Error running workflow: {e}")
                import traceback
                st.code(traceback.format_exc())
                
                # Add error to history
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # --- Clean up temporary image file after processing (if one was created) ---
    if image_path_to_use and os.path.exists(image_path_to_use):
        try:
            os.unlink(image_path_to_use)
            logger.info(f"UI: Deleted temporary image file {image_path_to_use}")
        except OSError as e:
            logger.warning(f"UI: Could not delete temporary file {image_path_to_use}: {e}")
