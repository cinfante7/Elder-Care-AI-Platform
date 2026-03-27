import streamlit as st
import datetime
import json
import os

REMINDER_FILE = "data/med_reminders.json"
COMMUNITY_EVENTS_FILE = "data/community_events.json"

def load_reminders():
    if not os.path.exists(REMINDER_FILE):
        return [], 1
    try:
        with open(REMINDER_FILE, "r") as f:
            data = json.load(f)
            reminders = data.get("reminders", [])
            next_id = data.get("next_id", 1)
            return reminders, next_id
    except Exception as e:
        print(f"Error loading reminders: {e}")
        return [], 1

def save_reminders(reminders, next_id):
    try:
        with open(REMINDER_FILE, "w") as f:
            json.dump({"reminders": reminders, "next_id": next_id}, f, indent=2)
    except Exception as e:
        print(f"Error saving reminders: {e}")

def load_community_events():
    if not os.path.exists(COMMUNITY_EVENTS_FILE):
        # Initialize with some default community events
        default_events = [
            {
                "id": 1,
                "name": "Bingo Night",
                "description": "Weekly bingo game with prizes",
                "day": "Friday",
                "time": "19:00",
                "location": "Community Center",
                "recurrence": "weekly",
                "status": "active"
            },
            {
                "id": 2,
                "name": "Movie Night",
                "description": "Classic movie screening with popcorn",
                "day": "Saturday",
                "time": "18:30",
                "location": "Activity Room",
                "recurrence": "weekly",
                "status": "active"
            },
            {
                "id": 3,
                "name": "Exercise Class",
                "description": "Gentle exercise for seniors",
                "day": "Monday",
                "time": "10:00",
                "location": "Fitness Room",
                "recurrence": "weekly",
                "status": "active"
            },
            {
                "id": 4,
                "name": "Book Club",
                "description": "Discussion of monthly book selection",
                "day": "Wednesday",
                "time": "14:00",
                "location": "Library",
                "recurrence": "monthly",
                "status": "active"
            },
            {
                "id": 5,
                "name": "Craft Circle",
                "description": "Knitting, crochet, and other crafts",
                "day": "Tuesday",
                "time": "13:00",
                "location": "Craft Room",
                "recurrence": "weekly",
                "status": "active"
            },
            {
                "id": 6,
                "name": "Gardening Club",
                "description": "Community garden maintenance and tips",
                "day": "Thursday",
                "time": "09:00",
                "location": "Community Garden",
                "recurrence": "weekly",
                "status": "active"
            },
            {
                "id": 7,
                "name": "Music Hour",
                "description": "Sing-along and music appreciation",
                "day": "Sunday",
                "time": "15:00",
                "location": "Music Room",
                "recurrence": "weekly",
                "status": "active"
            },
            {
                "id": 8,
                "name": "Technology Help",
                "description": "Learn to use smartphones and tablets",
                "day": "Wednesday",
                "time": "10:00",
                "location": "Computer Lab",
                "recurrence": "weekly",
                "status": "active"
            },
            {
                "id": 9,
                "name": "Walking Group",
                "description": "Group walk around the community",
                "day": "Tuesday",
                "time": "08:00",
                "location": "Main Entrance",
                "recurrence": "weekly",
                "status": "active"
            },
            {
                "id": 10,
                "name": "Game Day",
                "description": "Board games and card games",
                "day": "Saturday",
                "time": "14:00",
                "location": "Game Room",
                "recurrence": "weekly",
                "status": "active"
            }
        ]
        save_community_events(default_events, 11)
        return default_events, 11
    try:
        with open(COMMUNITY_EVENTS_FILE, "r") as f:
            data = json.load(f)
            events = data.get("events", [])
            next_id = data.get("next_id", 1)
            return events, next_id
    except Exception as e:
        print(f"Error loading community events: {e}")
        return [], 1

def save_community_events(events, next_id):
    try:
        with open(COMMUNITY_EVENTS_FILE, "w") as f:
            json.dump({"events": events, "next_id": next_id}, f, indent=2)
    except Exception as e:
        print(f"Error saving community events: {e}")

def init_reminders():
    if "med_reminders" not in st.session_state or "next_med_id" not in st.session_state:
        reminders, next_id = load_reminders()
        st.session_state.med_reminders = reminders
        st.session_state.next_med_id = next_id

def init_community_events():
    if "community_events" not in st.session_state or "next_event_id" not in st.session_state:
        events, next_id = load_community_events()
        st.session_state.community_events = events
        st.session_state.next_event_id = next_id

def add_med_reminder(med_name: str, time_str: str, recurrence: str = "none", note: str = ""):
    reminder = {
        "id": st.session_state.next_med_id,
        "med_name": med_name,
        "time": time_str,
        "recurrence": recurrence,
        "note": note,
        "status": "pending",
        "timestamp": None,
    }
    st.session_state.med_reminders.append(reminder)
    st.session_state.next_med_id += 1
    save_reminders(st.session_state.med_reminders, st.session_state.next_med_id)

def update_med_status(reminder_id: int, status: str):
    for rem in st.session_state.med_reminders:
        if rem["id"] == reminder_id:
            rem["status"] = status
            rem["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break
    save_reminders(st.session_state.med_reminders, st.session_state.next_med_id)

def get_pending_reminders(current_time: str, window_minutes: int = 2):
    try:
        now = datetime.datetime.strptime(current_time, "%H:%M")
    except Exception as e:
        print(f"Error parsing current_time: {e}")
        return []

    pending = []
    for rem in st.session_state.med_reminders:
        if rem["status"] == "pending":
            try:
                rem_time = datetime.datetime.strptime(rem["time"], "%H:%M")
                delta_minutes = abs((now - rem_time).total_seconds() / 60)
                if delta_minutes <= window_minutes:
                    pending.append(rem)
            except Exception as e:
                print(f"Error parsing reminder time '{rem['time']}': {e}")
    return pending

def get_upcoming_community_events():
    """Get community events for the next 7 days"""
    events = st.session_state.get("community_events", [])
    upcoming = []
    today = datetime.datetime.now()
    
    for event in events:
        if event["status"] == "active":
            # Simple logic: if today matches the event day, it's upcoming
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            today_name = day_names[today.weekday()]
            
            if event["day"] == today_name:
                upcoming.append(event)
    
    return upcoming

def add_community_event(name, description, day, time, location, recurrence="weekly"):
    event = {
        "id": st.session_state.next_event_id,
        "name": name,
        "description": description,
        "day": day,
        "time": time,
        "location": location,
        "recurrence": recurrence,
        "status": "active"
    }
    st.session_state.community_events.append(event)
    st.session_state.next_event_id += 1
    save_community_events(st.session_state.community_events, st.session_state.next_event_id)
