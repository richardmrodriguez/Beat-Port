##  static_fountain_parser.py
##  Beat
##
##  Copyright © 2016 Hendrik Noeller. All rights reserved.
##  Parts copyright © 2019-2023 Lauri-Matti Parppei. All rights reserved.

##  Parts copyright © 2024 Richard Mamaril Rodriguez. All rights reserved.

## This parser is based upon the ContinuousFountainParser from Lauri-Matti Parppei's Beat,
## which itself is based upon Writer by Hendrik Noeller.

## This has been ported / translated from Objective-C to Python.
## As a result, many omissions and structural changes are made,
## though the core parsing logic remains largely the same.

##  Relased under GPL


import uuid

from helper_dataclasses import LocationAndLength as loc_len
import helper_funcs as hf

from line import Line, LineType
from parser_data_classes.formatting_characters import FormattingCharacters as fc

from document_model import DocumentModel as Document

class StaticFountainParser:
    lines: list[Line] = []
    pure_fountain_parsing: bool = False # TODO use to enable or disable Beat-specific QoL parsing methods (?)
    disabledTypes: list[any] = []

    # ----- Public Functions ----- 
    def get_parsed_lines_from_raw_string(self, text: str) -> list[Line]:
        """
        This function takes a raw string `text` which represents an entire document or file.
        
        This returns a list of fountain-parsed `Line` objects. Each `Line` contains the `string`, the `LineType` for the line, and other metadata as properties.
        """

        return self._get_parsed_lines_from_line_array(
            self._get_unparsed_line_array_from_raw_string(text)
            )

    # ----- Private Functions ----- 
    @classmethod
    def _get_parsed_lines_from_line_array(cls, lines: list[Line]):
        # the actual parsing
        index: int = 0
        for l in range(len(lines)):
            line = lines[l]
            print("Index", index)
            line.type = cls._parse_line_type_for(lines, index)
            # Check if previous line is supposed to actually be just action (Characters need 1 empty line before and 1 NON-empty line after)
            if line.type == LineType.empty:
                if l-1 in range(len(lines)):
                    prev = lines[l-1]
                    if prev.type == LineType.character:
                        prev.type = LineType.action
            index += 1
        return lines

    @staticmethod
    def _get_unparsed_line_array_from_raw_string(text: str) -> list[Line]:

        unparsed_lines: list = []
        if (text == None): text = ""
        text = text.replace("\r\n", "\n") ## Replace MS Word/Windows line breaks with unix newlines
        
        raw_lines: list = text.splitlines()
        position: int = 0; ## To track at which position every line begins
        
        for r in raw_lines:
            unparsed_lines.append(Line(r, position, type=LineType.unparsed))
            position += (len(r) + 1) # +1 is to account for newline character

        return unparsed_lines

    ### Parses the line type for given line. It *has* to know its line index.
    @classmethod
    def _parse_line_type_for(cls, lines: list[Line], index: int) -> LineType:

        line = lines[index]

        nextLine: Line = None
        previousLine: Line = None
        
        if len(lines) > 0:
            if index > 0:
                previousLine: Line = lines[index - 1]
            if (
                (line != lines[-1])
                and (index+1 <= len(lines))
                ):
                nextLine: Line = lines[index+1]
        
        previousIsEmpty: bool  = True
        
        ## Check if there is a previous line
        ## If so, check if previous line is empty
        if previousLine is not None:
            if previousLine.type != LineType.empty:
                previousIsEmpty = False


        ## --------- Handle empty lines first
        empty_lines_result: LineType  = cls._check_if_empty_lines(line)
        if empty_lines_result is not None:
            return empty_lines_result
        

        ## --------- Check FORCED elements
        forced_element_result: LineType  = cls._check_if_forced_element(
            line=line, 
            previousIsEmpty=previousIsEmpty
            )
        if forced_element_result is not None:
            return forced_element_result


        ## --------- Title page
        title_page_result: LineType = cls._check_if_title_page_element(
            line=line, 
            previousLine=previousLine,
            index=index
            )
        if (title_page_result is not None):
            return title_page_result
            
        
        ## --------- Transitions
        transition_result: LineType  = cls._check_if_transition(
            line=line,
            previousIsEmpty=previousIsEmpty
            )
        if transition_result is not None:
            return transition_result
        
            # Handle items which require an empty line before them.
            
        ## --------- Heading
        heading_result: LineType  = cls._check_if_heading(
            line=line,
            previousIsEmpty=previousIsEmpty
            )
        if heading_result is not None:
            return heading_result
                

        ## --------- Check for Dual Dialogue
        dual_dialogue_result: LineType  = cls._check_if_dual_dialogue(
            line=line,
            previousLine=previousLine,
            nextLine=nextLine
            )
        if dual_dialogue_result is not None:
            return dual_dialogue_result

        ## --------- Character
        character_result: LineType  = cls._check_if_character(
            line=line,
            nextLine=nextLine,
            twoLinesOver=lines[index+2] if (index + 2 < len(lines)) else None,
            index=index,
            previousLine=previousLine
            )
        if character_result is not None:
            return character_result

        ## --------- Dialogue or Parenthetical
        dialogue_or_parenthetical_result: LineType  = cls._check_if_dialogue_or_parenthetical(
            line=line,
            previousLine=previousLine,
        )
        if dialogue_or_parenthetical_result is not None:
            return dialogue_or_parenthetical_result
            
        ## --------- Default
        return LineType.action
    
    # ---------- Parsing helper funcs ---------- 
    @staticmethod    
    def _only_uppercase_until_parenthesis(text: str): # Might want to move this func to helper_funcs to be cleaner
        until_parenthesis = text.split("(")[0]
        if (
            until_parenthesis == until_parenthesis.upper()
            and len(until_parenthesis) > 0
            ):
            return True
        return False
        
    # ---------- Parsing sub-functions ---------- 
    @staticmethod
    def _check_if_transition(line: Line, previousIsEmpty: bool):
        if (
            len(line.string) > 2 
            and line.string[-1] == ':' 
            and line.string == line.string.upper() 
            and previousIsEmpty
            ):
            return LineType.transitionLine
        
        return None
    
    @staticmethod    
    def _check_if_dialogue_or_parenthetical(line: Line, previousLine: Line):
        if line.string.startswith("  "):
            print("Non empty line here!")
        if previousLine is None:
            return None
        
        if (
            previousLine.isDialogue()
            and len(previousLine.string) > 0
            ):
            if (line.string[:1] == '(' ): 
                return LineType.parenthetical 
            return LineType.dialogue
        
        if previousLine.type == LineType.parenthetical:
            return LineType.dialogue
        
        if line.string.startswith("  "):
            return LineType.dialogue
        
    @staticmethod
    def _check_if_heading(line: Line, previousIsEmpty: bool):

        if not (previousIsEmpty
              and len(line.string)>= 3 
              ):
            return None
        
        firstChars: str = line.string[:3].lower()
        if not (firstChars == "int" or
            firstChars == "ext" or
            firstChars == "est" or
            firstChars == "i/e"):
            return None
            
        ## If it's just under 4 characters, return heading
        if (len(line.string) == 3):
            return LineType.heading
        
        ## To avoid words like "international" from becoming headings, the extension HAS to end with either dot, space or slash
        nextChar: str = line.string[3]
        if (nextChar == '.' 
            or nextChar == ' ' 
            or nextChar == '/'):

            return LineType.heading
       
    @staticmethod    
    def _check_if_forced_element(line: Line, previousIsEmpty: bool) -> LineType:
        
        firstChar: str = line.string[:1]
        lastChar: str = line.string[-1:]


        ## Also, lets add the first \ as an escape character
        if (firstChar == '\\'):
            line.escapeRanges.append(0)
        
        ## --------- Forced whitespace
        containsOnlyWhitespace: bool = True if ''.join(line.string.split()) == "" else False ## Save to use again later
        twoSpaces: bool = (
            firstChar == ' ' 
            and lastChar == ' ' 
            and len(line.string) > 1) ## Contains at least two spaces
        
        if containsOnlyWhitespace and not twoSpaces:
            return LineType.empty
        

        ## --------- Page Break
        if line.string.strip() == "===":
            return LineType.pageBreak
        ## --------- FORCED Action or Shot
        if (firstChar == '!'):
            ## Action or shot
            if (len(line.string) > 1):
                secondChar: str = line.string[1]
                if (secondChar == '!'):
                    return LineType.shot
            
            return LineType.action
        ## --------- FORCED Heading / Slugline
        if (firstChar == '.' 
              and previousIsEmpty
              ):
            
            ## '.' forces a heading.
            ## Because our American friends love to shoot their guns like we Finnish people love our booze,
            ## screenwriters might start dialogue blocks with such "words" as '.44'
            if (len(line.string) > 1):
                secondChar = line.string[1]
                if (secondChar != '.'):
                    return LineType.heading
            else:
                return LineType.heading
            
        
        ## Rest of the FORCED Line Types
        elif (firstChar == '@'): return LineType.character
        elif (firstChar == '>' and lastChar == '<'): return LineType.centered
        elif (firstChar == '>'): return LineType.transitionLine
        elif (firstChar == '~'): return LineType.lyrics
        elif (firstChar == '='): return LineType.synopse
        elif (firstChar == '#'): return LineType.section
        elif (firstChar == '@' and ord(lastChar) == 94 and previousIsEmpty): return LineType.dualDialogueCharacter
        elif (firstChar == '.' and previousIsEmpty): return LineType.heading

        else:
            return None
    
    @staticmethod
    def _check_if_title_page_element(line: Line, previousLine: Line, index: int) -> LineType:
        
        if (previousLine is not None):
            if not previousLine.isTitlePage():
                return None
        
        # After the above block, previousLine should always be a title page element or None
            
        key: str = line.getTitlePageKey()
    
        if (len(key) > 0 and key != ""):
            
            match key:
                case "title":
                    return LineType.titlePageTitle
                case "author":
                    return LineType.titlePageAuthor
                case "authors":
                    return LineType.titlePageAuthor
                case "credit": 
                    return LineType.titlePageCredit
                case "source": 
                    return LineType.titlePageSource
                case "contact": 
                    return LineType.titlePageContact
                case "contacts": 
                    return LineType.titlePageContact
                case "contact info": 
                    return LineType.titlePageContact
                case "draft date": 
                    return LineType.titlePageDraftDate
                case "draft":
                    return LineType.titlePageDraftDate
                case _: 
                    return LineType.titlePageUnknown
            
        if (previousLine is not None):
            prev_key: str = previousLine.getTitlePageKey()
            if (
                (len(prev_key) > 0)
                or line.string.startswith("\t") 
                or line.string.startswith(" "*3) 
                ):
                
                return previousLine.type

    @staticmethod
    def _check_if_character(line: Line, nextLine: Line, twoLinesOver: Line, index: int, previousLine: Line) -> LineType:
        
        if not (hf.only_uppercase_until_parenthesis(line.string) and line.string != ""):
            return None
        
        if line.string != line.string.strip():
            if line.string.startswith("  "):
                return None
        
        lastChar = line.string[-1:]
        ## A character line ending in ^ is a dual dialogue character
        ## (94 = ^, we'll compare the numerical value to avoid mistaking Tuskic alphabet character Ş as ^)
        #if list(line.noteRanges) != []:
            #if sorted(list(line.noteRanges))[0] != 0: # get first ordered numerical value in noteRanges? #NOTE: Not 100% sure what this condition is tbh
        if (ord(lastChar) == 94):
        
            ## Note the previous character cue that it's followed by dual dialogue
            # self.makeCharacterAwareOfItsDualSiblingFrom(index) #NOTE: Does the parser need to be responsible for this?
            return LineType.dualDialogueCharacter

        # Check if this line is actually just an ALLCAPS action line
        if previousLine is not None:
            if previousLine.type != LineType.empty:
                return LineType.action
        
        return LineType.character
        
    @staticmethod    
    def _check_if_empty_lines(line: Line) -> LineType:
        
        if (len(line.string) == 0):
            return LineType.empty
        else:
            return None
    
    @staticmethod          
    def _check_if_dual_dialogue(line: Line, previousLine: Line, nextLine: Line = None,) -> LineType: 
        if previousLine is not None:
            if (
                previousLine.isDualDialogue()
                ):
                
                if line.string[0] == "(":
                    return LineType.dualDialogueParenthetical
                else:
                    return LineType.dualDialogue
        
        else:
            return None

    # ---------- Deprecated / Unknown ---------- 

    def fix_parsing_mistakes(self, line: Line, previousLine: Line, index: int): # NOTE: Not sure if this is needed
        ## Fix some parsing mistakes
            if (previousLine.type == LineType.action and len(previousLine.string) > 0
                and previousLine.string.split('(')[0] == previousLine.string.split('(')[0].upper
                and len(line.string) > 0
                and not previousLine.is_forced() # be wary -- this is a FUNC not a property, needs the paretheses ()
                and self.previousLine(previousLine).type == LineType.empty):
                ## Make all-caps lines with < 2 characters character cues
                ## and/or make all-caps actions character cues when the text is changed to have some dialogue follow it.
                ## (94 = ^, we'll use the unichar numerical value to avoid mistaking Turkish alphabet letter 'Ş' as '^')
                if (previousLine.string[-1:] == 94): 
                    previousLine.type = LineType.dualDialogueCharacter # !!!!!! THIS FUCKIN LINE
                else:
                    previousLine.type = LineType.character
                
                self.changedIndices.add(index-1)
                
                if (len(line) > 0 
                    and line.string[0] == '('
                    ):
                    return LineType.parenthetical
                else: 
                    return LineType.dialogue
    def old_dual_dialogue_block(self, line: Line, previousLine: Line, nextLine: Line):
        # this block of code was running inside the check_if_dual_dialogue func... but it seems unnecessary now. keeping for reference
        if nextLine is not None:
                if (previousLine.isDialogue() or previousLine.isDualDialogue()):
                    
                    ## If preceeded by a character cue, always return dialogue
                    if (previousLine.type == LineType.character):
                        return LineType.dialogue
                    elif (previousLine.type == LineType.dualDialogueCharacter):
                        return LineType.dualDialogue
                
                    
                
                    ## If it's any other dialogue line and we're editing it, return dialogue
                    if (
                        (
                            previousLine.isAnyDialogue()
                            or previousLine.isAnyParenthetical()
                        ) 
                        and len(previousLine.string)> 0 
                        and (
                            len(nextLine.string) == 0 
                            or nextLine is None
                            ) 
                        ## and selection in rangeFromLocLen(line._range)
                        ):

                        if previousLine.isDialogue():
                            return LineType.dialogue
                        else:
                            return LineType.dualDialogue