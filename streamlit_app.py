import streamlit as st
import requests

st.title("📅 AI Calendar Booking Assistant")
st.caption("Ask me to schedule, check, move, or delete calendar events.")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.chat_input("Ask me anything about your meetings")
if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                "https://aichatbot-production-a7c6.up.railway.app/chat",
                json={"question": user_input},
                timeout=20
            )
            bot_msg = response.json().get("response", "❌ Error: No response")
        except Exception as e:
            bot_msg = f"❌ Error: {e}"
        st.session_state.history.append({"role": "assistant", "content": bot_msg})

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
