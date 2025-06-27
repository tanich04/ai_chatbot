import streamlit as st
import requests
import json
from datetime import datetime

BACKEND_URL = "https://aichatbot-production-a7c6.up.railway.app/chat"  # ✅ Your FastAPI backend

st.set_page_config(page_title="📅 Calendar Bot", layout="centered")
st.title("🤖 AI Calendar Assistant")
st.caption("Ask me to book, delete, move or view your meetings!")

# --- Chat Section ---
if "chat" not in st.session_state:
    st.session_state.chat = []

user_input = st.chat_input("Ask something like 'Book meeting on Monday at 2PM'")
if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})
    with st.spinner("Talking to bot..."):
        try:
            response = requests.post(BACKEND_URL, json={"messages": st.session_state.chat})
            answer = response.json()["response"]
        except Exception as e:
            answer = f"❌ Error: {e}"
        st.session_state.chat.append({"role": "assistant", "content": answer})

# --- Display Conversation ---
for message in st.session_state.chat:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.divider()

# --- 📚 Calendar Logs Viewer ---
st.subheader("📚 Calendar Log History")

try:
    with open("calendar_log.json", "r") as f:
        logs = json.load(f)
except FileNotFoundError:
    logs = []

if logs:
    # -- Filter Options --
    st.markdown("### 🔎 Filter Logs")
    action_filter = st.multiselect("Filter by action", ["create", "modify", "delete"], default=[])
    date_filter = st.date_input("Filter by date (optional)", value=None)

    # -- Apply Filters --
    filtered_logs = []
    for log in logs:
        include = True
        if action_filter and log["action"] not in action_filter:
            include = False
        if date_filter:
            log_date = datetime.fromisoformat(log["timestamp"]).date()
            if log_date != date_filter:
                include = False
        if include:
            filtered_logs.append(log)

    # -- Display Logs --
    if filtered_logs:
        for log in reversed(filtered_logs):
            st.markdown(f"""
                🔹 **Action**: `{log['action'].capitalize()}`
                📅 **Date**: `{log['date']}`
                ⏰ **Time**: `{log['time']}`
                📝 **Title**: `{log.get('title', '')}`
                🕒 **Logged at**: `{log['timestamp']}`
                {"🔁 Moved from: `" + log.get("old_time", "") + "`" if log['action'] == 'modify' else ""}
                ---
            """)
    else:
        st.info("No logs found matching your filters.")
    
    # -- Download Button --
    st.download_button("📥 Download Full Log", data=json.dumps(logs, indent=2), file_name="calendar_log.json", mime="application/json")
else:
    st.info("No logs found.")
