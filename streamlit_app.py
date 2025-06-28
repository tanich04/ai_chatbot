import streamlit as st
import requests

st.title("📅 AI Google Calendar Booking Assistant")
st.caption("Ask me to schedule, modify, or view your meetings!")

query = st.text_input("What would you like to do?")

if st.button("Ask") and query:
    try:
        response = requests.post("https://aichatbot-production-a7c6.up.railway.app/chat", json={"question": query})
        st.write("**Bot:**", response.json()["response"])
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
