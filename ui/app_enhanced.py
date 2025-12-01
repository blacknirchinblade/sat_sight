"""
Enhanced Sat-Sight UI with Multiple Chat Sessions
Features: Create/Delete chats, Persist history, Resume conversations
"""

import streamlit as st
import os
import sys
from pathlib import Path
import tempfile
from datetime import datetime
import uuid

# Setup path - sat_sight is a package, so we need its parent directory
project_root = Path(__file__).resolve().parent.parent  # sat_sight directory
parent_dir = project_root.parent  # GenAi_Project directory

from sat_sight.core.workflow import run_workflow
from sat_sight.ui.components.thinking_display import render_thinking_process
from sat_sight.ui.chat_manager import ChatDatabase

def generate_smart_title(query):
    """
    Generate an intelligent, concise chat title from the user's first question
    """
    # Remove common question words and clean up
    query = query.strip()
    
    # Extract key phrases
    keywords = []
    
    # Look for specific topics
    topic_map = {
        'forest': '🌲 Forest Analysis',
        'deforest': '🪓 Deforestation',
        'urban': '🏙️ Urban Area',
        'water': '💧 Water Bodies',
        'river': '🌊 River',
        'ocean': '🌊 Ocean',
        'lake': '🏞️ Lake',
        'agriculture': '🌾 Agriculture',
        'farm': '🚜 Farmland',
        'desert': '🏜️ Desert',
        'mountain': '⛰️ Mountain',
        'climate': '🌡️ Climate',
        'pollution': '🏭 Pollution',
        'ice': '🧊 Ice/Glacier',
        'vegetation': '🌿 Vegetation',
        'biodiversity': '🦋 Biodiversity',
        'land use': '🗺️ Land Use',
        'satellite': '🛰️ Satellite Imagery',
        'change': '📊 Change Detection',
        'monitor': '📡 Monitoring',
    }
    
    # Check for topics
    query_lower = query.lower()
    for key, title in topic_map.items():
        if key in query_lower:
            return title
    
    # If no specific topic, create smart title from first few words
    words = query.split()
    
    # Remove common starting words
    skip_words = {'can', 'you', 'show', 'me', 'what', 'is', 'are', 'the', 'a', 'an', 'how', 'why', 'when', 'where', 'tell', 'explain', 'describe', 'analyze'}
    
    important_words = []
    for word in words:
        if word.lower() not in skip_words and len(important_words) < 4:
            important_words.append(word.capitalize())
    
    if important_words:
        title = ' '.join(important_words)
        # Limit length
        if len(title) > 35:
            title = title[:32] + "..."
        return title
    
    # Fallback
    return query[:35] + "..." if len(query) > 35 else query

def check_if_satellite_image(image_path, query=""):
    """
    Check if an uploaded image is a satellite image using vision model
    Returns True if satellite image, False otherwise
    """
    try:
        from sat_sight.models.vision_models import VisionModel
        
        vision_model = VisionModel()
        
        # Use vision model to check image type
        check_prompt = (
            "Is this a satellite or aerial image taken from above showing terrain, "
            "land use, geographic features, or environmental monitoring? "
            "Answer with just 'YES' if it's a satellite/aerial image, or 'NO' if it's not. "
            "Satellite images typically show: terrain from above, land cover, urban areas from space, "
            "forests, water bodies, agricultural fields, or geographic features from a bird's eye view."
        )
        
        result = vision_model.analyze(image_path, check_prompt)
        
        # Check if response contains YES
        if result and ("YES" in result.upper() or "SATELLITE" in result.upper() or "AERIAL" in result.upper()):
            return True
        
        return False
        
    except Exception as e:
        print(f"Error checking satellite image: {e}")
        # Default to True if we can't check (assume it's satellite)
        return True

st.set_page_config(
    page_title="Sat-Sight | Satellite Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Sat-Sight: Advanced multi-agent satellite image analysis system"
    }
)

# Initialize chat database
@st.cache_resource
def get_chat_db():
    return ChatDatabase()

chat_db = get_chat_db()

