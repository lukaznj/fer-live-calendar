import base64
import json
import logging
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential

from event import Event

def _is_rate_limit_error(exception: Exception) -> bool:
    return isinstance(exception, HttpError) and exception.resp.status in [403, 429]

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=_is_rate_limit_error
)
def add_events_batch(events: list[Event], calendar_id: str, service: Resource) -> None:
    if not events:
        logging.info("No events to add in batch.")
        return

    batch = service.new_batch_http_request()

    def batch_callback(request_id, response, exception):
        if exception:
            logging.error(f"Error in batch for request_id '{request_id}': {exception}")
        else:
            logging.info(f"Successfully added event with ID: {response.get('id')} (request_id: {request_id}).")

    for event in events:
        serialized_event = {
            "start": {"dateTime": event.start_time, "timeZone": event.timezone},
            "end": {"dateTime": event.end_time, "timeZone": event.timezone},
            "summary": event.summary,
            "location": event.location,
            "description": event.description,
            "iCalUID": event.uid,
        }
        batch.add(
            service.events().insert(calendarId=calendar_id, body=serialized_event),
            request_id=event.uid,
            callback=batch_callback
        )

    logging.info(f"Executing batch request to add {len(events)} events...")
    batch.execute()
    logging.info("Batch request for adding events finished.")


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=_is_rate_limit_error
)
def remove_events_batch(event_uids: list[str], calendar_id: str, service: Resource) -> None:
    if not event_uids:
        logging.info("No events to remove in batch.")
        return

    events_to_delete: list[dict] = []
    for uid in event_uids:
        try:
            events_result = service.events().list(calendarId=calendar_id, iCalUID=uid).execute()
            items = events_result.get("items", [])
            if items:
                events_to_delete.append({'uid': uid, 'google_id': items[0]['id']})
            else:
                logging.warning(f"For removal, event with iCalUID '{uid}' not found.")
        except HttpError as e:
            logging.error(f"Failed to fetch event with iCalUID '{uid}' for deletion: {e}")
            continue

    if not events_to_delete:
        logging.info("No existing events found to remove in batch.")
        return

    batch = service.new_batch_http_request()

    def batch_callback(request_id, _, exception):
        if exception:
            logging.error(f"Error in batch for request_id '{request_id}': {exception}")
        else:
            logging.info(f"Successfully removed event with iCalUID: {request_id}.")

    for item in events_to_delete:
        batch.add(
            service.events().delete(calendarId=calendar_id, eventId=item["google_id"]),
            request_id=item["uid"],
            callback=batch_callback
        )

    logging.info(f"Executing batch request to remove {len(events_to_delete)} events...")
    batch.execute()
    logging.info("Batch request for removing events finished.")

def get_google_service() -> Resource:
    base64_str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_BASE64")
    if not base64_str:
        raise ValueError("Environment variable 'GOOGLE_SERVICE_ACCOUNT_JSON_BASE64' not set.")

    try:
        decoded_json_str = base64.b64decode(base64_str).decode("utf-8")
        credentials_info = json.loads(decoded_json_str)
    except (base64.binascii.Error, UnicodeDecodeError):
        raise ValueError("Variable 'GOOGLE_SERVICE_ACCOUNT_JSON_BASE64' not a valid Base64 string.")
    except json.JSONDecodeError:
        raise ValueError("Decoded string is not in a valid JSON format.")

    credentials = service_account.Credentials.from_service_account_info(
        credentials_info, scopes=["https://www.googleapis.com/auth/calendar"]
    )

    service = build("calendar", "v3", credentials=credentials)
    return service