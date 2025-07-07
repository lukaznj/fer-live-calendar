from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build, Resource
import os
import json
import base64
import logging

from event import Event

def add_event(event: Event,  calendar_id: str, service: Resource) -> None:
    try:
        serialized_event: dict = {
            "start": {
                "dateTime": event.start_time,
                "timeZone": event.timezone,
            },
            "end": {
                "dateTime": event.end_time,
                "timeZone": event.timezone,
            },
            "summary": event.summary,
            "location": event.location,
            "description": event.description,
            "iCalUID": event.uid
        }

        returned_event: dict = service.events().insert(calendarId=calendar_id, body=serialized_event).execute()

        logging.info(f"Added event with ID: {returned_event.get("id")}.")

    except Exception as e:
        logging.error(f"Error adding a new event: {e}.")


def remove_event(event_uid: str, calendar_id: str, service: Resource):
    try:
        events_result: dict = service.events().list(
            calendarId=calendar_id,
            iCalUID=event_uid
        ).execute()

        events = events_result.get('items', [])

        if not events:
            logging.warning(f"No event found with iCalUID: {event_uid}.")
            return

        event_to_delete = events[0]
        event_google_id = event_to_delete['id']

        service.events().delete(calendarId=calendar_id, eventId=event_google_id).execute()

        logging.info(f"Removed event with iCalUID: {event_uid} and eventId: {event_google_id}.")

    except Exception as e:
        logging.error(f"Error removing event with iCalUID {event_uid}: {e}.")


def get_google_service() -> Resource:
    base64_str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_BASE64")
    if not base64_str:
        raise ValueError("Environment variable 'GOOGLE_SERVICE_ACCOUNT_JSON_BASE64' not set.")

    try:
        decoded_json_str = base64.b64decode(base64_str).decode('utf-8')

        credentials_info = json.loads(decoded_json_str)

    except (base64.binascii.Error, UnicodeDecodeError):
        raise ValueError("Variable 'GOOGLE_SERVICE_ACCOUNT_JSON_BASE64' not valid Base64 string.")
    except json.JSONDecodeError:
        raise ValueError("Decoded string not in valid JSON format.")

    credentials: Credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=["https://www.googleapis.com/auth/calendar"]
    )

    service: Resource = build("calendar", "v3", credentials=credentials)

    return service