import streamlit as st
import requests

st.title("📅 AI Calendar Booking Assistant")
st.caption("Ask anything like 'Book a meeting on Monday at 2PM'")

question = st.text_input("What would you like to do?")

if st.button("Ask"):
    if question:
        try:
            res = requests.post("https://aichatbot-production-a7c6.up.railway.app/chat", json={"question": question})
            st.write("**B**", res.json()["response"])
        except Exception as e:
            st.error(f"❌ Error: {e}")
