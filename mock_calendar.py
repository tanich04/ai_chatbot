import json
import dateparser
from typing import Dict
from datetime import datetime, timedelta

CALENDAR_FILE = "calendar.json"
LOG_FILE = "calendar_log.json"

def log_action(action_type, date, time, title="", old_time=None):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action_type,
        "date": date,
        "time": time,
        "title": title
    }
    if old_time:
        entry["old_time"] = old_time

    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []

    logs.append(entry)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def normalize_date(date_str: str) -> str:
    parsed = dateparser.parse(date_str)
    return parsed.strftime("%Y-%m-%d") if parsed else date_str

def load_calendar() -> Dict[str, Dict[str, str]]:
    try:
        with open(CALENDAR_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_calendar(data):
    with open(CALENDAR_FILE, "w") as f:
        json.dump(data, f, indent=2)

calendar_data: Dict[str, Dict[str, str]] = load_calendar()

def check_availability(date: str) -> str:
    date = normalize_date(date)
    slots = ["10:00 AM", "2:00 PM", "4:00 PM"]
    booked = calendar_data.get(date, {})
    available = [slot for slot in slots if slot not in booked]
    return f"📅 Available slots on {date}: {', '.join(available) if available else 'No slots available'}"

def create_event(date: str, time: str, title: str) -> str:
    date = normalize_date(date)
    calendar_data.setdefault(date, {})
    if time in calendar_data[date]:
        return f"❌ Slot {time} on {date} is already booked."
    calendar_data[date][time] = title
    save_calendar(calendar_data)
    log_action("create", date, time, title)
    return f"✅ Event '{title}' booked on {date} at {time}."

def delete_event(date: str, time: str) -> str:
    date = normalize_date(date)
    if date in calendar_data and time in calendar_data[date]:
        title = calendar_data[date].pop(time)
        save_calendar(calendar_data)
        log_action("delete", date, time, title)
        return f"🗑️ Deleted event '{title}' on {date} at {time}."
    return f"❌ No event found at {time} on {date}."

def modify_event(date: str, old_time: str, new_time: str) -> str:
    date = normalize_date(date)
    if date in calendar_data and old_time in calendar_data[date]:
        if new_time in calendar_data[date]:
            return f"❌ Cannot move to {new_time} on {date}; slot already booked."
        title = calendar_data[date].pop(old_time)
        calendar_data[date][new_time] = title
        save_calendar(calendar_data)
        log_action("modify", date, new_time, title, old_time=old_time)
        return f"✏️ Moved '{title}' from {old_time} to {new_time} on {date}."
    return f"❌ No event at {old_time} to modify on {date}."

def get_calendar_matrix() -> str:
    if not calendar_data:
        return "📭 No events scheduled."
    calendar_view = "🗓️ **Calendar Overview**\n\n"
    for date in sorted(calendar_data.keys()):
        calendar_view += f"📅 {date}:\n"
        for time in sorted(calendar_data[date].keys()):
            event = calendar_data[date][time]
            calendar_view += f"  ⏰ {time} → {event}\n"
    return calendar_view

def get_calendar_day_view(date: str) -> str:
    date = normalize_date(date)
    if date not in calendar_data:
        return f"📭 No events found on {date}."
    response = f"📅 Events on {date}:\n"
    for time, title in sorted(calendar_data[date].items()):
        response += f"  ⏰ {time} → {title}\n"
    return response

def get_calendar_week_view(date: str) -> str:
    parsed_date = dateparser.parse(date)
    if not parsed_date:
        return "❌ Invalid date provided."
    start = parsed_date - timedelta(days=parsed_date.weekday())
    week_dates = [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    response = "📅 Events This Week:\n"
    for d in week_dates:
        if d in calendar_data:
            response += f"\n🗓️ {d}:\n"
            for time, title in sorted(calendar_data[d].items()):
                response += f"  ⏰ {time} → {title}\n"
    return response if "🗓️" in response else "📭 No events this week."
