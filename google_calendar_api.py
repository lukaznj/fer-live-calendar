from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build, Resource
import os
import json
import logging
from datetime import datetime

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
    credentials_file_name: str = os.getenv("CREDENTIALS_FILE_NAME")

    with open(credentials_file_name, "r") as file:
        credentials_info = json.load(file)

    # SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    # if not SERVICE_ACCOUNT_JSON:
    #     raise ValueError("Environment varijabla GOOGLE_SERVICE_ACCOUNT_JSON nije postavljena.")
    #
    # credentials_info = json.loads(SERVICE_ACCOUNT_JSON)

    credentials: Credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=["https://www.googleapis.com/auth/calendar"]
    )

    service: Resource = build("calendar", "v3", credentials=credentials)

    return service