from dataclasses import dataclass, field
from enum import Enum

from line import Line #, LineType
# from helper_dataclasses import LocationAndLength as loc_len

@dataclass
class PageSizeStandard(Enum):
    A4: int = 0
    US_letter: int = 1

@dataclass
class DocumentModel:

    def _default_margins():
        return [1.0,    # Top
                1.0,    # Bottom
                1.5,    # Left
                1.0]    # Right
    title_page_lines: list[dict]
    lines: list[Line] = field(default_factory=list)
    page_size_standard: int = PageSizeStandard.US_letter
    page_DPI: float = 72.0

    margins_inches: list[float] = field(default_factory=_default_margins) # Top, Bottom, Left, Right

    using_rows_columns_sizing: bool = False
    page_size_rows_columns: list = field(default_factory=list) # example: [55, 61] is 55 rows tall by 61 columns wide


# newdoc = DocumentModel()

# print(newdoc)
#print(PageSizeStandard(newdoc.page_size_standard))
    
