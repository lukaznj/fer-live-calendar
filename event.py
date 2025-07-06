from dataclasses import dataclass

@dataclass
class Event:
    uid: str
    start_time: str = ""
    end_time: str = ""
    timezone: str = ""
    summary: str = ""
    location: str = ""
    description: str = ""