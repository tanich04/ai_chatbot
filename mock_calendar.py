import os
import json
import dateparser
from datetime import datetime, timedelta
from typing import Dict, List
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load and parse service account credentials from env
service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
credentials = service_account.Credentials.from_service_account_info(service_account_info)

# Build Google Calendar API client
service = build("calendar", "v3", credentials=credentials)
CALENDAR_ID = "primary"
SLOTS = ["10:00 AM", "2:00 PM", "4:00 PM"]

def normalize_date(date_str: str) -> str:
    parsed = dateparser.parse(date_str)
    return parsed.strftime("%Y-%m-%d") if parsed else date_str

def create_event(date: str, time: str, title: str) -> str:
    date = normalize_date(date)
    time_obj = dateparser.parse(f"{date} {time}")
    if not time_obj:
        return f"❌ Invalid date/time."
    start_time = time_obj.isoformat()
    end_time = (time_obj + timedelta(hours=1)).isoformat()
    event = {
        'summary': title,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'}
    }
    service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return f"✅ Event '{title}' booked on {date} at {time}."

def check_availability(date: str) -> str:
    date = normalize_date(date)
    start = dateparser.parse(f"{date} 00:00")
    end = start + timedelta(days=1)
    events = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start.isoformat() + 'Z',
        timeMax=end.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])
    booked = [dateparser.parse(e['start']['dateTime']).strftime("%I:%M %p") for e in events]
    available = [slot for slot in SLOTS if slot not in booked]
    return f"📅 Available slots on {date}: {', '.join(available) if available else 'No slots available'}"

def delete_event(date: str, time: str) -> str:
    date = normalize_date(date)
    start = dateparser.parse(f"{date} 00:00")
    end = start + timedelta(days=1)
    events = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start.isoformat() + 'Z',
        timeMax=end.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])
    for e in events:
        if dateparser.parse(e['start']['dateTime']).strftime("%I:%M %p") == time:
            service.events().delete(calendarId=CALENDAR_ID, eventId=e['id']).execute()
            return f"🗑️ Deleted event on {date} at {time}."
    return f"❌ No event found at {time} on {date}."

def modify_event(date: str, old_time: str, new_time: str) -> str:
    date = normalize_date(date)
    start = dateparser.parse(f"{date} 00:00")
    end = start + timedelta(days=1)
    events = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start.isoformat() + 'Z',
        timeMax=end.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])
    for e in events:
        if dateparser.parse(e['start']['dateTime']).strftime("%I:%M %p") == old_time:
            new_start = dateparser.parse(f"{date} {new_time}").isoformat()
            new_end = (dateparser.parse(f"{date} {new_time}") + timedelta(hours=1)).isoformat()
            e['start']['dateTime'] = new_start
            e['end']['dateTime'] = new_end
            service.events().update(calendarId=CALENDAR_ID, eventId=e['id'], body=e).execute()
            return f"✏️ Moved event from {old_time} to {new_time} on {date}."
    return f"❌ No event at {old_time} to modify on {date}."

def get_calendar_day_view(date: str) -> str:
    date = normalize_date(date)
    start = dateparser.parse(date)
    end = start + timedelta(days=1)
    events = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start.isoformat() + 'Z',
        timeMax=end.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute().get("items", [])
    if not events:
        return f"📭 No events found on {date}."
    return "\n".join([f"⏰ {dateparser.parse(e['start']['dateTime']).strftime('%I:%M %p')} → {e['summary']}" for e in events])

def get_calendar_week_view(date: str) -> str:
    base = dateparser.parse(date)
    start = base - timedelta(days=base.weekday())
    end = start + timedelta(days=7)
    events = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start.isoformat() + 'Z',
        timeMax=end.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute().get("items", [])
    if not events:
        return "📭 No events this week."
    return "\n".join([f"🗓️ {dateparser.parse(e['start']['dateTime']).strftime('%Y-%m-%d %I:%M %p')} → {e['summary']}" for e in events])
