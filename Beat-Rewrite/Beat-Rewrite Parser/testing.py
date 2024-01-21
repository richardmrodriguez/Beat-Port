from continuous_fountain_parser import ContinuousFountainParser
from line import Line, LineType
from helper_dataclasses import LocationAndLength as loc_len


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

test_string = '''TITLE: Test String
CREDIT: Some Guy IDK

INT. HOUSE - NIGHT

A lady SHRIEKS -- pan over to the LADY:

LADY
(Screaming)
Get out of my house, you demons!

'''

parser = ContinuousFountainParser(string=test_string)

# title_lines = parser.titlePageLines()
# for line in title_lines:
#     print(line.string, "Line type:", line.type)


for n in parser.parseText(test_string):
    print(n.string, "Line type:", n.type)
# print(parser.titlePageForString("TITLE: HOUSE \nCREDIT: Some Guy"))
print("Test")