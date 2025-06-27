import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="📅 AI Calendar Assistant", layout="centered")
st.title("📅 AI Calendar Assistant")

st.markdown("""
Welcome! Ask me anything about your schedule:
- Book a meeting on Friday at 3PM
- Delete my Tuesday 10AM meeting
- What's available next Monday?
- Show my calendar week view
""")

with st.form(key="chat_form"):
    user_input = st.text_input("You:", placeholder="e.g., Book a meeting on Monday at 2PM")
    submit = st.form_submit_button("Send")

if submit and user_input:
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json={"question": user_input},
            timeout=10
        )
        if response.status_code == 200:
            answer = response.json().get("response", "❌ No response")
        else:
            answer = f"❌ Error: {response.status_code}"
    except Exception as e:
        answer = f"❌ Error: {e}"

    st.markdown(f"**Bot:** {answer}")

# Calendar visualization
st.markdown("---")
st.subheader("📋 Calendar Events Overview")

try:
    calendar_res = requests.get("http://localhost:8000/calendar")
    if calendar_res.status_code == 200:
        calendar_json = calendar_res.json()
        flat_data = [
            {"Date": date, "Time": time, "Event": event}
            for date, times in calendar_json.items()
            for time, event in times.items()
        ]
        if flat_data:
            df = pd.DataFrame(flat_data)
            df_sorted = df.sort_values(by=["Date", "Time"])
            st.dataframe(df_sorted, use_container_width=True)
        else:
            st.info("📭 No events found in calendar.")
    else:
        st.error("❌ Could not fetch calendar data.")
except Exception as e:
    st.error(f"❌ Error fetching calendar: {e}")
