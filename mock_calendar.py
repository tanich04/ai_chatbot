import os
import json
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    json_creds = os.environ.get("SERVICE_ACCOUNT_JSON")
    if not json_creds:
        raise Exception("Missing SERVICE_ACCOUNT_JSON env variable")

    info = json.loads(json_creds)
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("calendar", "v3", credentials=creds)


def create_event(date: str, time: str, title: str) -> str:
    service = get_calendar_service()
    start_dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %I:%M %p")
    end_dt = start_dt + datetime.timedelta(hours=1)
    event = {
        "summary": title,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Kolkata"},
    }
    service.events().insert(calendarId="primary", body=event).execute()
    return f"✅ Event '{title}' booked on {date} at {time}."


def check_availability(date: str) -> str:
    service = get_calendar_service()
    date_dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    start = date_dt.isoformat() + "Z"
    end = (date_dt + datetime.timedelta(days=1)).isoformat() + "Z"
    events = service.events().list(
        calendarId="primary",
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    slots = ["10:00 AM", "2:00 PM", "4:00 PM"]
    taken = [
        datetime.datetime.fromisoformat(e["start"]["dateTime"]).strftime("%I:%M %p")
        for e in events.get("items", []) if "dateTime" in e["start"]
    ]
    available = [slot for slot in slots if slot not in taken]
    return f"📅 Available slots on {date}: {', '.join(available) if available else 'No slots'}"


def get_calendar_day_view(date: str) -> str:
    service = get_calendar_service()
    date_dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    start = date_dt.isoformat() + "Z"
    end = (date_dt + datetime.timedelta(days=1)).isoformat() + "Z"
    events = service.events().list(
        calendarId="primary",
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    result = f"📅 Events on {date}:\n"
    for event in events.get("items", []):
        dt = event["start"].get("dateTime")
        if dt:
            parsed = datetime.datetime.fromisoformat(dt).strftime("%I:%M %p")
            result += f"⏰ {parsed} → {event['summary']}\n"
    return result.strip() or "📭 No events."


def get_calendar_week_view(date: str) -> str:
    service = get_calendar_service()
    start_dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    start = start_dt.isoformat() + "Z"
    end = (start_dt + datetime.timedelta(days=7)).isoformat() + "Z"
    events = service.events().list(
        calendarId="primary",
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    result = "📅 Events This Week:\n"
    for event in events.get("items", []):
        dt = event["start"].get("dateTime")
        if dt:
            parsed = datetime.datetime.fromisoformat(dt)
            result += f"⏰ {parsed.strftime('%Y-%m-%d %I:%M %p')} → {event['summary']}\n"
    return result.strip() or "📭 No events this week."
