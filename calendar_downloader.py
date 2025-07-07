import logging
import shutil
import urllib.request, urllib.error
import os

from textwrap import dedent
from dotenv import load_dotenv

load_dotenv()

DATA_DIR: str = os.getenv("DATA_DIR")
LATEST_ICS_PATH:str = os.path.join(DATA_DIR, "latest.ics")
PREVIOUS_ICS_PATH:str = os.path.join(DATA_DIR, "previous.ics")

def ensure_data_dir_exists():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def download_latest_ics(url: str, file_path: str) -> None:
    try:
        urllib.request.urlretrieve(url, file_path)
        logging.info(f"Successfully downloaded the latest ics file.")

    except urllib.error.URLError as e:
        logging.error(f"Error downloading the latest ics file: {e}.")

    except Exception as e:
        logging.error(f"Unexpected error: {e}.")


def ics_file_updater(url: str) -> None:
    ensure_data_dir_exists()
    if os.path.isfile(PREVIOUS_ICS_PATH):
        if os.path.exists(LATEST_ICS_PATH):
            shutil.copy(LATEST_ICS_PATH, PREVIOUS_ICS_PATH)
        download_latest_ics(url, LATEST_ICS_PATH)

    else:
        with open(PREVIOUS_ICS_PATH, "w") as file:
            default_config: str = dedent("""\
                    BEGIN:VCALENDAR
                    VERSION:2.0
                    PRODID:-//QUILTCMS//NONSGML v1.0//EN
                    CALSCALE:GREGORIAN
                    END:VCALENDAR
                """)
            file.write(default_config)

        download_latest_ics(url, LATEST_ICS_PATH)



