import os
import json
import dateparser
from typing import Optional
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON")
if not SERVICE_ACCOUNT_JSON:
    raise EnvironmentError("SERVICE_ACCOUNT_JSON is not set.")

info = json.loads(SERVICE_ACCOUNT_JSON)
creds = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/calendar"])
service = build("calendar", "v3", credentials=creds)
CALENDAR_ID = info["client_email"]


def normalize_date(date_str: str) -> Optional[datetime]:
    return dateparser.parse(date_str)

def format_time(time_str: str) -> str:
    parsed = dateparser.parse(time_str)
    return parsed.strftime("%I:%M %p") if parsed else time_str

def create_event(date_str: str, time_str: str, title: str) -> str:
    date = normalize_date(date_str)
    time = normalize_date(time_str)
    if not date or not time:
        return "❌ Invalid date or time."
    start = datetime.combine(date.date(), time.time())
    end = start + timedelta(hours=1)
    event = {
        'summary': title,
        'start': {'dateTime': start.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end.isoformat(), 'timeZone': 'Asia/Kolkata'}
    }
    service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return f"✅ Event '{title}' booked on {date.date()} at {format_time(time_str)}."

def check_availability(date_str: str) -> str:
    date = normalize_date(date_str)
    if not date:
        return "❌ Invalid date."
    start_of_day = datetime.combine(date.date(), datetime.min.time())
    end_of_day = datetime.combine(date.date(), datetime.max.time())
    events = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start_of_day.isoformat() + 'Z',
        timeMax=end_of_day.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute().get("items", [])
    busy_slots = [
        dateparser.parse(event["start"]["dateTime"]).strftime("%I:%M %p") for event in events
    ]
    all_slots = ["10:00 AM", "2:00 PM", "4:00 PM"]
    available = [slot for slot in all_slots if slot not in busy_slots]
    return f"📅 Available on {date.date()}: {', '.join(available) if available else 'No slots available'}"

def delete_event(date_str: str, time_str: str) -> str:
    date = normalize_date(date_str)
    target_time = normalize_date(time_str)
    if not date or not target_time:
        return "❌ Invalid input."
    events = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=date.isoformat() + 'Z',
        timeMax=(date + timedelta(days=1)).isoformat() + 'Z',
        singleEvents=True
    ).execute().get("items", [])
    for event in events:
        start = dateparser.parse(event["start"]["dateTime"])
        if start.hour == target_time.hour:
            service.events().delete(calendarId=CALENDAR_ID, eventId=event["id"]).execute()
            return f"🗑️ Deleted event '{event['summary']}' on {date.date()} at {format_time(time_str)}."
    return f"❌ No event at {format_time(time_str)} on {date.date()}."

def modify_event(date_str: str, old_time: str, new_time: str) -> str:
    date = normalize_date(date_str)
    old = normalize_date(old_time)
    new = normalize_date(new_time)
    if not date or not old or not new:
        return "❌ Invalid input."
    events = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=date.isoformat() + 'Z',
        timeMax=(date + timedelta(days=1)).isoformat() + 'Z',
        singleEvents=True
    ).execute().get("items", [])
    for event in events:
        start = dateparser.parse(event["start"]["dateTime"])
        if start.hour == old.hour:
            end = datetime.combine(date.date(), new.time()) + timedelta(hours=1)
            event['start']['dateTime'] = datetime.combine(date.date(), new.time()).isoformat()
            event['end']['dateTime'] = end.isoformat()
            service.events().update(calendarId=CALENDAR_ID, eventId=event['id'], body=event).execute()
            return f"✏️ Rescheduled '{event['summary']}' from {format_time(old_time)} to {format_time(new_time)}."
    return f"❌ No event at {format_time(old_time)} on {date.date()} to modify."

def get_calendar_day_view(date_str: str) -> str:
    date = normalize_date(date_str)
    if not date:
        return "❌ Invalid date."
    events = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=date.isoformat() + 'Z',
        timeMax=(date + timedelta(days=1)).isoformat() + 'Z',
        singleEvents=True
    ).execute().get("items", [])
    if not events:
        return f"📭 No events found on {date.date()}."
    return "\n".join([
        f"⏰ {dateparser.parse(e['start']['dateTime']).strftime('%I:%M %p')} → {e['summary']}" for e in events
    ])

def get_calendar_week_view(date_str: str) -> str:
    date = normalize_date(date_str)
    if not date:
        return "❌ Invalid date."
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=7)
    events = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start.isoformat() + 'Z',
        timeMax=end.isoformat() + 'Z',
        singleEvents=True
    ).execute().get("items", [])
    if not events:
        return "📭 No events scheduled this week."
    output = {}
    for e in events:
        d = dateparser.parse(e['start']['dateTime']).strftime('%Y-%m-%d')
        t = dateparser.parse(e['start']['dateTime']).strftime('%I:%M %p')
        output.setdefault(d, []).append(f"⏰ {t} → {e['summary']}")
    return "\n".join([f"📅 {d}:\n" + "\n".join(v) for d, v in output.items()])
