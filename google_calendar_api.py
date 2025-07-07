from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build, Resource
import os
import json
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
    secret_path: str = "/run/secrets/google_credentials"

    try:
        with open(secret_path, "r") as file:
            credentials_info: str = json.load(file)

    except FileNotFoundError:
        raise ValueError(f"Docker secret not found on path: {secret_path}")

    except json.JSONDecodeError:
        raise ValueError("Docker secret not in valid JSON format.")

    credentials: Credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=["https://www.googleapis.com/auth/calendar"]
    )

    service: Resource = build("calendar", "v3", credentials=credentials)

    return service