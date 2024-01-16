from enum import Enum, auto
from dataclasses import dataclass

### Line type enum
### Some types are only used in static parsing and/or exporting, such as `more` and `dualDialogueMore`. 
### `BeatFormatting` class also introduces supplementary types for internal use.

@dataclass
class LineType(Enum):
    (
        empty,
        section,
        synopse,
        titlePageTitle,
        titlePageAuthor,
        titlePageCredit,
        titlePageSource,
        titlePageContact,
        titlePageDraftDate,
        titlePageUnknown,
        heading,
        action,
        character,
        parenthetical,
        dialogue,
        dualDialogueCharacter,
        dualDialogueParenthetical,
        dualDialogue,
        transitionLine,
        lyrics,
        pageBreak,
        centered,
        shot,
        more, ### fake element for exporting
        dualDialogueMore, ### fake element for exporting
        typeCount
        ) = range(0, 26) ### This is the the max number of line types, used in `for` loops and enumerations, can be ignored
    
# print(LineType(15))