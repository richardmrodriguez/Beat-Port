from continuous_fountain_parser import ContinuousFountainParser
from static_fountain_parser import StaticFountainParser
from line import Line, LineType
from helper_dataclasses import LocationAndLength as loc_len

# ITEMS:
    #0. DOING: Re-organize codebase to be more modular and workable
    #1. TODO: Finish Fountain Parsing
    #2. TODO: parse for Beat metadata
    #3: TODO: parse for formatting + ranges (Bold, italic, etc.)


#1 - FOUNTAIN PARSING
    # TODO: Boneyards don't work yet.
    # TODO: Notes don't work yet.

#0 - CODE STRUCTURE
# TODO: The Line class has a bunch of functions and stuff in it,
# should probably separate into `LineData` and `LineFuncs`.

test_string = '''\
Title:
    _**AMONG US**_
    The Sequel
Credit: Written by
Author:
    John Gamer
    Jane Gaming
Source: Story by InnerSloth
Draft date: 04 - 09 - 2024
Contact: john@gaming.sus

FADE IN:

int. HOUSE - NIGHT

!A lady SHRIEKS -- pan over to the LADY:

.HEADING

!!SHOT

LADY
(Screaming)
Get out of my house, you demons!

The lady swings a big sword,
SLASHES,
and destroys a perfectly good sofa.

LADY 2^
(Also Screaming)
Yeah, get out!


===
# ACT 2
## The Big Scaries

ARBITRARY TRANSITION:

INT. HOUSE - DAYTIME
=This is the big moment.

'''

parser = StaticFountainParser()
lines: list[Line] = []
parsed_lines = parser.get_parsed_lines_from_raw_string(test_string)

def add_spacing(line: Line):
    left_margin_spacing: int = 0

    if line.isAnyCharacter():
        left_margin_spacing = 20
    elif line.isAnyDialogue():
        left_margin_spacing = 10
    elif line.isAnyParenthetical():
        left_margin_spacing = 15
    else:
        left_margin_spacing = 0
            

    return (" "*left_margin_spacing)

def pretty_print():
    for line in parsed_lines:
        print(add_spacing(line) + line.string)

def print_title_page_elements(titlepage):
    for e in titlepage:
        print(e)


def debug_print_lines_and_types():
    for line in parsed_lines:
        typestring = line.getTypeAsString()
        print(typestring.rjust(24) + " - " + line.string)

print("------------------------------------")
debug_print_lines_and_types()
print("------------------------------------")
