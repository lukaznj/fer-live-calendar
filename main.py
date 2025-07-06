from dotenv import load_dotenv
import os

from ics_parser import lea
from latest_calendar_download import download_latest_updates

load_dotenv()

calendar_download_url: str = os.getenv("CALENDAR_DOWNLOAD_URL")
calendar_file_name: str = os.getenv("LATEST_CALENDAR_FILE_NAME")

download_latest_updates(calendar_download_url, calendar_file_name)

latest_json: str = lea(calendar_file_name)

print(latest_json)