import logging
import time
import schedule
from dotenv import load_dotenv
from googleapiclient.discovery import Resource
from event import Event
from google_calendar_api import get_google_service, remove_event, add_event
from ics_parser import parse_ics, diff_checker
from calendar_downloader import ics_file_updater
import os


def calendar_change_check():
    logging.info("Starting new check cycle.")
    ics_download_url: str = os.getenv("CALENDAR_DOWNLOAD_URL")
    google_calendar_id: str = os.getenv("CALENDAR_ID")
    data_dir: str = os.getenv("DATA_DIR")

    latest_ics_path = os.path.join(data_dir, "latest.ics")
    previous_ics_path = os.path.join(data_dir, "previous.ics")

    ics_file_updater(ics_download_url)

    current_events: list[Event] = parse_ics(latest_ics_path)

    previous_events: list[Event] = parse_ics(previous_ics_path)

    removed_events, added_events = diff_checker(current_events, previous_events)

    if removed_events or added_events:
        service: Resource = get_google_service()

        for event in removed_events:
            remove_event(event.uid, google_calendar_id, service)

        for event in added_events:
            add_event(event, google_calendar_id, service)


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logging.info("Starting scheduler.")

    calendar_change_check()

    schedule.every().hour.do(calendar_change_check)

    while True:
        schedule.run_pending()
        time.sleep(1)