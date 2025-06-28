# streamlit_app.py
import streamlit as st
import requests

st.set_page_config(page_title="📅 AI Calendar Assistant", layout="centered")
st.title("📅 AI Calendar Booking Assistant")

# Railway deployed FastAPI backend URL
BACKEND_URL = "https://aichatbot-production-b99a.up.railway.app/chat"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Accept user input
prompt = st.chat_input("Ask me anything about your meetings")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = requests.post(BACKEND_URL, json={"question": prompt})
            response.raise_for_status()
            data = response.json()
            answer = data.get("response", "❌ Error: No valid response.")
        except Exception as e:
            answer = f"❌ Error: {e}"

        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
