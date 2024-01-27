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
    # TODO: Dual Dialogue isn't checked yet.
    # TODO: transitionLines in the official fountain spec assume "TO:" will end a line, 
        # but this is oviously english centric.
        # Converse with Lauri and others about how to solve this
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

CUT TO:

int. HOUSE - NIGHT

!A lady SHRIEKS -- pan over to the LADY:

.HEADING

!!SHOT

LADY
(Screaming)
Get out of my house, you demons!

LADY 2^
(Also Screaming)
Yeah, get out!


CUT TO:

INT. HOUSE - DAYTIME

'''

parser = StaticFountainParser()
parsed_lines = parser.get_parsed_lines_from_raw_string(test_string)

print("------------------------------------")
def add_spacing(line_type_str: str):
    left_margin_spacing: int = 0

    str_chara = str(LineType.character)
    str_dial = str(LineType.dialogue)
    str_parenthetical = str(LineType.parenthetical)

    if line_type_str == str_chara:
        left_margin_spacing = 20
    elif line_type_str == str_dial:
        left_margin_spacing = 10
    elif line_type_str == str_parenthetical:
        left_margin_spacing = 15
    else:
        left_margin_spacing = 0
            

    return (" "*left_margin_spacing) + ""


def debug_print_lines_and_types():
    for line in parsed_lines:
        typestring = line.getTypeAsString()
        print(typestring.rjust(24) + " - " + line.string)

        #print(add_spacing(str(line.type)) + line.string)
        #print(line.string)
    print("Test")

debug_print_lines_and_types()

print("------------------------------------")


if LineType.empty == LineType.action:
    print("It's fucking empty")

# print(parsed_lines)
#pretty_print_screenplay(parsed_lines)