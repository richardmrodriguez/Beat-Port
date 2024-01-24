
from dataclasses import dataclass
from enum import Enum


# This dataclass is a struct which holds the location (index) and length (int) of a string within a superstring.
# Must compare with the Line class; 
@dataclass
class LocationAndLength:
    location: int
    length: int