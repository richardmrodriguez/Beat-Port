##
##  OutlineChanges.m
##  BeatParsing
##
##  Created by Lauri-Matti Parppei on 26.6.2023.
##

#import "OutlineChanges.h"

from dataclasses import dataclass
from enum import Enum, auto

@dataclass
class OutlineChangeType(Enum):
    none = 0,
    SceneAdded = auto()
    SceneRemoved = auto()


class OutlineChanges:

    updated: list = []
    removed: list = []
    added: list = []
    needsFullUpdate: bool = False
    
    ## ?? syntax hurty
    def __init__(self) -> None:
        
        self.updated = []
        self.removed = []
        self.added = []

    def hasChanges(self) -> bool:
    
        return (
            (self.updated != [])
            or (self.removed != [])
            or (self.added != [])
            or (self.needsFullUpdate)
            )
    
    def copy(self):
        changes = OutlineChanges()
        changes.updated = self.updated
        changes.removed = self.removed
        changes.added = self.added
        changes.needsFullUpdate = self.needsFullUpdate
        
        return changes
    
    # ??? syntax hurty
    # memory management
    def copyWithZone(self, zone: NSZone) :
        return self.copy
    

