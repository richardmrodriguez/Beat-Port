##
##  static_fountain_parser.py
##  Beat
##
##  Copyright © 2016 Hendrik Noeller. All rights reserved.
##  Parts copyright © 2019-2023 Lauri-Matti Parppei. All rights reserved.

##  parts copyright © 2024 Richard Mamaril Rodriguez. All rights reserved.

## This parser is based upon the ContinuousFountainParser from Lauri-Matti Parppei's Beat,
## which itself is based upon Writer by Hendrik Noeller.

## This has been ported / translated from Objective-C to Python.
## As a result, many omissions and structural changes are made,
## though the core parsing logic remains largely the same.

##  Relased under GPL


import uuid

from helper_dataclasses import LocationAndLength as loc_len
from helper_funcs import *

from line import Line, LineType
from parser_data_classes.formatting_characters import FormattingCharacters as fc

from document_model import DocumentModel as Document

class StaticFountainParser:
    title_page: list = []
    lines: list[Line] = []

    title_page_done_populating: bool = False # TODO use this to skip title page parsing when we are done with title page elements

    disabledTypes: list[any] = []

    def get_parsed_lines_from_raw_string(self, text: str) -> list[Line]:
        self.lines = []
        
        if (text == None): text = ""
        text = text.replace("\r\n", "\n") ## Replace MS Word/Windows line breaks with macOS ones # NOTE: Will this break text files on windows if we leave this?
        
        ## Split the text by line breaks
        raw_lines: list = text.splitlines()
        
        position: int = 0; ## To track at which position every line begins
        
        previousLine: Line = None
        
        for rawLine in raw_lines:
            index: int = len(self.lines)
            print("Index", index)
            beat_line: Line = Line(string=rawLine, position=position)
            self.lines.append(beat_line)
            
            beat_line.type = self.parseLineTypeFor(beat_line, index=index)
            
            ## Quick fix for mistaking an ALL CAPS action for a character cue # NOTE: Don't know what's wrong with this block rn
            
            '''if previousLine is not None:
                if (previousLine.type == LineType.character 
                    and
                    (
                        (len(beat_line.string) < 1) 
                        or (beat_line.type == LineType.empty)
                    )
                    ):
                    
                    
                    previousLine.type = self.parseLineTypeFor(beat_line, index=(index - 1))
                    
                    if (previousLine.type == LineType.character): 
                        previousLine.type = LineType.action'''
            
                    
            position += (len(rawLine) + 1); ## +1 for newline character # NOTE: since this code adds 1 for newlines, we should NOT use 'keepends' when using str.splitlines()
            previousLine = beat_line
        
        return self.lines
    
    
    
    ### Parses the line type for given line. It *has* to know its line index.
    
    def parseLineTypeFor(self, line: Line, index: int) -> LineType:
        previousLine: Line = self.lines[index - 1] if (
            index > 0) else None
        nextLine: Line = self.lines[index+1] if (
            (line != self.lines[-1]) 
            and (index+1 < len(self.lines))
            ) else None
        
        firstChar: str = line.string[:1]
        lastChar: str = line.string[-1:]
        
        previousIsEmpty: bool  = False
        
        trimmedString: str = line.string.strip() if (len(line.string) > 0) else ""
        
        ## Check if there is a previous line
        ## If so, check if previous line is empty
        if (
            previousLine is None 
            or index == 0 
            ):
            previousIsEmpty = True
        elif (previousLine is not None 
              and previousLine.type == LineType.empty):
            
            previousIsEmpty = True
        
        ## --------- Handle empty lines first
        empty_lines_result = self.check_if_empty_lines(
            previousLine=previousLine,
            nextLine=nextLine,
            line=line)
        if empty_lines_result != None:
            return empty_lines_result
        
        ## --------- Check FORCED elements
        forced_element_result = self.check_if_forced_element(
            line=line, 
            previousLine=previousLine)
        if forced_element_result is not None:
            return forced_element_result


        ## --------- Title page
        if (previousLine == None or previousLine.isTitlePage):
            titlePageType: LineType = self.parseTitlePageLineTypeFor(line=line, 
                                                                     previousLine=previousLine,
                                                                     index=index)
            if (titlePageType is not None):
                
                return titlePageType
            
        
        ## --------- Transitions
        if (
            len(line.string) > 2 
            and line.string[-1] == ':' 
            and line.string == line.string.upper() 
            and previousIsEmpty
            ):
            return LineType.transitionLine
        
        
        ## Handle items which require an empty line before them (and we're not forcing character input)
        
            
        ## --------- Heading
        heading_result = self.check_if_heading(
            line=line,
            previousIsEmpty=previousIsEmpty)
        if heading_result is not None:
            return heading_result
                
             
        ## --------- Character
        character_result = self.check_if_character(
            line=line,
            nextLine=nextLine, 
            index=index
            )
        if character_result is not None:
            return character_result

        ## --------- Dialogue or Parenthetical
        dialogue_or_parenthetical_result = self.check_if_dialogue_or_parenthetical(
            line=line,
            previousLine=previousLine,
            index=index
        )
        if dialogue_or_parenthetical_result is not None:
            return dialogue_or_parenthetical_result
            
        ## --------- Default
        return LineType.action
    
    
        
    # ---------- Parsing helper funcs ---------- 
        
    def only_uppercase_until_parenthesis(self, text: str): # Might want to move this func to helper_funcs to be cleaner
        until_parenthesis = text.split("(")[0]
        if (
            until_parenthesis == until_parenthesis.upper()
            and len(until_parenthesis) > 0
            
            ):
            return True
        else:
            return False
        
    # ---------- Parsing sub-functions ---------- 
        
    def check_if_dialogue_or_parenthetical(self, line: Line, previousLine: Line, index: int):
        if previousLine is not None:
            firstChar: str = line.string[:1]
            if (
                (
                    previousLine.isDialogue
                    or previousLine.isDualDialogue
                ) 
                 and len(previousLine.string) > 0):
                if (firstChar == '(' ): 
                    return LineType.parenthetical if (previousLine.isDialogue) else LineType.dualDialogueParenthetical
                return LineType.dialogue if (previousLine.isDialogue)  else LineType.dualDialogue
            
            
            ## Fix some parsing mistakes
            if (previousLine.type == LineType.action and len(previousLine.string) > 0
                and previousLine.string.split('(')[0] == previousLine.string.split('(')[0].upper
                and len(line.string) > 0
                and not previousLine.forced
                and self.previousLine(previousLine).type == LineType.empty):
                ## Make all-caps lines with < 2 characters character cues
                ## and/or make all-caps actions character cues when the text is changed to have some dialogue follow it.
                ## (94 = ^, we'll use the unichar numerical value to avoid mistaking Turkish alphabet letter 'Ş' as '^')
                if (previousLine.string[-1] == 94): previousLine.type = LineType.dualDialogueCharacter
                else: previousLine.type = LineType.character
                
                self.changedIndices.add(index-1)
                
                if (len(line) > 0 
                    and line.string[0] == '('
                    ):
                    return LineType.parenthetical
                else: 
                    return LineType.dialogue
        else:
            return None
    
    def check_if_heading(self, line: Line, previousIsEmpty: bool):

        if (previousIsEmpty
              and len(line.string)>= 3 
              ):
            firstChars: str = line.string[:3].lower()
            if (firstChars == "int" or
                firstChars == "ext" or
                firstChars == "est" or
                firstChars == "i/e"):
                
                ## If it's just under 4 characters, return heading
                if (len(line.string) == 3):
                    return LineType.heading
                else:
                    ## To avoid words like "international" from becoming headings, the extension HAS to end with either dot, space or slash
                    nextChar: str = line.string[3]
                    if (nextChar == '.' 
                        or nextChar == ' ' 
                        or nextChar == '/'):

                        return LineType.heading
        else:
            return None
        
    def check_if_forced_element(self, line: Line, previousLine: Line) -> LineType:
        
        firstChar: str = line.string[:1]
        lastChar: str = line.string[-1:]

        previousIsEmpty: bool = False

        if previousLine is not None:
            if previousLine.type == LineType.empty:
                previousIsEmpty == True

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
        
    def parseTitlePageLineTypeFor(self, line: Line, previousLine: Line, index: int) -> LineType:
        key: str = line.getTitlePageKey()
        
        
        if (len(key) > 0 and key != ""):
            value: str = line.getTitlePageValue()
            if (value == None):
                value = ""
            
            ## Store title page data
            titlePageData: dict = { key: [value] }
            self.title_page.append(titlePageData) # NOTE: instead of holding the lines / title page elements / etc. in the parser instance, they should be stored in a Document Model instance
            
            ## Set this key as open (in case there are additional title page lines)
            # self.openTitlePageKey = key # NOTE Don't know what this does yet
            
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


                    
        elif (
            previousLine is not None 
            and len(self.title_page)> 0
            ):
            if (previousLine.isTitlePage):
                
                key: str = ""
                i: int = index -1
                #old while loop ... not sure how it is different, am afraid to delete it until i understand it
                '''while (i >= 0):
                    pl: line = self.lines[i]
                    if (len(pl.getTitlePageKey()) > 0):
                        key = pl.getTitlePageKey()
                        break
                    
                    i -= 1'''

                
                
                key = previousLine.getTitlePageKey()

                
                print(str(previousLine.type).split("LineType."))
                if (len(key) > 0 ):
                    _dict = self.title_page[-1]
                    if key in _dict.keys():
                        _dict[key].append(line.string)
                        return previousLine.type
                        
                elif line.string.startswith("\t") or line.string.startswith("   "):
                    return previousLine.type
                
                    
                    
        else:   
            return None
    
    def check_if_character(self, 
                           line, 
                           nextLine, 
                           index,) -> LineType:
        
        lastChar = line.string[-1:]
        if (
            self.only_uppercase_until_parenthesis(line.string)
            and (not ''.join(line.string.split()) == "")
            ):

            
            ## A character line ending in ^ is a dual dialogue character
            ## (94 = ^, we'll compare the numerical value to avoid mistaking Tuskic alphabet character Ş as ^)
            if list(line.noteRanges) != []:
                if sorted(list(line.noteRanges))[0] != 0: # get first ordered numerical value in noteRanges? #NOTE: Not 100% sure what this condition is tbh
                    if (ord(lastChar) == 94):
                    
                        ## Note the previous character cue that it's followed by dual dialogue
                        # self.makeCharacterAwareOfItsDualSiblingFrom(index)
                        return LineType.dualDialogueCharacter
                    else:
                        ## It is possible that this IS NOT A CHARACTER but an all-caps action line
                        if (index + 2 < len(self.lines)):
                            twoLinesOver: Line = self.lines[index+2]
                            
                            ## Next line is empty, line after that isn't - and we're not on that particular line
                            if ((len(nextLine.string) == 0 and len(twoLinesOver.string) > 0)):
                                return LineType.action
                        
                        
                       
            return LineType.character
        else:
            return None
        
    def check_if_empty_lines(self, previousLine, nextLine, line,) -> LineType:
        if (len(line.string) == 0):
            if previousLine is not None: # added this line, to make funny errors go away, not sure if this is best approach
                ## If preceding line is formatted as dialogue BUT it's empty, we'll just return empty.
                if (len(previousLine.string) == 0):
                    return LineType.empty
                
            # if self.check_if_dual_dialogue() is not None: # NOTE disabling this check for now, might put somewhere else
            #     return self.check_if_dual_dialogue()
            
            return LineType.empty
        else:
            return None
              
    def check_if_dual_dialogue(self, previousLine: Line = None, nextLine: Line = None) -> LineType:
        if previousLine is not None and nextLine is not None:
            if (previousLine.isDialogue or previousLine.isDualDialogue):
                
                
                ## If preceeded by a character cue, always return dialogue
                if (previousLine.type == LineType.character):
                    return LineType.dialogue
                elif (previousLine.type == LineType.dualDialogueCharacter):
                    return LineType.dualDialogue
            
                # selection: int = self.delegate.selectedRange.location if (True) else 0 # syntax hurty self.delegate ???
            
                ## If it's any other dialogue line and we're editing it, return dialogue
                if (
                    (
                        previousLine.isAnyDialogue 
                        or previousLine.isAnyParenthetical
                    ) 
                    and len(previousLine.string)> 0 
                    #and (
                    #    len(nextLine.string) == 0 
                    #    or nextLine is None
                    #    ) 
                    ## and selection in rangeFromLocLen(line._range)
                    ):

                    return LineType.dialogue if (previousLine.isDialogue) else LineType.dualDialogue
        else:
            return None