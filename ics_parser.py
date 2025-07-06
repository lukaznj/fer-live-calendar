from icalendar import Calendar
import os
import json


def lea(file_name: str) -> str:
    # Učitaj .ics datoteku
    with open(file_name, "r") as file:
        cal = Calendar.from_ical(file.read())

    # Pretvori u JSON
    events = []
    for component in cal.walk("VEVENT"):
        event = {
            "summary": str(component.get("summary", "")),
            "start": component.get("dtstart").dt.isoformat() if component.get("dtstart") else None,
            "end": component.get("dtend").dt.isoformat() if component.get("dtend") else None,
            "location": str(component.get("location", "")),
            "description": str(component.get("description", "")),
        }
        events.append(event)

    json_output = json.dumps(events, indent=2, ensure_ascii=False)
    return json_output
