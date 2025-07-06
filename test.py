from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json
import logging
from datetime import datetime



# Postavi logging
# logging.basicConfig(filename="/app/logs/calendar.log", level=logging.INFO)

# Učitaj vjerodajnice iz environment varijable
#SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

credentials_file_name: str = os.getenv("CREDENTIALS_FILE")

with open("service-account-credentials.json", "r") as file:
    credentials_info = json.load(file)

# if not SERVICE_ACCOUNT_JSON:
#     raise ValueError("Environment varijabla GOOGLE_SERVICE_ACCOUNT_JSON nije postavljena.")
#
# credentials_info = json.loads(SERVICE_ACCOUNT_JSON)
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Kreiraj vjerodajnice
credentials = service_account.Credentials.from_service_account_info(
    credentials_info, scopes=SCOPES
)

# Kreiraj Calendar API servis
service = build("calendar", "v3", credentials=credentials)

# Funkcija za dodavanje događaja
def dodaj_dogadjaj(summary, start_time, end_time):
    calendar_id: str = os.getenv("CALENDAR_ID")
    try:
        event = {
            "summary": summary,
            "location": "Zagreb",
            "description": "Događaj kreiran iz Docker kontejnera",
            "start": {
                "dateTime": start_time,
                "timeZone": "Europe/Zagreb",
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "Europe/Zagreb",
            },
        }
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        logging.info(f"Događaj kreiran: {event.get("id")} u {datetime.now()}")
        print(f"Događaj kreiran: {event.get("id")}")
    except Exception as e:
        logging.error(f"Greška pri dodavanju događaja: {e}")
        print(f"Greška: {e}")

# Primjer korištenja
if __name__ == "__main__":
    dodaj_dogadjaj(
        summary="LEA JE JOS UVIJEK GLUPACA",
        start_time="2025-07-11T10:00:00+02:00",
        end_time="2025-07-11T11:00:00+02:00"
    )