import streamlit as st
import requests

st.title("📅 AI Calendar Assistant")
API_URL = "https://aichatbot-production-a7c6.up.railway.app/chat"

if "history" not in st.session_state:
    st.session_state.history = []

prompt = st.chat_input("Ask about availability, booking, or your calendar")

if prompt:
    st.session_state.history.append(("user", prompt))
    try:
        response = requests.post(API_URL, json={"message": prompt})
        response.raise_for_status()
        answer = response.json()["response"]
    except Exception as e:
        answer = f"❌ Error: {str(e)}"
    st.session_state.history.append(("bot", answer))

for role, msg in st.session_state.history:
    with st.chat_message(role):
        st.markdown(msg)