# Initialize session state with persistence
# Use query params to persist user_id and session_id across page refreshes
if "user_id" not in st.session_state:
    # Try to get from query params first (for persistence)
    query_params = st.query_params
    if "user_id" in query_params:
        st.session_state.user_id = query_params["user_id"]
    else:
        st.session_state.user_id = str(uuid.uuid4())
        st.query_params["user_id"] = st.session_state.user_id

if "current_session_id" not in st.session_state:
    # Try to get from query params first (for persistence)
    query_params = st.query_params
    if "session_id" in query_params:
        # Verify session exists in database
        session = chat_db.get_session(query_params["session_id"])
        if session:
            st.session_state.current_session_id = query_params["session_id"]
        else:
            # Session doesn't exist, create new one
            sessions = chat_db.get_user_sessions(st.session_state.user_id)
            if sessions:
                st.session_state.current_session_id = sessions[0]['session_id']
            else:
                st.session_state.current_session_id = chat_db.create_session(
                    st.session_state.user_id, 
                    "New Chat"
                )
            st.query_params["session_id"] = st.session_state.current_session_id
    else:
        # Try to load last active session or create new one
        sessions = chat_db.get_user_sessions(st.session_state.user_id)
        if sessions:
            st.session_state.current_session_id = sessions[0]['session_id']
        else:
            st.session_state.current_session_id = chat_db.create_session(
                st.session_state.user_id, 
                "New Chat"
            )
        st.query_params["session_id"] = st.session_state.current_session_id

if "messages_loaded" not in st.session_state:
    st.session_state.messages_loaded = False

