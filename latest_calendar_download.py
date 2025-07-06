import urllib.request, urllib.error
import os

def download_latest_updates(url: str, file_name: str) -> None:
    try:
        urllib.request.urlretrieve(url, file_name)

    except urllib.error.URLError as e:

        print(f"Error while downloading the latest ics file from FER: {e}")

    except Exception as e:

        print(f"Unexpected error: {e}")