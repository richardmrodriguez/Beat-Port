from continuous_fountain_parser import ContinuousFountainParser
from static_fountain_parser import StaticFountainParser
from line import Line, LineType
from helper_dataclasses import LocationAndLength as loc_len


# TODO: make the parser actually work lmao
# ITEMS:
    # 1. Get Title Page Lines - def get_title_page_lines
    # 2. Get standard fountain lines (action, character, dialogue, transition, shot) - get_fountain_lines
    # 3. Get Beat lines (notes, colors, metadata)
# TODO: Create a `StaticParser` class, 
# which is totally separate from the "Continuous" parsing (hot-reload)

# TODO: The Line class has a bunch of functions and stuff in it,
# should probably separate into `LineData` and `LineFuncs`.


class ParserDelegate:
    printSceneNumbers: bool
    # documentSettings: BeatDocumentSettings
    characterInputForLine: Line
    selectedRange: loc_len
    disabledTypes: set

    def sceneNumberingStartsFrom() -> int:
        pass
    def reformatLinesAtIndices(indices: set):
        pass
    def applyFormatChanges():
        pass

test_string = '''\
Title:
_**AMONG US**_
The Sequel
Credit: Written by
Author: John Gamer
Source: Story by InnerSloth
Draft date: 04 - 09 - 2024
Contact: john@gaming.sus

int. HOUSE - NIGHT

!A lady SHRIEKS -- pan over to the LADY:

.HEADING

..SHOT

LADY
(Screaming)
Get out of my house, you demons!

'''

parser = StaticFountainParser()
parsed_lines = parser.get_parsed_lines_from_raw_string(test_string)

print("------------------------------------")

for line in parsed_lines:
    typestring = str(line.type)[len("LineType."):]
    print(typestring.rjust(20) + " - " + line.string)
print("Test")