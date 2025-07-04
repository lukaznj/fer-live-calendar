from dotenv import load_dotenv
import os
from latest_calendar_download import download_latest_updates

load_dotenv()

CALENDAR_DOWNLOAD_URL: str = os.getenv("CALENDAR_DOWNLOAD_URL")

download_latest_updates(CALENDAR_DOWNLOAD_URL)