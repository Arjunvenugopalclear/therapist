import streamlit as st
import webrtc_audio
import asyncio
import os

st.set_page_config(page_title="Digital Therapist", page_icon="🧠", layout="wide")

async def main():
    st.title("Digital Therapist")
    st.write("Welcome to your digital therapy session. Click 'Start Therapy Session' to begin.")

    if 'session_active' not in st.session_state:
        st.session_state.session_active = False
        st.session_state.pc = None
        st.session_state.audio_track = None

    if not st.session_state.session_active:
        if st.button("Start Therapy Session"):
            st.session_state.session_active = True
            st.write("Please grant microphone and speaker permissions when prompted by your browser.")
            st.session_state.pc, st.session_state.audio_track = await webrtc_audio.initialize_audio_stream()
            st.rerun()
    else:
        if st.button("Stop Session"):
            st.session_state.session_active = False
            if st.session_state.pc:
                await webrtc_audio.stop_audio_processing(st.session_state.pc)
            st.session_state.pc = None
            st.session_state.audio_track = None
            st.rerun()

        st.write("Session in progress. If you can't hear anything, please check your browser's audio settings and ensure you've granted the necessary permissions.")
        st.write("Speak clearly into your microphone.")
        st.write("The AI therapist will respond to you in real-time.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    asyncio.run(main())
    os.system(f"streamlit run main.py --server.port {port}")
