from icalendar import Calendar
from event import Event


def parse_ics(file_name: str) -> list[Event]:
    with open(file_name, "r") as file:
        cal: Calendar = Calendar.from_ical(file.read())

    events: list[Event] = []
    for component in cal.walk("VEVENT"):
        event = Event(
            start_time=component.get("dtstart").dt.isoformat() if component.get("dtstart") else "",
            end_time=component.get("dtend").dt.isoformat() if component.get("dtend") else "",
            timezone="Europe/Zagreb",
            summary=str(component.get("summary", "")),
            location=str(component.get("location", "")),
            description=str(component.get("description", "")),
            uid=str(component.get("uid", ""))
        )
        events.append(event)

    return events


def diff_checker(current_events: list[Event], previous_events: list[Event]) -> tuple[list[Event], list[Event]]:
    """Returns a tuple, where the first element is a list of removed events, and the second is a list of new events"""

    previous_uids: set[str] = set()
    current_uids: set[str] = set()

    for event in previous_events:
        previous_uids.add(event.uid)

    for event in current_events:
        current_uids.add(event.uid)

    removed_uids: set[str] = previous_uids.difference(current_uids)
    added_uids: set[str] = current_uids.difference(previous_uids)

    removed_events: list[Event] = [event for event in previous_events if event.uid in removed_uids]
    added_events: list[Event] = [event for event in current_events if event.uid in added_uids]

    return removed_events, added_events

