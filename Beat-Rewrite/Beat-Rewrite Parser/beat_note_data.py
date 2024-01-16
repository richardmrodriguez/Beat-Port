 ##
 ##  BeatNoteData.m
 ##  BeatParsing
 ##
 ##  Created by Lauri-Matti Parppei on 1.4.2023.
 ##

 
 ## Note Object
 
 ## Note parsing is done by the parser. It creates `BeatNoteData` objects for each `[[note]]` on a line.
 ## Each note knows its own `range`, `type` (whether it's a normal note, color, marker, or beat), `color` (if applicable) and if the note is part of a `multiline` note block.

from dataclasses import dataclass
from enum import Enum,auto

@dataclass
class NoteType(Enum):
    NoteTypeNormal = 0,
    NoteTypeMarker = auto()
    NoteTypeBeat = auto()
    NoteTypeColor = auto()

class BeatNoteData:
    
    content: str
    color: str
    _range: range
    type: NoteType
    multiline: bool # How or where is this used ??

    def initWithContent(self, content: str, color: str, _range: range, type: NoteType):
        if (self):
            self.content = content
            self.color = color
            self._range = range
            self.type = type

        return self
    
    def withNote(self, text: str, range: range) -> any:
        content = text
        color = ""
        
        type = NoteType.NoteTypeNormal
        lowercaseText = content.lower()
        
        if lowercaseText.find("marker")== 0:
            ## Check if this note is a marker
            type = NoteType.NoteTypeMarker
        
        elif (lowercaseText in BeatNoteData.colors) or (lowercaseText.find("color") == 0):
            ## This note only contains a color
            type = NoteType.NoteTypeColor
        
        elif (lowercaseText.find("beat") == 0) or (lowercaseText.find("storyline") == 0):
            type = NoteType.NoteTypeBeat
        
        elif ":" in lowercaseText:
            ## Check if this note has a color assigned to it, ie. [[red: Hello World]]
            i: int = lowercaseText.find(":")
            c: str = lowercaseText[:i]
            if (len(c) > 0) and ((c[0] == '#') or (c in BeatNoteData.colors)):
                color = c
                content = text[i+1:]
            
        
            
        return self.initWithContent(content=content, color=color, range=range, type=type)

    # NOTE: ?? isn't this array of colors in the continuous fountain parser also?
    def colors() -> list[str]:
        colors: list
        if (colors == []) or (colors is None):
            colors = ["red", 
                      "blue", 
                      "green", 
                      "pink", 
                      "magenta", 
                      "gray", 
                      "purple", 
                      "cyan", 
                      "teal", 
                      "yellow", 
                      "orange", 
                      "brown",
                      ]
        return colors
    

    ### Returns JSON representation
    def _json(self) -> dict:
        return {
            "content": (self.content != None) if self.content else "",
            "color": (self.color != None) if self.color else "",
            "range": { 
                "location": (self._range.location),  # !! syntax hurty
                "length": (self._range.length) 
                },
            "type": self.typeAsString()
        }
    

    def typeAsString(self) -> str:
        match self.type:
            case NoteType.NoteTypeNormal:
                return "note"
            case NoteType.NoteTypeColor:
                return "color"
            case NoteType.NoteTypeMarker:
                return "marker"
            case NoteType.NoteTypeBeat:
                return "beat"
            case _:
                return ""
        
