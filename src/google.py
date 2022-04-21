from datetime import datetime
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from src.models import User
from src.settings import get_settings
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

settings = get_settings()


def generate_auth_url(user_id: str):
    auth_url = settings.google_auth_flow.authorization_url()[0]
    parsed = urlparse(auth_url)
    qs = parse_qs(parsed.query)
    qs["state"] = user_id
    new_qs = urlencode(qs, doseq=True)
    auth_url = urlunparse([new_qs if i == 4 else x for i, x in enumerate(parsed)])

    return auth_url


def insert_event(user: User, date: datetime, text: str) -> Any:
    calendar_service = build("calendar", "v3", credentials=user.google_credentials)
    event = {
        "summary": "Personal Secretary Bot event",
        "description": text,
        "start": {"dateTime": date.isoformat() + "+03:00", "timeZone": "Europe/Moscow"},
        "end": {"dateTime": date.isoformat() + "+03:00", "timeZone": "Europe/Moscow"},
        "reminders": {
            "useDefault": True,
        },
    }
    event = calendar_service.events().insert(calendarId="primary", body=event).execute()

    return event


def cancel_event(user: User, event_id: str):
    calendar_service = build("calendar", "v3", credentials=user.google_credentials)
    try:
        calendar_service.events().delete(calendarId="primary", eventId=event_id).execute()
    except HttpError:
        pass
