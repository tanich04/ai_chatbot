import streamlit as st
import requests
import pandas as pd
import json

st.set_page_config(page_title="📅 AI Meeting Assistant")

st.title("🤖 AI Meeting Assistant")
st.caption("Ask me anything about your meetings (e.g., 'Book a meeting on Monday at 2PM')")

API_URL = "https://aichatbot-production-a7c6.up.railway.app/chat"

# Chat interface
for message in st.session_state.get("chat_history", []):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask me anything about your calendar...")
if user_input:
    st.session_state.chat_history = st.session_state.get("chat_history", [])
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        response = requests.post(API_URL, json={"question": user_input})
        answer = response.json()["response"]
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)
    except Exception as e:
        st.error(f"❌ Error: Could not get response.\n\n{e}")

# 📅 View Calendar Button
if st.button("📋 Show calendar data"):
    try:
        with open("calendar.json", "r") as f:
            calendar_data = json.load(f)
        data = []
        for date, slots in calendar_data.items():
            for time, title in slots.items():
                data.append({"Date": date, "Time": time, "Title": title})
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df.sort_values(by=["Date", "Time"]))
        else:
            st.info("📭 No events scheduled.")
    except FileNotFoundError:
        st.warning("📭 Calendar file not found.")
