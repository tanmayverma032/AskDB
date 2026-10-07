import streamlit as st
import uuid

# Initialize page config before anything else
st.set_page_config(
    page_title="AskDB - AI Database Assistant",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.styles import get_custom_css, get_sql_highlight_css
from utils.api_client import api_client
from components.sidebar import render_sidebar
from components.chat import render_chat, handle_user_input
from components.voice import render_voice_input

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "connected" not in st.session_state:
        st.session_state.connected = False
    if "db_info" not in st.session_state:
        st.session_state.db_info = {}
    if "schema" not in st.session_state:
        st.session_state.schema = None
    if "query_history" not in st.session_state:
        st.session_state.query_history = []
    if "voice_prompt" not in st.session_state:
        st.session_state.voice_prompt = None

    # Check if backend is already connected (e.g. from environment settings)
    if not st.session_state.connected and not st.session_state.get("_initial_checked"):
        st.session_state._initial_checked = True
        try:
            status = api_client.get_status()
            if status.get("connected"):
                st.session_state.connected = True
                schema_res = api_client.get_schema()
                if "tables" in schema_res:
                    st.session_state.schema = schema_res
        except Exception:
            pass

def main():
    # Inject CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    st.markdown(get_sql_highlight_css(), unsafe_allow_html=True)
    
    # Init state
    init_session_state()
    
    # Sidebar
    render_sidebar()
    
    # Main Header
    col_a, col_b = st.columns([1, 6])
    with col_b:
        st.title("AskDB")
        st.markdown("<p style='color: #00d4ff; font-size: 1.2rem; font-weight: 500;'>AI-Powered Database Assistant</p>", unsafe_allow_html=True)
    with col_a:
        if st.session_state.connected:
            st.markdown("<div style='margin-top: 25px;'><span style='color: #00ff00;'>🟢</span> Connected</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='margin-top: 25px;'><span style='color: #ff0000;'>🔴</span> Disconnected</div>", unsafe_allow_html=True)
    
    st.divider()
    
    if not st.session_state.connected:
        st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 2rem; text-align: center; backdrop-filter: blur(5px); margin-top: 2rem;'>
            <h2>Welcome to AskDB 🔮</h2>
            <p style='font-size: 1.1rem; color: #aaa;'>Your natural language interface to your databases.</p>
            <p>Please connect to a database using the sidebar to get started.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Check if voice transcription triggered a prompt
        if st.session_state.voice_prompt:
            vp = st.session_state.voice_prompt
            st.session_state.voice_prompt = None
            handle_user_input(vp)
            
        render_chat()
        st.markdown("<br><br>", unsafe_allow_html=True)
        render_voice_input()

if __name__ == "__main__":
    main()
