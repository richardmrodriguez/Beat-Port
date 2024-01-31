from dataclasses import dataclass

from helper_dataclasses import LocationAndLength as loc_len

@dataclass
class Note:
    note_content: str
    raw_location_length: loc_len
