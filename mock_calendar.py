import os
import json
import dateparser
from typing import Dict
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_JSON = json.loads(os.getenv("SERVICE_ACCOUNT_JSON"))
credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_JSON, scopes=SCOPES)
calendar_service = build("calendar", "v3", credentials=credentials)
calendar_id = "primary"

SLOTS = ["10:00 AM", "2:00 PM", "4:00 PM"]


def normalize_date(date_str):
    parsed = dateparser.parse(date_str)
    return parsed.strftime("%Y-%m-%d") if parsed else date_str

def check_availability(date_str: str) -> str:
    date = normalize_date(date_str)
    booked = get_events_on(date)
    available = [s for s in SLOTS if s not in booked]
    return f"📅 Available slots on {date}: {', '.join(available) if available else 'No slots available'}"

def create_event(date_str: str, time: str, title: str) -> str:
    date = normalize_date(date_str)
    parsed_time = dateparser.parse(f"{date} {time}")
    end_time = (parsed_time + timedelta(hours=1)).isoformat()
    body = {
        'summary': title,
        'start': {'dateTime': parsed_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'}
    }
    calendar_service.events().insert(calendarId=calendar_id, body=body).execute()
    return f"✅ Event '{title}' booked on {date} at {time}."

def get_events_on(date: str) -> Dict[str, str]:
    start = datetime.strptime(date, "%Y-%m-%d")
    end = start + timedelta(days=1)
    events = calendar_service.events().list(
        calendarId=calendar_id,
        timeMin=start.isoformat() + 'Z',
        timeMax=end.isoformat() + 'Z',
        singleEvents=True,
        orderBy="startTime"
    ).execute().get("items", [])

    return {dateparser.parse(e["start"]["dateTime"]).strftime("%I:%M %p"): e["summary"] for e in events if "dateTime" in e["start"]}

def delete_event(date: str, time: str) -> str:
    events = calendar_service.events().list(calendarId=calendar_id).execute().get("items", [])
    for event in events:
        start = event.get("start", {}).get("dateTime")
        if start and date in start and time in dateparser.parse(start).strftime("%I:%M %p"):
            calendar_service.events().delete(calendarId=calendar_id, eventId=event["id"]).execute()
            return f"🗑️ Deleted event on {date} at {time}."
    return f"❌ No event found at {time} on {date}."

def modify_event(date: str, old_time: str, new_time: str) -> str:
    events = calendar_service.events().list(calendarId=calendar_id).execute().get("items", [])
    for event in events:
        start = event.get("start", {}).get("dateTime")
        if start and date in start and old_time in dateparser.parse(start).strftime("%I:%M %p"):
            parsed_time = dateparser.parse(f"{date} {new_time}")
            end_time = (parsed_time + timedelta(hours=1)).isoformat()
            event['start']['dateTime'] = parsed_time.isoformat()
            event['end']['dateTime'] = end_time
            calendar_service.events().update(calendarId=calendar_id, eventId=event['id'], body=event).execute()
            return f"✏️ Moved event from {old_time} to {new_time} on {date}."
    return f"❌ No event found to modify."

def get_calendar_day_view(date: str) -> str:
    events = get_events_on(date)
    if not events:
        return f"📭 No events on {date}."
    return f"📅 {date} Events:\n" + '\n'.join(f"⏰ {t} → {e}" for t, e in events.items())

def get_calendar_week_view(date: str) -> str:
    base = dateparser.parse(date)
    result = "📆 Week View:\n"
    for i in range(7):
        day = (base + timedelta(days=i)).strftime("%Y-%m-%d")
        result += get_calendar_day_view(day) + '\n'
    return result
