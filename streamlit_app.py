import streamlit as st
import requests

st.title("📅 AI Meeting Scheduler")
st.write("Ask me to book, cancel, or modify a meeting.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_input = st.chat_input("What would you like to do?")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            response = requests.post(
                "https://aichatbot-production-b99a.up.railway.app/chat",
                json={"question": user_input},
                timeout=30
            )
            bot_reply = response.json()["response"]
            st.markdown(bot_reply)
        except Exception as e:
            bot_reply = f"❌ Error: {str(e)}"
            st.error(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
