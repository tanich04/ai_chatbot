import streamlit as st
import requests
import pandas as pd
from mock_calendar import get_calendar_matrix

st.set_page_config(page_title="🧠 AI Calendar Assistant")

st.title("📅 AI Calendar Assistant")
st.subheader("Ask me anything about your meetings")

BACKEND_URL = "https://aichatbot-production-a7c6.up.railway.app/chat"

if "chat" not in st.session_state:
    st.session_state.chat = []

for msg in st.session_state.chat:
    st.chat_message("user").write(msg["content"])

user_input = st.chat_input("Book a meeting for 2PM Monday")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    try:
        response = requests.post(BACKEND_URL, json={"messages": st.session_state.chat})
        response.raise_for_status()
        data = response.json()

        if "response" in data:
            answer = data["response"]
        else:
            answer = f"❌ Error: Invalid response format. Data: {data}"
    except Exception as e:
        answer = f"❌ Error: {str(e)}"

    st.chat_message("assistant").write(answer)

st.markdown("---")
if st.button("📋 Show calendar data"):
    data = get_calendar_matrix()
    rows = []
    for date, times in data.items():
        for time, title in times.items():
            rows.append({"Date": date, "Time": time, "Event": title})
    df = pd.DataFrame(rows)
    if not df.empty:
        st.dataframe(df.sort_values(by=["Date", "Time"]), use_container_width=True)
    else:
        st.info("📭 No events scheduled.")
