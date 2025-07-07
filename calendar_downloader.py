import logging
import shutil
import urllib.request, urllib.error
import os
from textwrap import dedent


def download_latest_ics(url: str, file_name: str) -> None:
    try:
        urllib.request.urlretrieve(url, file_name)
        logging.info(f"Successfully downloaded the latest ics file.")

    except urllib.error.URLError as e:
        logging.error(f"Error downloading the latest ics file: {e}.")

    except Exception as e:
        logging.error(f"Unexpected error: {e}.")


def ics_file_updater(url: str) -> None:
    if os.path.isfile("previous.ics"):
        shutil.copy("latest.ics", "previous.ics")
        download_latest_ics(url, "latest.ics")

    else:
        with open("previous.ics", "w") as file:
            default_config: str = dedent("""\
                    BEGIN:VCALENDAR
                    VERSION:2.0
                    PRODID:-//QUILTCMS//NONSGML v1.0//EN
                    CALSCALE:GREGORIAN
                    END:VCALENDAR
                """)
            file.write(default_config)

        download_latest_ics(url, "latest.ics")



