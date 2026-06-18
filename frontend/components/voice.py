import streamlit as st
from utils.api_client import api_client

def render_voice_input():
    with st.expander("🎤 Voice Input & Output"):
        st.markdown("Upload an audio file to transcribe and ask.")
        audio_file = st.file_uploader("Upload Audio", type=["wav", "mp3", "webm", "ogg"])
        
        if audio_file is not None:
            if st.button("Transcribe & Ask"):
                with st.spinner("Transcribing..."):
                    text = api_client.transcribe_audio(audio_file.read())
                    if text and not text.startswith("Error"):
                        st.success(f"Transcribed: {text}")
                        # Store in session state so app can pick it up
                        if st.session_state.get("connected"):
                            st.session_state.voice_prompt = text
                    else:
                        st.error("Failed to transcribe audio.")
                        
        # Synthesis section
        if st.session_state.messages:
            last_msg = st.session_state.messages[-1]
            if last_msg["role"] == "assistant":
                if st.button("🔊 Read Last Response"):
                    content_to_read = last_msg.get("content", "")
                    # Optionally read insights as well
                    data = last_msg.get("data", {})
                    insights = data.get("insights", [])
                    if insights:
                        content_to_read += ". " + " ".join(insights)
                        
                    if content_to_read:
                        with st.spinner("Synthesizing..."):
                            audio_bytes = api_client.synthesize_speech(content_to_read)
                            if audio_bytes:
                                st.audio(audio_bytes, format="audio/mpeg")
                            else:
                                st.error("Failed to synthesize speech.")
