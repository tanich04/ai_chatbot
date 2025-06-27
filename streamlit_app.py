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

# Display the chat history
for msg in st.session_state.chat:
    st.chat_message(msg["role"]).write(msg["content"])

# Input box
user_input = st.chat_input("E.g., Book meeting 2PM on Monday")

if user_input:
    user_msg = {"role": "user", "content": user_input}
    st.session_state.chat.append(user_msg)
    st.chat_message("user").write(user_input)

    try:
        # 🛠 Send full message list as expected by FastAPI backend
        payload = {"messages": st.session_state.chat}
        response = requests.post(BACKEND_URL, json=payload)
        response.raise_for_status()
        data = response.json()

        if "response" in data:
            answer = data["response"]
        else:
            answer = f"❌ Error: Unexpected response format.\n\n{data}"
    except Exception as e:
        answer = f"❌ Error: {str(e)}"

    st.chat_message("assistant").write(answer)
    st.session_state.chat.append({"role": "assistant", "content": answer})

# Calendar view
st.markdown("---")
if st.button("📋 Show calendar data"):
    calendar_data = get_calendar_matrix()
    rows = []
    for date, slots in calendar_data.items():
        for time, event in slots.items():
            rows.append({"Date": date, "Time": time, "Event": event})
    if rows:
        df = pd.DataFrame(rows).sort_values(by=["Date", "Time"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("📭 No events scheduled.")
