import streamlit as st
import requests
import pandas as pd
from mock_calendar import load_calendar

st.set_page_config(page_title="📅 AI Calendar Bot", layout="centered")
st.title("📅 AI Calendar Booking Assistant")
st.markdown("What would you like to do?")

user_input = st.chat_input("Type here...")

if "history" not in st.session_state:
    st.session_state.history = []

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.spinner("Talking to calendar bot..."):
        try:
            response = requests.post("http://localhost:8000/chat", json={"question": user_input})
            response.raise_for_status()
            answer = response.json()["response"]
        except Exception as e:
            answer = f"❌ Error: Could not get response.\n{e}"
        st.session_state.history.append({"role": "assistant", "content": answer})

for chat in st.session_state.history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

with st.expander("📋 Show calendar data"):
    calendar_data = load_calendar()
    rows = []
    if calendar_data:
        for date, slots in calendar_data.items():
            for time, title in slots.items():
                rows.append({"Date": date, "Time": time, "Event": title})
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df.sort_values(by=["Date", "Time"]))
    else:
        st.info("📭 No events scheduled yet.")
