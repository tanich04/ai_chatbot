import streamlit as st
import requests
import pandas as pd
from mock_calendar import calendar_data

st.set_page_config(page_title="📅 AI Calendar Assistant")
st.title("📅 AI Calendar Assistant")

st.sidebar.header("📋 Events")
if calendar_data:
    rows = []
    for date in sorted(calendar_data):
        for time, title in calendar_data[date].items():
            rows.append({"Date": date, "Time": time, "Event": title})
    df = pd.DataFrame(rows)
    st.dataframe(df.sort_values(by=["Date", "Time"]))
else:
    st.sidebar.info("No meetings yet.")

st.subheader("💬 Talk to Calendar Bot")
if "chat" not in st.session_state:
    st.session_state.chat = []

query = st.text_input("Ask me anything about your meetings")

if query:
    st.session_state.chat.append(("user", query))
    try:
        res = requests.post(
            "https://aichatbot-production-a7c6.up.railway.app/chat",
            json={"question": query}
        )
        ans = res.json().get("response", "❌ Error: No response.")
    except Exception as e:
        ans = f"❌ Error: {e}"
    st.session_state.chat.append(("bot", ans))

for sender, msg in st.session_state.chat:
    st.write(f"**{'You' if sender == 'user' else 'Bot'}:** {msg}")