# Custom CSS - Professional colors for both light and dark modes
st.markdown("""
    <style>
    .main-header {
        font-size: 2rem;
        font-weight: 600;
        color: #2563eb;
        margin-bottom: 0.5rem;
    }
    .message-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
        border-left: 4px solid #4f46e5;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .message-user strong {
        color: #fbbf24;
        font-weight: 600;
    }
    .message-assistant {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: #ffffff;
        border-left: 4px solid #059669;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .message-assistant strong {
        color: #fde047;
        font-weight: 600;
    }
    .stat-box {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
    }
    .stat-label {
        font-size: 0.875rem;
        color: #e0e7ff;
        font-weight: 500;
    }
    /* Info box styling */
    .stAlert {
        background-color: rgba(59, 130, 246, 0.1);
        border: 1px solid #3b82f6;
        border-radius: 6px;
        color: inherit;
    }
    /* Attach button styling - integrated look */
    button[kind="secondary"] {
        font-size: 1.2rem;
        padding: 0.5rem;
        border-radius: 8px;
        background: transparent;
        border: none;
        min-width: 40px;
        height: 40px;
    }
    button[kind="secondary"]:hover {
        background: rgba(88, 101, 242, 0.1);
    }
    /* File uploader when shown */
    [data-testid="stFileUploader"] {
        border: 2px dashed #3b82f6;
        border-radius: 8px;
        padding: 1rem;
        background: rgba(59, 130, 246, 0.05);
        margin-top: 0.5rem;
    }
    /* Remove stat box CSS since we removed statistics */
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="main-header">💬 Chat Sessions</div>', unsafe_allow_html=True)
    
    # New Chat Button
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("➕ New Chat", use_container_width=True):
            new_session_id = chat_db.create_session(st.session_state.user_id, "New Chat")
            st.session_state.current_session_id = new_session_id
            st.query_params["session_id"] = new_session_id  # Update query param for persistence
            st.session_state.messages_loaded = False
            st.rerun()
    
    with col2:
        if st.button("🔄", help="Refresh"):
            st.rerun()
    
    # Search
    search_term = st.text_input("🔍 Search chats", "")
    
    st.markdown("---")
    
    # Load sessions
    if search_term:
        sessions = chat_db.search_sessions(st.session_state.user_id, search_term)
    else:
        sessions = chat_db.get_user_sessions(st.session_state.user_id)
    
    if not sessions:
        st.info("No chat sessions yet. Start a new chat!")
    else:
        st.markdown(f"**{len(sessions)} Chat(s)**")
        
        for session in sessions:
            is_active = session['session_id'] == st.session_state.current_session_id
            
            with st.container():
                col_title, col_delete = st.columns([4, 1])
                
                with col_title:
                    title = session['title']
                    msg_count = session['message_count']
                    updated = session['updated_at'].split('.')[0] if '.' in session['updated_at'] else session['updated_at']
                    
                    if st.button(
                        f"{'📌 ' if is_active else ''}{title}\n{msg_count} msgs • {updated[:16]}",
                        key=f"session_{session['session_id']}",
                        use_container_width=True
                    ):
                        st.session_state.current_session_id = session['session_id']
                        st.query_params["session_id"] = session['session_id']  # Update query param for persistence
                        st.session_state.messages_loaded = False
                        st.rerun()
                
                with col_delete:
                    if st.button("🗑️", key=f"del_{session['session_id']}", help="Delete"):
                        chat_db.delete_session(session['session_id'])
                        if is_active and len(sessions) > 1:
                            other_sessions = [s for s in sessions if s['session_id'] != session['session_id']]
                            st.session_state.current_session_id = other_sessions[0]['session_id']
                            st.query_params["session_id"] = other_sessions[0]['session_id']  # Update query param
                            st.session_state.messages_loaded = False
                        st.rerun()

# Main chat area
st.markdown('<div class="main-header">🛰️ Sat-Sight</div>', unsafe_allow_html=True)

# Get current session info
current_session = chat_db.get_session(st.session_state.current_session_id)

if current_session:
    # Session title editor
    col_title, col_edit, col_clear = st.columns([6, 1, 1])
    
    with col_title:
        new_title = st.text_input(
            "Chat Title",
            value=current_session['title'],
            key="title_input",
            label_visibility="collapsed"
        )
        if new_title != current_session['title']:
            chat_db.update_session_title(st.session_state.current_session_id, new_title)
    
    with col_edit:
        st.write("")
    
    with col_clear:
        if st.button("🗑️ Clear", help="Clear all messages"):
            chat_db.clear_session_messages(st.session_state.current_session_id)
            st.session_state.messages_loaded = False
            st.rerun()
    
    st.markdown("---")
    
    # Load messages from database
    if not st.session_state.messages_loaded:
        messages = chat_db.get_session_messages(st.session_state.current_session_id)
        st.session_state.current_messages = messages
        st.session_state.messages_loaded = True
    
    # Display messages
    if not st.session_state.current_messages:
        st.info("👋 Start a conversation! Ask about satellite imagery, environmental monitoring, or land use analysis.")
        
        st.markdown("**Example queries:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Show me deforested areas"):
                st.session_state.example_query = "Show me satellite images of deforested areas"
                st.rerun()
        with col2:
            if st.button("What is urban sprawl?"):
                st.session_state.example_query = "What is urban sprawl and its environmental impacts?"
                st.rerun()
        with col3:
            if st.button("Monitor water bodies"):
                st.session_state.example_query = "How can satellites monitor water bodies?"
                st.rerun()
    else:
        for message in st.session_state.current_messages:
            if message['role'] == 'user':
                # Check if user uploaded an image
                if message.get('metadata') and message['metadata'].get('uploaded_image'):
                    st.markdown(f'<div class="message-user"><strong>🙋 You</strong><br><div style="color: #ffffff; margin-top: 0.5rem;">{message["content"]}</div></div>', unsafe_allow_html=True)
                    img_path = message['metadata']['uploaded_image']
                    if os.path.exists(img_path):
                        st.image(img_path, width=300, caption="Your uploaded image")
                else:
                    st.markdown(f'<div class="message-user"><strong>� You</strong><br><div style="color: #ffffff; margin-top: 0.5rem;">{message["content"]}</div></div>', unsafe_allow_html=True)
            else:
                # Display metadata (thinking, then images, then text)
                if message.get('metadata'):
                    metadata = message['metadata']
                    
                    # 1. Thinking process FIRST (at the top)
                    if 'thinking' in metadata and metadata['thinking']:
                        render_thinking_process(metadata['thinking'])
                    
                    # 2. Images SECOND
                    if 'images' in metadata and metadata['images']:
                        st.markdown('<div style="margin: 1rem 0;"><strong style="color: #10b981; font-size: 1.1rem;">📷 Retrieved Satellite Images</strong></div>', unsafe_allow_html=True)
                        
                        # Display images in a grid
                        num_images = len(metadata['images'][:6])
                        cols = st.columns(min(3, num_images))
                        
                        for i, img_data in enumerate(metadata['images'][:6]):
                            with cols[i % 3]:
                                # Use 'path' field which has 'images/filename.jpg' format
                                # Fallback to 'image_path' if 'path' doesn't exist
                                img_path = img_data.get('path', img_data.get('image_path', ''))
                                if img_path:
                                    # Handle both absolute and relative paths
                                    if not os.path.isabs(img_path):
                                        # Try multiple possible locations
                                        possible_paths = [
                                            os.path.join(str(project_root), 'data', img_path),  # data/images/filename.jpg
                                            os.path.join(str(project_root), img_path),  # Relative to project root
                                            os.path.join(str(project_root), 'data', 'images', os.path.basename(img_path)),  # In data/images
                                            img_path  # As-is
                                        ]
                                        
                                        # Find the first existing path
                                        img_path = None
                                        for path in possible_paths:
                                            if os.path.exists(path):
                                                img_path = path
                                                break
                                    
                                    if img_path and os.path.exists(img_path):
                                        st.image(img_path, use_container_width=True)
                                        if 'label' in img_data:
                                            st.caption(f"🏷️ {img_data['label']} (Score: {img_data.get('score', 'N/A')})")
                                    else:
                                        st.warning(f"⚠️ Image not found: {os.path.basename(img_data.get('image_path', 'unknown'))}")
                
                # 3. Assistant text response LAST
                st.markdown(f'<div class="message-assistant"><strong>🛰️ Sat-Sight</strong><br><div style="color: #ffffff; margin-top: 0.5rem; line-height: 1.6;">{message["content"]}</div></div>', unsafe_allow_html=True)
    
    # Chat input with inline image upload (compact like chatbots)
    st.markdown("---")
    
    uploaded_image = None
    
    # Initialize upload state
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = False
    if "uploaded_image_path" not in st.session_state:
        st.session_state.uploaded_image_path = None
    if "input_counter" not in st.session_state:
        st.session_state.input_counter = 0
    
    # Simple working layout - attach button above input
    if st.button("📎 Attach Image", help="Upload satellite image", key="attach_btn"):
        st.session_state.show_uploader = not st.session_state.show_uploader
    
    # Handle example queries
    if "example_query" in st.session_state:
        prompt = st.session_state.example_query
        del st.session_state.example_query
        st.session_state.send_message = True
    else:
        # Chat input with Enter key support
        prompt = st.chat_input(
            "Ask about satellite images or environmental topics... (Press Enter to send)",
            key=f"user_input_{st.session_state.input_counter}"
        )
    
    # Show file uploader only when button is clicked
    if st.session_state.show_uploader:
        uploaded_file = st.file_uploader(
            "Choose an image", 
            type=['png', 'jpg', 'jpeg', 'tif', 'tiff', 'geotiff'],
            key="image_uploader"
        )
        
        if uploaded_file:
            # Save uploaded image
            upload_dir = project_root / "data" / "uploaded_images"
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            img_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
            img_path = upload_dir / img_filename
            
            with open(img_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state.uploaded_image_path = str(img_path)
            st.session_state.show_uploader = False
            st.rerun()
    
    # Show attached image preview
    if st.session_state.uploaded_image_path:
        col_preview, col_remove = st.columns([5, 1])
        with col_preview:
            st.success(f"📷 Attached: {Path(st.session_state.uploaded_image_path).name}")
        with col_remove:
            if st.button("✖", help="Remove image"):
                st.session_state.uploaded_image_path = None
                st.rerun()
        uploaded_image = st.session_state.uploaded_image_path
    
    # Send message trigger (Enter key from chat_input automatically triggers)
    if prompt:
        st.session_state.send_message = True
    
    if st.session_state.get('send_message'):
        # Clear the flag immediately to prevent loops
        del st.session_state.send_message
        
        if not prompt and uploaded_image:
            prompt = "Can you analyze this satellite image?"
        
        # Only process if we have content
        if not prompt and not uploaded_image:
            st.warning("⚠️ Please enter a message or upload an image")
            st.stop()
        
        # Prepare user message metadata
        user_metadata = {}
        if uploaded_image:
            user_metadata['uploaded_image'] = uploaded_image
        
        # Add user message to database
        chat_db.add_message(
            st.session_state.current_session_id,
            "user",
            prompt,
            user_metadata if user_metadata else None
        )
        
        # Process query
        with st.spinner("🔄 Analyzing..."):
            try:
                # If user uploaded an image, check if it's a satellite image
                if uploaded_image:
                    is_satellite = check_if_satellite_image(uploaded_image, prompt)
                    
                    if not is_satellite:
                        response = (
                            "🤔 Hmm, this doesn't appear to be a satellite image. "
                            "I specialize in analyzing satellite imagery for environmental monitoring, "
                            "land use analysis, and geographic insights.\n\n"
                            "However, I can still try to help! Could you:\n"
                            "1. Upload a satellite image if you have one, or\n"
                            "2. Ask me general questions about the image, or\n"
                            "3. Ask me about satellite imagery and environmental topics without an image\n\n"
                            "What would you like to know?"
                        )
                        
                        chat_db.add_message(
                            st.session_state.current_session_id,
                            "assistant",
                            response,
                            {'uploaded_image_type': 'non_satellite'}
                        )
                        st.session_state.messages_loaded = False
                        st.rerun()
                    else:
                        # Process with uploaded satellite image
                        prompt_with_image = f"{prompt}\n[Note: User uploaded their own satellite image for analysis]"
                        response, final_state = run_workflow(
                            query=prompt_with_image,
                            image_path=uploaded_image,
                            user_id=st.session_state.user_id
                        )
                else:
                    # Normal query processing without uploaded image
                    response, final_state = run_workflow(
                        query=prompt,
                        user_id=st.session_state.user_id
                    )
                
                # Prepare metadata
                metadata = {
                    'thinking': final_state.get('thinking_process', []),
                    'images': [],
                    'agents': final_state.get('completed_sources', [])
                }
                
                # Process retrieved images
                if final_state.get('retrieved_image_metadata'):
                    for i, img_meta in enumerate(final_state['retrieved_image_metadata'][:6]):
                        metadata['images'].append({
                            'path': img_meta.get('path', img_meta.get('image_path', '')),  # Use 'path' first, fallback to 'image_path'
                            'image_path': img_meta.get('image_path', ''),  # Keep for backward compatibility
                            'label': img_meta.get('class', img_meta.get('label', 'Unknown')),  # Use 'class' field
                            'score': f"{img_meta.get('score', 0):.4f}" if 'score' in img_meta else 'N/A'
                        })
                
                # Add assistant message to database
                chat_db.add_message(
                    st.session_state.current_session_id,
                    "assistant",
                    response,
                    metadata
                )
                
                # Update session title if first message
                if current_session['message_count'] == 0:
                    # Generate smart title from first query
                    title = generate_smart_title(prompt)
                    chat_db.update_session_title(st.session_state.current_session_id, title)
                
                # Clear uploaded image and input after sending
                st.session_state.uploaded_image_path = None
                st.session_state.input_counter += 1  # This will reset the text input
                st.session_state.messages_loaded = False
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.exception(e)

else:
    st.error("Session not found. Creating new session...")
    new_session_id = chat_db.create_session(st.session_state.user_id, "New Chat")
    st.session_state.current_session_id = new_session_id
    st.rerun()
