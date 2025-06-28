import datetime
import pytz
from typing import Dict
from google.oauth2 import service_account
from googleapiclient.discovery import build
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Get credentials from Streamlit secrets
credentials = service_account.Credentials.from_service_account_info(
    {
        "type": "service_account",
        "project_id": st.secrets["GOOGLE_PROJECT_ID"],
        "private_key_id": st.secrets["GOOGLE_PRIVATE_KEY_ID"],
        "private_key": st.secrets["GOOGLE_PRIVATE_KEY"].replace("\\n", "\n"),
        "client_email": st.secrets["GOOGLE_CLIENT_EMAIL"],
        "client_id": st.secrets["GOOGLE_CLIENT_ID"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["GOOGLE_CLIENT_CERT_URL"]
    },
    scopes=SCOPES
)

calendar_service = build('calendar', 'v3', credentials=credentials)
CALENDAR_ID = st.secrets["GOOGLE_CALENDAR_ID"]

def check_availability(date: str) -> str:
    date_obj = datetime.datetime.fromisoformat(date)
    start = date_obj.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
    end = date_obj.replace(hour=23, minute=59, second=59).isoformat() + 'Z'

    events_result = calendar_service.events().list(
        calendarId=CALENDAR_ID, timeMin=start, timeMax=end, singleEvents=True,
        orderBy='startTime').execute()

    events = events_result.get('items', [])
    booked_slots = [e['start']['dateTime'].split('T')[1][:5] for e in events if 'dateTime' in e['start']]

    return f"Booked times on {date}: {', '.join(booked_slots) if booked_slots else 'None'}"

def create_event(date: str, time: str, title: str) -> str:
    start_dt = datetime.datetime.fromisoformat(f"{date}T{time}:00")
    end_dt = start_dt + datetime.timedelta(hours=1)

    event = {
        'summary': title,
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Kolkata'}
    }

    calendar_service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return f"✅ Event '{title}' booked on {date} at {time}."

def delete_event(date: str, time: str) -> str:
    start_dt = datetime.datetime.fromisoformat(f"{date}T{time}:00").isoformat() + 'Z'
    end_dt = datetime.datetime.fromisoformat(f"{date}T{time}:00") + datetime.timedelta(hours=1)
    end_dt = end_dt.isoformat() + 'Z'

    events = calendar_service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start_dt,
        timeMax=end_dt,
        singleEvents=True
    ).execute().get('items', [])

    if not events:
        return f"❌ No event found at {time} on {date}."

    for event in events:
        calendar_service.events().delete(calendarId=CALENDAR_ID, eventId=event['id']).execute()

    return f"🗑️ Deleted event at {time} on {date}."

def modify_event(date: str, old_time: str, new_time: str) -> str:
    start_dt = datetime.datetime.fromisoformat(f"{date}T{old_time}:00").isoformat() + 'Z'
    end_dt = datetime.datetime.fromisoformat(f"{date}T{old_time}:00") + datetime.timedelta(hours=1)
    end_dt = end_dt.isoformat() + 'Z'

    events = calendar_service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start_dt,
        timeMax=end_dt,
        singleEvents=True
    ).execute().get('items', [])

    if not events:
        return f"❌ No event to move from {old_time} on {date}."

    event = events[0]
    new_start = datetime.datetime.fromisoformat(f"{date}T{new_time}:00")
    new_end = new_start + datetime.timedelta(hours=1)

    event['start']['dateTime'] = new_start.isoformat()
    event['end']['dateTime'] = new_end.isoformat()
    event['start']['timeZone'] = 'Asia/Kolkata'
    event['end']['timeZone'] = 'Asia/Kolkata'

    calendar_service.events().update(calendarId=CALENDAR_ID, eventId=event['id'], body=event).execute()
    return f"✏️ Moved event to {new_time} on {date}."
