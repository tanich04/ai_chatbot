import streamlit as st
import requests
import pandas as pd
from mock_calendar import calendar_data, normalize_date

st.set_page_config(page_title="📅 AI Calendar Assistant")
st.title("📅 AI Calendar Assistant")

st.sidebar.header("🗓️ Calendar")
if calendar_data:
    rows = []
    for date in sorted(calendar_data):
        for time, title in calendar_data[date].items():
            rows.append({"Date": date, "Time": time, "Event": title})
    df = pd.DataFrame(rows)
    st.dataframe(df.sort_values(by=["Date", "Time"]))
else:
    st.sidebar.info("No events yet. Start booking!")

st.divider()
st.subheader("🤖 Chat with your assistant")

if "chat" not in st.session_state:
    st.session_state.chat = []

user_input = st.text_input("You:", placeholder="e.g. Book a meeting on Monday at 2PM")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})
    try:
        response = requests.post(
            "https://aichatbot-production-a7c6.up.railway.app/chat",
            json={"question": user_input},
            timeout=30
        )
        bot_reply = response.json()["response"]
    except Exception as e:
        bot_reply = f"❌ Error: {e}"
    st.session_state.chat.append({"role": "bot", "content": bot_reply})

for chat in st.session_state.chat:
    align = "🧑‍💻 You:" if chat["role"] == "user" else "🤖 Bot:"
    st.write(f"{align} {chat['content']}")
