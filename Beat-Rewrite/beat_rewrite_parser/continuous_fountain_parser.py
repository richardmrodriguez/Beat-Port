##
##  ContinousFountainParser.m
##  Beat
##
##  Copyright © 2016 Hendrik Noeller. All rights reserved.
##  Parts copyright © 2019-2023 Lauri-Matti Parppei. All rights reserved.

##  Relased under GPL
 
'''This code was originally based on Hendrik Noeller's work.
It is heavily modified for Beat, and not a lot of Hendrik's original code remains.

Parsing happens SEPARATELY from the text view. Once something is changed in the text view,
we send the changed range here. On iOS, you have to use text storage delegate, and on macOS,
you can do that in shouldChangeText: - note that those happen at a different stage of editing.

This means that the text view and parser CAN GO OUT OF SYNC. Be EXTREMELY careful with this.
I've messed it up now and then. My dream would be creating a Beat text container protocol which
could then be used on NSTextContainer, or just on normal NSAttributedString. The text container
would register its own changes and provide lines to the parser, eliminating the chance of ever
going out of sync with the editor.

For now, the current system isn't broken so why fix it.

This is a sprawling, 3800-line class, but I've tried explaining and dividing it with markers.
A lot of stuff could/should be moved to the line class, I guess, but that's starting to look
just as bad, he he.

Dread lightly, dear friend.'''


import uuid

from helper_dataclasses import LocationAndLength as loc_len
from helper_funcs import *

from line import Line, LineType
from parser_data_classes.formatting_characters import FormattingCharacters as fc
# from outline_scene import OutlineScene
# from outline_changes import OutlineChanges

# import <BeatParsing/BeatParsing-Swift.h> # ? doesn't exist in the repoo currently
# import "ContinuousFountainParser+Preprocessing.h" # another circular import? or do I just not understand categories in Objective-C?

#pragma mark - Parser

class ContinuousFountainParser:
        
    NEW_OUTLINE: bool = True
    changeInOutline: bool
    outlineChanges: any # OutlineChanges
    changedOutlineElements: list

    ### The line which was last edited. We're storing this when asking for a line at caret position.
    lastEditedLine: Line
    ### An index for the last fetched line result when asking for lines in range
    lastLineIndex: int
    ### The range which was edited most recently.
    editedRange: loc_len

    ## Title page parsing
    openTitlePageKey: str
    previousTitlePageKey: str

    ## Static parser flag
    nonContinuous: bool

    ## Cached line set for UUID creation
    cachedLines: set # syntax hurty: MUTABLE SETS and UUID

    # macros: BeatMacroParser
    titlePage: list
    ##
    prevLineAtLocation: Line

    # pragma mark - Initializers
    def __init__(self, string:str = "", delegate: any = None):
   
        self.lines = []
        self.outline = []
        self.changedIndices = set()
        self.titlePage = []
        self.storylines = []
        
        self.delegate = delegate
        # self.nonContinuous = nonContinuous
        # self.staticDocumentSettings = settings
        
        ## Inform that this parser is STATIC and not continuous (wtf, why is this done using dual values?)
        '''if (self.nonContinuous):
            self.staticParser = True
        else:
            self.staticParser = False'''
        
        self.parseText(string)
        # [self updateMacros]

    ### Extracts the title page from given string
    def titlePageForString(self, string: str) -> list:
        rawLines: list[str] = string.splitlines()
        
        if rawLines.count == 0: 
             return []
        elif ":" not in rawLines[0]:
             return []
        
        text = ""
        
        for l in rawLines:
            ## Break at empty line
            text += l + "\n"
            if l == "":
                break
        
        text += "\n"
        
        # parser = ContinuousFountainParser(string)
        # parser.updateMacros() ## Resolve macros
        # return parser.titlePage # what does returning this title page do?
        return self.titlePage
    


    #pragma mark - Document setting getter  ---- BACKBURNER

    ### Returns either document settings OR static document settings. Note that if static document settings are provided, they are preferred.
    ### TODO: Perhaps the parser should hold the document settings and read them when originally parsing the document? This would be much more sensible.
    '''def BeatDocumentSettings*)documentSettings
    {
        if (self.staticDocumentSettings != None) return self.staticDocumentSettings
        else return self.delegate.documentSettings
    }'''

    #pragma mark - Saved file processing

    ### Returns the RAW text  when saving a screenplay. Automatically fixes some stylistical issues.
    def screenplayForSaving(self) -> str:
        lines: list = self.lines
        content = ""
        
        previousLine: Line
        for line in lines: 
            if (line is None): continue # ? What is this line of code supposed to do?
            
            string: str = line.string
            type: LineType = line.type
        
            ## Make some lines uppercase
            if ((type == LineType.heading or type == LineType.transitionLine) and
                line.numberOfPrecedingFormattingCharacters == 0):
                 string = string.upper
            
            ## Ensure correct whitespace before elements
            if ((line.isAnyCharacter or line.type == LineType.heading) and
                previousLine.string.length > 0):
                content += "\n"
                
            ## Append to full content
            content += string
            
            ## Add a line break until we reach the end
            if (line != self.lines[-1]):
                content += "\n"
            
            previousLine = line
        
        
        return content
    

    ### Returns the whole document as single string
    def rawText(self) -> str:
        string: str = ""

        for line in self.lines:
            if (line != self.lines[-1]):
                string += (line.string + "\n")
            else:
                string += line.string
            
        return string
    


    #pragma mark - Parsing

    #pragma mark Bulk parsing

    
        
        
        ## Reset outline
        # self.changeInOutline = True
        # self.updateOutline()
        # self.outlineChanges = OutlineChanges() # ? What or where is OutlineChanges? Is it a struct or a class?
        
        ## Reset changes (to force the editor to reformat each line)

        # self.changedIndices.update(range(len(self.lines))) 
        
        ## Set identifiers (if applicable)
        # self.setIdentifiersForOutlineElements(self.documentSettings.get(DocSettingHeadingUUIDs)) # syntax hurty
    

    ## This sets EVERY INDICE as changed.
    def resetParsing(self):
        index: int = 0
        while (index < self.lines.count):
            self.changedIndices.addIndex(index) # ? What does this func do exactly?
            index += 1
        
    


    # HOT RELOAD
    #pragma mark - Continuous Parsing ---- BACKBURNER

    '''
    
    Note to future me:
    
    I have revised the original parsing system, which parsed changes by
    always removing single characters in a loop, even with longer text blocks.
    
    I optimized the logic so that if the change includes full lines (either removed or added)
    they are removed or added as whole, rather than character-by-character. This is why
    there are two different methods for parsing the changes, and the other one is still used
    for parsing single-character edits. parseAddition/parseRemovalAt methods fall back to
    them when needed.
    
    Flow:
    parseChangeInRange ->
    parseAddition/parseRemoval methods write changedIndices
    -> correctParsesInLines processes changedIndices
    
    '''

    '''def parseChangeInRange(self, _range: loc_len, withString=""): # NOTE: param name "range" shadowed the range type in python, changed it to _range
    
        if (_range.location == None):
            return ## This is for avoiding crashes when plugin developers are doing weird things
        
        _lastEditedLine = None
        _editedRange = _range
        
        # syntax hurty
        # NOTE: this method has to be run single-threaded to avoid race conditions
        # need to implement python threading here
        @synchronized (self.lines) {
            NSMutableIndexSet *changedIndices = NSMutableIndexSet.new # so... list time?
            if (_range.length == 0): ## Addition
                [changedIndices addIndexes:[self.parseAddition:string atPosition:_range.location]] # syntax hurty : RANGE position needs to be calc'd
                
             elif (string.length == 0):  ## Removal
                [changedIndices addIndexes:[self.parseRemovalAt:_range]]
                
             else:  ##Replacement
                [changedIndices addIndexes:[self.parseRemovalAt:_range]]; ## First remove
                [changedIndices addIndexes:[self.parseAddition:string atPosition:_range.location]]; ## Then add # syntax hurty : RANGE position needs to be calc'd
            
            
            self.correctParsesInLines(changedIndices)
        }
    

    
    ### Ensures that the given line is parsed correctly. Continuous parsing only. A bit confusing to use.
    def ensureDialogueParsingFor(self, line: Line):
        if (not line.isAnyCharacter): return
        
        i = self.indexOfLine(line)
        if i is None: return
        
        lines: list = self.lines
        
        nextLine: Line
        
        ## Get the neighboring lines
        if (i < len(self.lines) - 1):
            nextLine = lines[i + 1]
        
        ## Let's not do anything, if we are currently editing these lines.
        if (nextLine != None and nextLine.string.length == 0 and # syntax hurty: RANGE
            not NSLocationInRange(self.selectedRange.location, line._range) and 
            not NSLocationInRange(self.selectedRange.location, nextLine._range) and
            line.numberOfPrecedingFormattingCharacters == 0
            ):
            
            line.type = LineType.action
            self.changedIndices(addIndex=i)
            # [_delegate applyFormatChanges] # syntax hurty : what the FUCK is a delegate
            self.applyFormatChanges'''
        

    # HOT RELOAD
    #pragma mark Parsing additions  ---- BACKBURNER

    '''def NSIndexSet*)parseAddition:(NSString*)string atPosition:(NSUInteger)position
    {
        NSMutableIndexSet *changedIndices = NSMutableIndexSet.new
        
        ## Get the line where into which we are adding characters
        NSUInteger lineIndex = [self lineIndexAtPosition:position]
        Line* line = self.lines[lineIndex]
        
        [changedIndices addIndex:lineIndex]
        
        NSUInteger indexInLine = position - line.position
        
        ## Cut the string in half
        NSString* tail = [line.string substringFromIndex:indexInLine]
        line.string = [line.string substringToIndex:indexInLine]
        
        NSInteger currentRange = -1
        
        for (NSInteger i=0; i<string.length; i += 1) {
            if (currentRange < 0) currentRange = i
            
            unichar chr = [string characterAtIndex:i]
            
            if (chr == '\n') {
                NSString* addedString = [string substringWithRange:loc_len(currentRange, i - currentRange)]
                line.string = [line.string stringByAppendingString:addedString]
                
                if (lineIndex < self.lines.count - 1) {
                    Line* nextLine = self.lines[lineIndex+1]
                    NSInteger delta = ABS(NSMaxRange(line.range) - nextLine.position)
                    [self decrementLinePositionsFromIndex:lineIndex+1 amount:delta]
                }
                
                [self addLineWithString:@"" atPosition:NSMaxRange(line.range) lineIndex:lineIndex+1]
                
                ## Increment current line index and reset inspected range
                lineIndex += 1
                currentRange = -1
                
                ## Set current line
                line = self.lines[lineIndex]
            }
        }
        
        ## Get the remaining string (if applicable)
        NSString* remainder = (currentRange >= 0) ? [string substringFromIndex:currentRange] : @""
        line.string = [line.string stringByAppendingString:remainder]
        line.string = [line.string stringByAppendingString:tail]
        
        [self adjustLinePositionsFrom:lineIndex]
        
        ## [self report]
        [changedIndices addIndexesInRange:loc_len(changedIndices.firstIndex + 1, lineIndex - changedIndices.firstIndex)]
        
        return changedIndices
    }'''

    # HOT RELOAD
    #pragma mark Parsing removals ---- BACKBURNER

    '''def NSIndexSet*)parseRemovalAt:(NSRange)range {
        NSMutableIndexSet *changedIndices = NSMutableIndexSet.new
        
        ## Note: First and last index can be the same, if we are parsing on the same line
        NSInteger firstIndex = [self lineIndexAtPosition:range.location]
        NSInteger lastIndex = [self lineIndexAtPosition:NSMaxRange(range)]
        
        Line* firstLine = self.lines[firstIndex]
        Line* lastLine = self.lines[lastIndex]
        
        bool originalLineWasEmpty = (firstLine.string.length == 0)
        bool lastLineWasEmpty = (lastLine.string.length == 0)
        
        bool omitOut = false
        bool omitIn = false
        
        NSInteger i = firstIndex
        while (i < self.lines.count) {
            Line* line = self.lines[i]
            
            ## Store a flag if last handled line previously terminated an omission
            omitOut = line.omitOut
            omitIn = line.omitIn
            
            NSRange intersection = NSIntersectionRange(line.range, range)
            NSRange localRange = loc_len(intersection.location - line.position, intersection.length)
            
            if (range.length <= 0) {
                break
            }
            elif (intersection.length == line.range.length) {
                ## The range covers this whole line, remove it altogether.
                [self removeLineAtIndex:i]
                range.length -= line.range.length; ## Subtract from full range
            }
            else {
                ## This line is partly covered by the range
                line.string = [line.string stringByRemovingRange:localRange]
                [self decrementLinePositionsFromIndex:i+1 amount:localRange.length]
                range.length -= localRange.length; ## Subtract from full range
                
                ## Move on to next line (even if we only wanted to remove one character)
                i += 1
            }
        }
        
        ## Join the two lines if the original line didn't get removed in the process
        if (firstIndex != lastIndex and firstLine == self.lines[firstIndex] and
            self.lines.count > firstIndex + 1 and self.lines[firstIndex+1] == lastLine) {
            firstLine.string = [firstLine.string stringByAppendingString:lastLine.string]
            [self removeLineAtIndex:firstIndex+1]
            
            NSInteger diff = NSMaxRange(firstLine.range) - lastLine.position
            [self incrementLinePositionsFromIndex:firstIndex+1 amount:diff]
        }
        
        ## [self report]
        
        ## Add necessary indices
        [changedIndices addIndex:firstIndex]
        
        ## If the line terminated or bleeded out an omit, check surrounding indices, too.
        ## Also removing a line break can cause some elements change their type.
        if ((omitOut or lastLineWasEmpty) and firstIndex < self.lines.count+1) [changedIndices addIndex:firstIndex+1]
        if ((omitIn or originalLineWasEmpty) and firstIndex > 0) [changedIndices addIndex:firstIndex-1]
        
        ## Make sure we have at least one line left after the operation
        if (self.lines.count == 0) {
            Line* newLine = [Line withString:@"" type:empty]
            newLine.position = 0
            [self.lines addObject:newLine]
        }
        
        return changedIndices
    }'''

    # EDITING / HOT RELOAD
    #pragma mark Add / remove lines ---- BACKBURNER

    ### Removes a line from the parsed content and decrements positions of other lines
    '''def removeLineAtIndex(self, index: int):
        if (index < 0 or index >= self.lines.count): return
        
        line: Line = self.lines[index]
        
        if (line.isOutlineElement): 
            self.removeOutlineElementForLine(line)
        
        self.addUpdateToOutlineIfNeededAt(index)
        
        self.lines.removeObjectAtIndex:(index)
        self.decrementLinePositionsFromIndex(index, amount=(line.range.length)) # syntax hurty : oh god oh fuck how do obj c ranges work AAAAA
        
        ## Reset cached line
        _lastEditedLine = None
        if (line == _prevLineAtLocation): 
            _prevLineAtLocation = None'''
    
    # EDITING / HOT RELOAD
    ### Adds a new line into the parsed content and increments positions of other lines
    '''def addLineWithString(self, string: str, position: int, index: int):
        newLine: Line = [Line.alloc initWithString(string=string, position=position, parser=self)]
        
        self.lines.insert(index, newLine)
        self.incrementLinePositionsFromIndex(index+1, amount=1) # syntax hurty: investigate this, this might be wrong now
        
        ## Reset cached line
        _lastEditedLine = None'''
    

    # EDITING / HOT RELOAD
    #pragma mark - Correcting parsed content for existing lines  -= 1- BACKBURNER

    ### Intermediate method for `corretParsesInLines` which first finds the indices for line objects and then passes the index set to the main method.
    '''def correctParsesForLines(self, lines: list):
        indices: list = []
        
        for i in range(0, len(lines)): 
            indices.append(i)
        
        self.correctParsesInLines(indices)
    

    ### Corrects parsing in given line indices
    def correctParsesInLines(self, lineIndices: list):
        for n in range(0, len(lineIndices)):
            self.correctParseInLine(0, indicesToDo=lineIndices)
        
    

    ### Corrects parsing in a single line. Once done, it will be removed from `indices`, but note that new indices might be added in the process.
    def correctParseInLine(self, index: int, indices: list):
        ## Do nothing if we went out of range.
        ## Note: for code convenience and clarity, some methods can ask to reformat lineIndex-2 etc.,
        ## so this check is needed.

        if (index < 0) or (index == None) or (index >= len(self.lines)):
            indices.pop(index)
            return
        
        
        ## Check if this is the last line to be parsed
        lastToParse: bool = (indices.count == 0)
        
        currentLine: Line = self.lines[index]
        
        ## Remove index as done from array if in array
        if (indices.count): 
            lowestToDo: int = indices.lowestIndex
            if (lowestToDo == index) {
                [indices removeIndex:index]
            }
        
        
        ## Save the original line type
        oldType: LineType = currentLine.type
        oldOmitOut: bool = currentLine.omitOut
        
        oldMarker: range = currentLine.markerRange
        NSIndexSet* oldNotes = currentLine.noteRanges.copy
        
        ## Parse correct type
        self.parseTypeAndFormattingForLine(currentLine, atIndex=index)
        
        ## Add, remove or update outline elements
        if ((oldType == section or oldType == heading) and not currentLine.isOutlineElement) {
            ## This line is no longer an outline element
            [self removeOutlineElementForLine:currentLine]
        } elif (currentLine.isOutlineElement and not (oldType == section or oldType == heading)) {
            ## This line became outline element
            [self addOutlineElement:currentLine]
        } else {
            ## In other case, let's see if we should update the scene
            if ((currentLine.isOutlineElement and (oldType == section or oldType == heading)) or
                (oldNotes != None and not [oldNotes isEqualToIndexSet:currentLine.noteRanges]) or
                not (NSEqualRanges(oldMarker, currentLine.markerRange)) or
                currentLine.noteRanges.count > 0 or
                currentLine.type == synopse or
                currentLine.markerRange.length or
                currentLine.isOutlineElement or
                (oldType == synopse and currentLine.type != synopse)
                ) {
                ## For any changes to outline elements, we also need to add update the preceding line
                bool didChangeType = (currentLine.type != oldType)
                [self addUpdateToOutlineAtLine:currentLine didChangeType:didChangeType]
            }
            
            ## Update all macros
            if (currentLine.macroRanges.count > 0) [self updateMacros]
        }
        
        ## Mark the current index as changed
        [self.changedIndices addIndex:index]
        
        if (index > 0) {
            ## Parse faulty and orphaned dialogue (this can happen, because... well, there are *reasons*)
            
            Line *prevLine = self.lines[index - 1]; ## Get previous line
            NSInteger selection = (NSThread.isMainThread) ? self.delegate.selectedRange.location : 0; ## Get selection
            
            ## If previous line is NOT EMPTY, has content and the selection is not at the preceding position, go through preceding lines
            if (prevLine.type != empty and prevLine.length == 0 and selection != prevLine.position - 1) {
                NSInteger i = index - 1
                
                while (i >= 0) {
                    Line *l = self.lines[i]
                    if (l.length > 0) {
                        ## Not a forced character cue, not the preceding line to selection
                        if (l.type == character and selection != NSMaxRange(l.textRange) and l.numberOfPrecedingFormattingCharacters == 0  and
                            l != self.delegate.characterInputForLine) {
                            l.type = action
                            [self.changedIndices addIndex:i]
                        }
                        break
                    }
                    elif (l.type != empty and l.length == 0) {
                        l.type = empty
                        [self.changedIndices addIndex:i]
                    }
                    
                    i -= 1
                }
            }
        }
        
        ##If there is a next element, check if it might need a reparse because of a change in type or omit out
        if (oldType != currentLine.type or oldOmitOut != currentLine.omitOut or lastToParse or
            currentLine.isDialogueElement or currentLine.isDualDialogueElement or currentLine.type == empty) {
            
            if (index < self.lines.count - 1) {
                Line* nextLine = self.lines[index+1]
                if (currentLine.isTitlePage or					## if line is a title page, parse next line too
                    currentLine.type == section or
                    currentLine.type == synopse or
                    currentLine.type == character or        					    ##if the line became anything to
                    currentLine.type == parenthetical or        					##do with dialogue, it might cause
                    (currentLine.type == dialogue and nextLine.type != empty) or     ##the next lines to be dialogue
                    currentLine.type == dualDialogueCharacter or
                    currentLine.type == dualDialogueParenthetical or
                    currentLine.type == dualDialogue or
                    currentLine.type == empty or                ##If the line became empty, it might
                    ##enable the next on to be a heading
                    ##or character
                    
                    nextLine.type == titlePageTitle or          ##if the next line is a title page,
                    nextLine.type == titlePageCredit or         ##it might not be anymore
                    nextLine.type == titlePageAuthor or
                    nextLine.type == titlePageDraftDate or
                    nextLine.type == titlePageContact or
                    nextLine.type == titlePageSource or
                    nextLine.type == titlePageUnknown or
                    nextLine.type == section or
                    nextLine.type == synopse or
                    nextLine.type == heading or                 ##If the next line is a heading or
                    nextLine.type == character or               ##character or anything dialogue
                    nextLine.type == dualDialogueCharacter or   ##related, it might not be anymore
                    nextLine.type == parenthetical or
                    nextLine.type == dialogue or
                    nextLine.type == dualDialogueParenthetical or
                    nextLine.type == dualDialogue or
                    
                    ## Look for unterminated omits & notes
                    nextLine.omitIn != currentLine.omitOut or
                    ((currentLine.isDialogueElement or currentLine.isDualDialogueElement) and nextLine.string.length > 0)
                    ) {
                    [self correctParseInLine:index+1 indicesToDo:indices]
                }
            }
        }'''


    # EDITING
    #pragma mark - Incrementing / decrementing line positions  -= 1- BACKBURNER
    
    ### A replacement for the old, clunky `incrementLinePositions` and `decrementLinePositions`. Automatically adjusts line positions based on line content.
    ### You still have to make sure that you are parsing correct stuff, though.
    '''def adjustLinePositionsFromm(self, index: int):
        line: Line = self.lines[index]
        delta: int = NSMaxRange(line.range) # syntax hurty : what is this max range you speak of
        index += 1
        while index < self.lines.count:  # was a for loop, changed to a while loop
            l: Line = self.lines[index]
            l.position = delta
            delta = NSMaxRange(l.range)
            index += 1
        
    

    def incrementLinePositionsFromIndex(self, index: int, amount: int):
        while index < len(self.lines):
            line: Line = self.lines[index]
            
            line.position += amount
            index += 1
        
    

    def decrementLinePositionsFromIndex(self, index: int, amount: int):
        while index < len(self.lines):
            line: Line = self.lines[index]
            line.position -= amount # syntax hurty : is this a NSRange position, or the line's position in the array?
            index += 1'''
        
    # ??? Don't know what these do
    #pragma mark - Macros  -= 1- BACKBURNER

    '''def updateMacros(self):
        parser: BeatMacroParser = BeatMacroParser()
        lines: list = self.safeLines
        
        for i in range(len(lines)):
            l: Line = lines[i]
            if (len(l.macroRanges) == 0):
                continue
            
            self.resolveMacrosOn(l, parser)
            if (l.isOutlineElement or l.type == synopse) {
                self.addUpdateToOutlineAtLine(l didChangeType=false)
            }
        
    

    def resolveMacrosOn(line, parser=macroParser):
    
        macros: dict = line.macros
        
        line.resolvedMacros = {}
        
        keys: list[any] = [macros.keys() sortedArrayUsingComparator:^NSComparisonResult(NSValue*  _Nonnull obj1, NSValue*  _Nonnull obj2) { ### syntax hurty
            if (obj1.rangeValue.location > obj2.rangeValue.location):
                return true
            return false
        }]
        
        for _range in keys:
            macro: str = macros[_range]
            value = macroParser.parseMacro(macro)
            
            if (value != None):
                line.resolvedMacros[_range] = "%" + value # NOTE: Look up other formatted strings with percent % signs, they probably need to be added back
        '''
    


    #pragma mark - Parsing Core

    ### Parses line type and formatting ranges for current line. This method also takes care of handling possible disabled types.
    ### @note Type and formatting are parsed by iterating through character arrays. Using regexes would be much easier, but also about 10 times more costly in CPU time.
    

    # BEEEG function
    
    def parseTypeAndFormattingForLine(self, line: Line, index: int):
        oldType: LineType = line.type
        line.escapeRanges = set()
        line.type = self.parseLineTypeFor(line, index=index)
        
        ## Make sure we didn't receive a disabled type
        if self.disabledTypes != []:
            if line.type in self.disabledTypes:
                if (len(line.string) > 0): 
                    line.type = LineType.action
                else: line.type = LineType.empty
        
        
        length: int = len(line.string)
        charArray: str 
        charArray = line.string
        
        ## Parse notes
        # self.parseNotesFor(line, at=index, oldType=oldType)
        
        ## Omits have stars in them, which can be mistaken for formatting characters.
        ## We store the omit asterisks into the "excluded" index set to avoid this mixup.
        excluded: list = []
        
        ## First, we handle notes and omits, which can bleed over multiple lines.
        ## The cryptically named omitOut and noteOut mean that the line bleeds omit/note out on the next line,
        ## while omitIn and noteIn tell that are a part of another omitted/note block.
        
        previousLine: Line
        if (index <= len(self.lines)) and (index > 0):
            previousLine: Line = self.lines[index-1]
        else:
            previousLine = None
        
        '''line.omittedRanges = self.rangesOfOmitChars(charArray,
                                                    length=         length,
                                                    line=           line,
                                                    lastLineOut=    previousLine.omitOut,
                                                    stars=          excluded)
        
        line.boldRanges = self.rangesInChars(charArray,
                                            length=                 length,
                                            startString=            fc.BOLD_CHAR,
                                            endString=              fc.BOLD_CHAR,
                                            delimLength=            fc.BOLD_PATTERN_LENGTH,
                                            excludes=               excluded,
                                            line=                   line)
        
        line.italicRanges = self.rangesInChars(charArray,
                                               length=              length,
                                               startString=         fc.ITALIC_CHAR,
                                               endString=           fc.ITALIC_CHAR,
                                               delimLength=         fc.ITALIC_PATTERN_LENGTH,
                                               excludes=            excluded,
                                               line=                line)
        
        line.underlinedRanges = self.rangesInChars(charArray,
                                                   length=          length,
                                                   startString=     fc.UNDERLINE_CHAR,
                                                   endString=       fc.UNDERLINE_CHAR,
                                                   delimLength=     fc.UNDERLINE_PATTERN_LENGTH,
                                                   excludes=        None,
                                                   line=            line)'''

        '''line.macroRanges = self.rangesInChars=charArray # syntax hurty: MACROS
                                    ofLength=length
                                    between=MACRO_OPEN_CHAR
                                        and=MACRO_CLOSE_CHAR
                                    withLength=2
                            excludingIndices=None
                                        line=line]'''
        
        ## Intersecting indices between bold & italic are boldItalic
        '''if len(line.boldRanges) and len(line.italicRanges):
            line.boldItalicRanges = line.italicRanges.indexesIntersectingIndexSet(line.boldRanges) # syntax hurty: INTERSECTING INDEXES
        else:
            line.boldItalicRanges = set()
        
        if (line.type == LineType.heading):
            line.sceneNumberRange = self.sceneNumberForChars(charArray, length)
            
            if (line.sceneNumberRange.length == 0): #syntax hurty: RANGE
                line.sceneNumber = ""
            else:
                line.sceneNumber = line.string[line.sceneNumberRange]''' #syntax hurty: RANGE
            
        
        
        ## set color for outline elements
        '''if (line.type == LineType.heading or line.type == LineType.section or line.type == LineType.synopse):
            line.color = self.colorForHeading(line)'''
        
        
        ## Markers
        # line.marker = self.markerForLine(line)
        
        if (line.isTitlePage):
            if ":" in line.string and len(line.string) > 0:
                ## If the title doesn't begin with \t or space, format it as key name
                if (
                    line.string[0] != ' ' and
                    line.string[0] != '\t' ):
                    
                    line.titleRange = loc_len(0, line.string.index(":") + 1) 
                else:
                    line.titleRange = loc_len(0, 0)
    

    
    

    


    
    

    ### Notifies character cue that it has a dual dialogue sibling
    def makeCharacterAwareOfItsDualSiblingFrom(self, index: int):
        i: int = index - 1
        while (i >= 0):
            prevLine: Line = self.lines[i]
            
            if (prevLine.type == LineType.character):
                prevLine.nextElementIsDualDialogue = True
                break
            
            if (not prevLine.isDialogueElement and not prevLine.isDualDialogueElement):
                break
            i -= 1
        
    

    def sceneNumberForChars(self, string: str, length: int) -> loc_len:
        backNumberIndex: int = None
        note: int = 0
        
        for i in range(length-1, 0):
            c: str = string[:i]
            
            ## Exclude note ranges: [[ Note ]]
            if (c == ' '):
                continue
            if (c == ']' and note < 2):
                note += 1 
                continue 
            if (c == '[' and note > 0):
                note -= 1 
                continue
            
            ## Inside a note range
            if (note == 2):
                continue
            
            if (backNumberIndex == None):
                if (c == '#'):
                    backNumberIndex = i
                else: 
                    break
            else: 
                if (c == '#'):
                    return loc_len(i+1, backNumberIndex-i-1)
                
        
        return loc_len(0, 0) # syntax hurty : why return range of 0?
    

    def markerForLine(self, line: Line) -> str:
        line.markerRange = loc_len(0,0) 
        line.marker = ""
        line.markerDescription = ""
        
        markerColor: str = ""
        markerContent: str = ""
        
        ## Get the last marker. If none is found, just return ""
        marker: list = line.contentAndRangeForLastNoteWithPrefix("marker")
        if (marker == None):
            return ""
        
        ## The correct way to add a marker is to write [[marker color:Content]], but we'll be gratitious here.
        _range: loc_len = marker[0].rangeValue # syntax hurty: RANGE
        string: str = marker[1]
        
        if (not ":" in string) and (" " in string):
            ## No colon, let's separate components.
            ## First words will always be "marker", so get the second word and see if it's a color
            words: list[str] = string.split()
            descriptionStart: int = len("marker ")
            
            if (words.count > 1):
                potentialColor: str = words[1].lower()
                if potentialColor in self.colors:
                    markerColor = potentialColor
                
            
            
            ## Get the content after we've checked for potential color for this marker
            markerContent = string[(descriptionStart + markerColor):]
        
        elif ":" in string:
            l: int = string.index(":")
            markerContent = string[l+1:]
            
            left: str = string[:l]
            words: list = left.split()
            
            if len(words) > 1:
                markerColor = words[1]
        
        
        ## Use default as marker color if no applicable color found
        line.marker = markerColor.lower() if len(markerColor) > 0 else "default"
        line.markerDescription = markerContent.strip()
        line.markerRange = _range
        
        return markerColor
    

    ### Finds and sets the color for given outline-level line.
    ### Only the last one is used, preceding color notes are ignored.
    def colorForHeading(self, line: Line)-> str:
        colors: list = self.colors
        
        headingColor: str = "" #syntax hurty: __block
        line.colorRange = loc_len(0, 0)
        
        # noteContents: dict[any, str] = line.noteContentsAndRanges # NOTE: does obj-c flip the key and value ??
        for key in noteContents.keys():
            _range = key.rangeValue #syntax hurty: RANGE Value ???
            content: str = noteContents[key].lower
            
            ## We only want the last color on the line, which DOESN'T bleed out.
            ## The values come from a dictionary, so we can't be sure, so just skip it if it's an earlier one.
            if (line.colorRange.location > _range.location or
                ((_range == line.length) and line.noteOut) ):
                continue
            
            ## We can define a color using both [[color red]] or just [[red]], or #ffffff
            if ("color " in content):
                ## "color red"
                headingColor = content[len("color "):]
                line.colorRange = _range
            
            elif (content in colors 
                  or (len(content) == 7 and content[0] == '#')):
                ## pure "red" or "#ff0000"
                headingColor = content
                line.colorRange = _range 
        
        return headingColor


    #pragma mark - Title page

    ### Returns the title page lines as string
    def titlePageAsString(self,) -> str:
        string: str = ""
        for line in self.lines:
            if (not line.isTitlePage):
                break
            string += (line.string + "\n")
        
        return string
    

    ### Returns just the title page lines
    def titlePageLines(self) -> list[Line]:
        lines: list = []
        for line in self.lines:
            if (not line.isTitlePage):
                break
            lines.append(line)
        
        return lines


    ### Re-parser the title page and returns a weird array structure: 
    ### `[ { "key": "value }, { "key": "value }, { "key": "value } ]`.
    ### This is because we want to maintain the order of the keys
    ### and though ObjC dictionaries sometimes stay in the correct order, 
    ### things don't work like that in Swift.
    def parseTitlePage(self) -> list[dict[str, list[Line]]]:
        self.titlePage.clear() # NOTE: Necessary in Python?
        
        ## Store the latest key
        key = ""
        # titlePageMacros: BeatMacroParser = BeatMacroParser # syntax hurty: MACROS
        
        ## Iterate through lines and break when we encounter a non- title page line
        for line in self.safeLines:
            if (not line.isTitlePage):
                break
            
            # [self resolveMacrosOn:line parser:titlePageMacros] # syntax hurty: MACROS
            
            ## Reset flags
            line.beginsTitlePageBlock = False # synatx hurty: this is a macro I guess? IDK how these are set in the Line class...
            line.endsTitlePageBlock = False
            
            ## Determine if the line is empty
            empty: bool = False
            
            ## See if there is a key present on the line ("Title: ..." -> "Title")
            if (line.titlePageKey.length > 0):
                key = line.titlePageKey.lower()
                if (key == "author"):
                    key = "authors"
                
                line.beginsTitlePageBlock = True
                
                titlePageValue: dict = {key: []} # syntax hurty: ???
                self.titlePage.update(titlePageValue)
                
                ## Add the line into the items of the current line, IF IT'S NOT EMPTY
                trimmed = line.string[(len(line.titlePageKey)+1):].strip()
                if (len(trimmed) == 0):
                    empty = True
            
            
            ## Find the correct item in an array of dictionaries
            ## [ { "title": [Line] } , { ... }, ... ]
            items: list = self.titlePage[key]
            if (items == None):
                continue
            
            ## Add the line if it's not empty
            if (not empty):
                items.append(line)
        
        
        ## After we've gathered all the elements, lets iterate them once more to determine where blocks end.
        for element in self.titlePage:
            lines: list[Line] = element.values()[0]
            lines[0].beginsTitlePageBlock = True
            lines[-1].endsTitlePageBlock = True
        
        
        return self.titlePage
    

    ### Returns the lines for given title page key.
    ### For example,`Title` would return something like `["My Film"]`.
    def titlePageArrayForKey(self, key: str) -> list[Line]:
        for d in self.titlePage:
            if d.keys()[0] == key:
                return d[d.keys()[0]]
        return None
    


    #pragma mark - Finding character ranges

    def rangesInChars(self,
                      string: str,
                      length: int,
                      startString: str,
                      endString: str,
                      delimLength: int,
                      excludes: list,
                      line: Line) -> set:
        ## Let's use the asym method here, just put in our symmetric delimiters.
        return self.asymRangesInChars(string,
                                      length,
                                      startString,
                                      endString,
                                      delimLength,
                                      delimLength,
                                      excludes,
                                      line)
    


    # @note This is a confusing method name, but only because it is based on the old rangesInChars method. However, it's basically the same code, but I've put in the ability to seek ranges between two delimiters that are **not** the same, and can have asymmetrical length.  The original method now just calls this using the symmetrical delimiters.
    # NOTE: oh dear
    def asymRangesInChars(string: str, 
                          length: int,
                          startString: str, 
                          endString: str,
                          startLength: int,
                          delimLength: int,
                          excludes: list,
                          line: Line) -> set:
    
        indexSet: set = set() # NOTE: fuck i have to go back and redo all the sets AAAAAA
        if (length < startLength + delimLength):
            return indexSet
        
        _range = loc_len(-1, 0)
        
        for i in range(length - delimLength):
            ## If this index is contained in the omit character indexes, skip
            if i in excludes:
                continue
            
            ## First check for escape character
            if (i > 0):
                prevChar: str = string[i-1]
                if (prevChar == '\\'):
                    line.escapeRanges.add(i - 1)
                    continue

            
            if (_range.location == -1):
                ## Next, see if we can find the whole start string
                found: bool = True
                for k in _range(startLength):
                    if (i+k >= length):
                        break
                    elif (startString[k] != string[i+k]):
                        found = False
                        break
                    
                if (not found):
                    continue
                
                ## Successnot  We found a matching string
                _range.location = i
                
                ## Pass the starting string
                i += startLength-1
                
            else:
                ## We have found a range, let's see if we find a closing string.
                found: bool = True
                for k in range(delimLength):
                    if (endString[k] != string[i+k]):
                        found = False
                        break
                
                if (not found):
                    continue
                
                ## Success, we found a closing string.
                _range.length = i + delimLength - _range.location

                for idx in _range_from_loc_len(_range):
                    indexSet.add(idx)
                
                ## Add the current formatting ranges to future excludes
                excludes.add(n for n in range(_range.location, startLength))
                excludes.add(n for n in range(i, delimLength))
                
                _range.location = -1
                
                ## Move past the ending string
                i += delimLength - 1
            
        return indexSet
    

    def rangesOfOmitChars(string: str,
                          length: int,
                          line: Line,
                          lastLineOut: bool,
                          stars: set )-> set:
        line.omitIn = lastLineOut
        
        indexSet: set = set()
        _range: loc_len =  loc_len(0, 0) if (line.omitIn) else loc_len(None, 0) # NOTE: not sure about just setting the location to None
        
        for i in range(length - 1): 
            if (i+1 > length): break
            c1 = string[i]
            c2 = string[i+1]
            
            if (c1 == '/' and c2 == '*' and _range.location == None):
                stars.add(i+1)
                _range.location = i
                
            elif (c1 == '*' and c2 == '/'):
                if (_range.location == None): continue
                
                stars.add(i)
                
                _range.length = i - _range.location + fc.OMIT_PATTERN_LENGTH
                indexSet.add(n for n in _range_from_loc_len(_range))
                
                _range = loc_len(None, 0)
            
        
        
        if (_range.location is not None):
            line.omitOut = True
            indexSet.update(loc_len(_range.location, len(line) - _range.location + 1))
        else:
            line.omitOut = False
        
        
        return indexSet
    


    #pragma mark - Fetching Outline Data ---- BACKBRUNER

    ### Returns a tree structure for the outline. Only top-level elements are included, get the rest using `element.chilren`.
    '''def NSArray*)outlineTree
    {
        NSMutableArray* tree = NSMutableArray.new
        
        NSInteger topLevelDepth = 0
        
        for (OutlineScene* scene in self.outline) {
            if (scene.type == section) {
                ## First define top level depth
                if (scene.sectionDepth > topLevelDepth and topLevelDepth == 0) {
                    topLevelDepth = scene.sectionDepth
                }
                elif (scene.sectionDepth < topLevelDepth) {
                    topLevelDepth = scene.sectionDepth
                }
                
                ## Add section to tree if applicable
                if (scene.sectionDepth == topLevelDepth) {
                    [tree addObject:scene]
                }

            } elif (scene.sectionDepth == 0) {
                ## Add bottom-level objects (scenes) by default
                [tree addObject:scene]
            }
        }
        
        return tree
    }

    ### Returns the first outline element which contains at least a part of the given range.
    def OutlineScene*)outlineElementInRange:(NSRange)range
    {
        for (OutlineScene *scene in self.safeOutline) {
            if (NSIntersectionRange(range, scene.range).length > 0 or NSLocationInRange(range.location, scene.range)) {
                return scene
            }
        }
        return None
    }

    ### Updates scene numbers for scenes. Autonumbered will get incremented automatically.
    ### - note: the arrays can contain __both__ `OutlineScene` or `Line` items to be able to update line content individually without building an outline.
    def updateSceneNumbers:(NSArray*)autoNumbered forcedNumbers:(NSSet*)forcedNumbers
    {
        static NSArray* postfixes
        if (postfixes == None) postfixes = @[@"A", @"B", @"C", @"D", @"E", @"F", @"G"]

        NSInteger sceneNumber = [self sceneNumberOrigin]
        for (id item in autoNumbered) {
            Line* line; OutlineScene* scene
            
            if ([item isKindOfClass:OutlineScene.class]) {
                ## This was a scene
                line = ((OutlineScene*)item).line
                scene = item
            }
            else {
                ## This was a plain Line object
                line = item
            }
            
            if (line.omitted) {
                line.sceneNumber = @""
                continue
            }
            
            NSString* oldSceneNumber = line.sceneNumber
            NSString* s = [NSString stringWithFormat:@"%lu", sceneNumber]
                    
            if ([forcedNumbers containsObject:s]) {
                for (NSInteger i=0; i<postfixes.count; i += 1) {
                    s = [NSString stringWithFormat:@"%lu%@", sceneNumber, postfixes[i]]
                    if (not [forcedNumbers containsObject:s]) break
                }
            }
            
            if (not [oldSceneNumber isEqualToString:s]) {
                if (scene != None) [self.outlineChanges.updated addObject:scene]
            }

            line.sceneNumber = s
            sceneNumber += 1
        }
    }

    ### Returns a set of all scene numbers in the outline
    def NSSet*)sceneNumbersInOutline
    {
        NSMutableSet<NSString*>* sceneNumbers = NSMutableSet.new
        for (OutlineScene* scene in self.outline) {
            [sceneNumbers addObject:scene.sceneNumber]
        }
        return sceneNumbers
    }

    ### Returns the number from which automatic scene numbering should start from
    def NSInteger)sceneNumberOrigin
    {
        NSInteger i = [self.documentSettings getInt:DocSettingSceneNumberStart]
        if (i > 0) return i
        else return 1
    }

    ### Gets and resets the changes to outline
    def changesInOutline() -> OutlineChanges:
    
        ## Refresh the changed outline elements
        for (OutlineScene* scene in self.outlineChanges.updated):
            [self updateScene:scene at:NSNotFound lineIndex:NSNotFound]
        
        for (OutlineScene* scene in self.outlineChanges.added):
            [self.updateScene(scene=scene. at:NSNotFound lineIndex:NSNotFound)]
        
        
        ## If any changes were made to the outline, rebuild the hierarchy.
        if (self.outlineChanges.hasChanges):
            self.updateOutlineHierarchy()
        
        changes: OutlineChanges = self.outlineChanges.copy # syntax hurty - MEMORY MANAGEMENT
        self.outlineChanges = OutlineChanges
        
        return changes
    

    ### Returns an array of dictionaries with UUID mapped to the actual string.
    def outlineUUIDs() -> list[dict[str, str]]:
        outline: list = []
        for scene in self.outline:
            outline.append(
                {
                    "uuid": scene.line.uuid.UUIDString,
                    "string": scene.line.string
                }
            )
        
        return outline'''
    
    # HOT RELOAD
    #pragma mark - Handling changes to outline ---- BACKBURNER
    ## TODO: Maybe make this a separate class, or are we stepping into the dangerous parts of OOP?

    ### Updates the current outline from scratch. Use sparingly.
    '''def updateOutline(self):
        self.updateOutlineWithLines(self.safeLines)


    ### Updates the whole outline from scratch with given lines.
    def updateOutlineWithLines(self, lines: list[Line]):
        self.outline: list = []
            
        for i in range(len(lines)):
            line: Line = self.lines[i]
            if not line.isOutlineElement():
                continue
            
            self.updateSceneForLine(line, len(self.outline), i)
        
        
        self.updateOutlineHierarchy
    

    ### Adds an update to this line, but only if needed
    def addUpdateToOutlineIfNeededAt(lineIndex: int):
        ## Don't go out of range
        if (self.lines.count == 0) return
        elif (lineIndex >= self.lines.count) lineIndex = self.lines.count - 1
        
        Line* line = self.safeLines[lineIndex]

        ## Nothing to update
        if (line.type != synopse and not line.isOutlineElement and line.noteRanges.count == 0 and line.markerRange.length == 0) return

        ## Find the containing outline element and add an update to it
        NSArray* lines = self.safeLines
        
        for (NSInteger i = lineIndex; i >= 0; i -= 1) {
            Line* line = lines[i]
            
            if (line.isOutlineElement) {
                [self addUpdateToOutlineAtLine:line didChangeType:false]
                return
            }
        }
    


    ### Forces an update to the outline element which contains the given line. No additional checks.
    def addUpdateToOutlineAtLine:(Line*)line didChangeType:(bool)didChangeType
    {
        OutlineScene* scene = [self outlineElementInRange:line.textRange]
        if (scene) [_outlineChanges.updated addObject:scene]
        
        ## In some cases we also need to update the surrounding elements
        if (didChangeType) {
            OutlineScene* previousScene = [self outlineElementInRange:loc_len(line.position - 1, 0)]
            OutlineScene* nextScene = [self outlineElementInRange:loc_len(NSMaxRange(scene.range) + 1, 0)]
            
            if (previousScene != None) [_outlineChanges.updated addObject:previousScene]
            if (nextScene != None) [_outlineChanges.updated addObject:nextScene]
        }
    }


    ### Updates the outline element for given line. If you don't know the index for the outline element or line, pass `NSNotFound`.
    def updateSceneForLine:(Line*)line at:(NSInteger)index lineIndex:(NSInteger)lineIndex
    {
        if (index == NSNotFound) {
            OutlineScene* scene = [self outlineElementInRange:line.textRange]
            index = [self.outline indexOfObject:scene]
        }
        if (lineIndex == NSNotFound) lineIndex = [self indexOfLine:line]
        
        OutlineScene* scene
        if (index >= self.outline.count or index == NSNotFound) {
            scene = [OutlineScene withLine:line delegate:self]
            [self.outline addObject:scene]
        } else {
            scene = self.outline[index]
        }
        
        [self updateScene:scene at:index lineIndex:lineIndex]
    }

    ### Updates the given scene and gathers its notes and synopsis lines. If you don't know the line/scene index pass them as `NSNotFound` .
    def updateScene:(OutlineScene*)scene at:(NSInteger)index lineIndex:(NSInteger)lineIndex
    {
        ## We can call this method without specifying the indices
        if (index == NSNotFound) index = [self.outline indexOfObject:scene]
        if (lineIndex == NSNotFound) lineIndex = [self.lines indexOfObject:scene.line]
        
        ## Reset everything
        scene.synopsis = NSMutableArray.new
        scene.beats = NSMutableArray.new
        scene.notes = NSMutableArray.new
        scene.markers = NSMutableArray.new
        
        NSMutableSet* beats = NSMutableSet.new
        
        for (NSInteger i=lineIndex; i<self.lines.count; i += 1) {
            Line* line = self.lines[i]
            
            if (line != scene.line and line.isOutlineElement) break
            
            if (line.type == synopse) {
                [scene.synopsis addObject:line]
            }
            
            if (line.noteRanges.count > 0) {
                [scene.notes addObjectsFromArray:line.noteData]
            }
            
            if (line.beats.count) {
                [beats addObjectsFromArray:line.beats]
            }
            
            if (line.markerRange.length > 0) {
                [scene.markers addObject:@{
                    @"description": (line.markerDescription) ? line.markerDescription : @"",
                    @"color": (line.marker) ? line.marker : @"",
                }]
            }
        }
        
        scene.beats = [NSMutableArray arrayWithArray:beats.allObjects]
    }

    ### Inserts a new outline element with given line.
    def addOutlineElement:(Line*)line
    {
        NSInteger index = NSNotFound

        for (NSInteger i=0; i<self.outline.count; i += 1) {
            OutlineScene* scene = self.outline[i]

            if (line.position <= scene.position) {
                index = i
                break
            }
        }

        _changeInOutline = YES

        OutlineScene* scene = [OutlineScene withLine:line delegate:self]
        if (index == NSNotFound) [self.outline addObject:scene]
        else [self.outline insertObject:scene indexindex]

        ## Add the scene
        [_outlineChanges.added addObject:scene]
        ## We also need to update the previous scene
        if (index > 0 and index != NSNotFound) [_outlineChanges.updated addObject:self.outline[index - 1]]
    }

    ### Remove outline element for given line
    def removeOutlineElementForLine:(Line*)line
    {
        OutlineScene* scene
        NSInteger index = NSNotFound
        for (NSInteger i=0; i<self.outline.count; i += 1) {
            scene = self.outline[i]
            if (scene.line == line) {
                index = i
                break
            }
        }
        
        if (index == NSNotFound) return
            
        _changeInOutline = YES
        [_outlineChanges.removed addObject:scene]
        
        [self.outline removeObjectAtIndex:index]

        ## We also need to update the previous scene
        if (index > 0) [_outlineChanges.updated addObject:self.outline[index - 1]]
    }

    ### Rebuilds the outline hierarchy (section depths) and calculates scene numbers.
    def updateOutlineHierarchy()
        NSUInteger sectionDepth = 0
        NSMutableArray *sectionPath = NSMutableArray.new
        OutlineScene* currentSection
        
        NSMutableArray* autoNumbered = NSMutableArray.new
        NSMutableSet<NSString*>* forcedNumbers = NSMutableSet.new
            
        for (OutlineScene* scene in self.outline) {
            scene.children = NSMutableArray.new
            scene.parent = None
            
            if (scene.type == section) {
                if (sectionDepth < scene.line.sectionDepth) {
                    scene.parent = sectionPath.lastObject
                    [sectionPath addObject:scene]
                } else {
                    while (sectionPath.count > 0) {
                        OutlineScene* prevSection = sectionPath.lastObject
                        [sectionPath removeLastObject]
                        
                        ## Break at higher/equal level section
                        if (prevSection.sectionDepth <= scene.line.sectionDepth) break
                    }
                    
                    scene.parent = sectionPath.lastObject
                    [sectionPath addObject:scene]
                }
                
                ## Any time section depth has changed, we need probably need to update the whole outline structure in UI
                if (scene.sectionDepth != scene.line.sectionDepth) {
                    self.outlineChanges.needsFullUpdate = true
                }
                
                sectionDepth = scene.line.sectionDepth
                scene.sectionDepth = sectionDepth
                
                currentSection = scene
            } else {
                ## Manage scene numbers
                if (scene.line.sceneNumberRange.length > 0) [forcedNumbers addObject:scene.sceneNumber]
                else [autoNumbered addObject:scene]
                
                ## Update section depth for scene
                scene.sectionDepth = sectionDepth
                if (currentSection != None) scene.parent = currentSection
            }
            
            ## Add this object to the children of its parent
            if (scene.parent) {
                [scene.parent.children addObject:scene]
            }
        }
        
        ## Do the actual scene number update.
        [self updateSceneNumbers:autoNumbered forcedNumbers:forcedNumbers]
    

    ### NOTE: This method is used by line preprocessing to avoid recreating the outline.
    ### It has some overlapping functionality with `updateOutlineHierarchy` and `updateSceneNumbers:forcedNumbers:`.
    def updateSceneNumbersInLines()
    
        NSMutableArray* autoNumbered = NSMutableArray.new
        NSMutableSet<NSString*>* forcedNumbers = NSMutableSet.new
        for (Line* line in self.safeLines):
            if (line.type == LineType.heading and not line.omitted):
                if (line.sceneNumberRange.length > 0) [forcedNumbers addObject:line.sceneNumber]
                else autoNumbered addObject:li
        
        
        ### `updateSceneNumbers` supports both `Line` and `OutlineScene` objects.
        [self.updateSceneNumbers:autoNumbered forcedNumbers:forcedNumbers]'''
    

    # MEMORY SAFETY
    #pragma mark - Thread-safety for arrays  -= 1- BACKBURNER


    
    ''' `safeLines` and `safeOutline` create a copy of the respective array when called from a background thread.
    
    Because Beat now supports plugins with direct access to the parser, we need to be extra careful with our threads.
    Almost any changes to the screenplay in editor will mutate the `.lines` array, so a background process
    calling something that enumerates the array (ie. `linesForScene:`) will cause an immediate crash.
    
    '''

    '''def NSArray*)safeLines
    {
        if (NSThread.isMainThread) return self.lines
        else return self.lines.copy
    }
    def NSArray*)safeOutline
    {
        if (NSThread.isMainThread) return self.outline
        else return self.outline.copy
    }

    ### Returns a map with the UUID as key to identify actual line objects.
    def NSDictionary<NSUUID*, Line*>*)uuidsToLines
    {
        @synchronized (self.lines) {
            ## Return the cached version when possible  -= 1 or when we are not in the main thread.
            NSArray* lines = self.lines.copy
            if ([self.cachedLines isEqualToArray:lines]) return _uuidsToLines
            
            ## Store the current state of lines
            self.cachedLines = lines
            
            ## Create UUID array. This method is usually used by background methods, so we'll need to create a copy of the line array.
            NSMutableDictionary* uuids = [NSMutableDictionary.alloc initWithCapacity:lines.count]
            
            for (Line* line in lines) {
                if (line == None) continue
                uuids[line.uuid] = line
            }
            
            _uuidsToLines = uuids
            
            return _uuidsToLines
        }
    }'''


    #pragma mark - Convenience methods ---- BACKBURNER

    '''def numberOfScenes() -> int:
        lines: list = self.safeLines
        scenes: int = 0
        
        for line in lines:
            if line.type == LineType.heading:
                scenes += 1
        
        
        return scenes
    def scenes() -> list:
        outline: list = self.safeOutline; ## Use thread-safe lines
        scenes: list = []
        
        for scene in outline:
            if (scene.type == LineType.heading):
                scenes.append(scene)
        return scenes


    ### Returns the lines in given scene
    def linesForScene(scene: OutlineScene) -> list:
        ## Return minimal results for non-scene elements
        if scene is None:
            return []
        elif (scene.type == LineType.synopse):
            return scene.line
        
        lines = self.safeLines
            
        lineIndex: int = self.indexOfLine(scene.line)
        if lineIndex is None:
            return []
        
        ## Automatically add the heading line and increment the index
        NSMutableArray *linesInScene = NSMutableArray.new
        linesInScene.append(scene.line)
        lineIndex += 1
        
        ## Iterate through scenes and find the next terminating outline element.
        try:
            while lineIndex < len(lines):
                _line = lines[lineIndex]

                if (_line.type == LineType.heading or _line.type == LineType.section):
                    break
                linesInScene.append(_line)
                
                lineIndex += 1
        except:
            print("No lines found")
        
        return linesInScene
    

    ### Returns the previous line from the given line
    def previousLine(line: Line) -> Line:
        i: int = self.lineIndexAtPosition(line.position) ## Note: We're using lineIndexAtPosition because it's *way* faster
        
        if i > 0 and i is not None:
            return self.safeLines[i - 1]
        else:
            return None
    

    ### Returns the following line from the given line
    def nextLine(line: Line) -> Line:
    
        lines: list = self.safeLines
        i: int = self.lineIndexAtPosition(line.position) ## Note: We're using lineIndexAtPosition because it's *way* faster
        
        if (i != None) and (i < len(lines) - 1):
            return lines[i + 1]
        else:
            return None
    

    ### Returns the next outline item of given type
    ### @param type Type of the outline element (heading/section)
    ### @param position Position where to start the search
    ### @param depth Desired hierarchical depth (ie. 0 for top level objects of this type)
    def nextOutlineItemOfType(_type: LineType, position: int, depth: int) -> Line:
        idx: int = self.lineIndexAtPosition(position) + 1
        lines: list = self.safeLines
        
        for i in range(idx, len(lines)): 
            line = lines[i]
            
            ## If no depth was specified, we'll just pass this check.
            wantedDepth: int = line.sectionDepth if (depth == NSNotFound) else depth
            
            if (line.type == type and wantedDepth == line.sectionDepth):
                return line
            

        return None
    
    
    ### Returns the previous outline item of given type
    ### @param type Type of the outline element (heading/section)
    ### @param position Position where to start the search
    ### @param depth Desired hierarchical depth (ie. 0 for top level objects of this type)
    def previousOutlineItemOfType(_type: LineType, 
                                  position: int,
                                  depth: int) -> Line:
    
        idx: int = self.lineIndexAtPosition(position) - 1
        if (idx == None) or (idx < 0):
            return None
        
        lines: list = self.safeLines
        
        for i in range(0, idx):
            line: Line = lines[i]

            ## If no depth was specified, we'll just pass this check.
            wantedDepth: int = line.sectionDepth if (depth == NSNotFound) else depth
            
            if (line.type == type and wantedDepth == line.sectionDepth):
                return line
        return None

    #this func should be called lineFromUUID, methinks
    def lineWithUUID(_uuid: uuid.uuid4) -> Line:
    
        for line in self.lines:
            if line.uuidString == str(_uuid):
                return line
        return None'''

    #pragma mark - Element blocks ---- BACKBRUNER

    ### Returns the lines for a full dual dialogue block
    '''def NSArray<NSArray<Line*>*>*)dualDialogueFor:(Line*)line isDualDialogue:(bool*)isDualDialogue {
        if (not line.isDialogue and not line.isDualDialogue) return @[]
        
        NSMutableArray<Line*>* left = NSMutableArray.new
        NSMutableArray<Line*>* right = NSMutableArray.new
        
        NSInteger i = [self indexOfLine:line]
        if (i == NSNotFound) return @[]
        
        NSArray* lines = self.safeLines
        
        while (i >= 0) {
            Line* l = lines[i]
            
            ## Break at first normal character
            if (l.type == character) break
            
            i -= 1
        }
        
        ## Iterate forward
        for (NSInteger j = i; j < lines.count; j += 1) {
            Line* l = lines[j]
            
            ## Break when encountering a character cue (which is not the first line), and whenever seeing anything else than dialogue.
            if (j > i and l.type == character) break
            elif (not l.isDialogue and not l.isDualDialogue and l.type != empty) break
            
            if (l.isDialogue) [left addObject:l]
            else [right addObject:l]
        }
        
        ## Trim left & right
        while (left.firstObject.type == empty and left.count > 0) [left removeObjectAtIndex:0]
        while (right.lastObject.length == 0 and right.count > 0) [right removeObjectAtIndex:right.count-1]
        
        *isDualDialogue = (left.count > 0 and right.count > 0)
        
        return [left, right]
    }

    ### Returns the lines for screenplay block in given range.
    def blockForRange(self, _range: range) -> list[Line]:
        blockLines: list = []
        lines: list = []
        
        if (_range.length > 0):
            lines = self.linesInRange(_range)
        else:
            lines = self.lineAtPosition(_range.location)

        for line in lines:
            if line in blockLines:
                continue
            
            block: list = self.blockFor(line)
            blockLines += block
        
        
        return blockLines
    
    
    ### Returns the lines for full screenplay block associated with this line – a dialogue block, for example.
    def blockFor:(Line*)line -> list[Line]:
    
        NSArray *lines = self.lines
        NSMutableArray *block = NSMutableArray.new
        NSInteger blockBegin = [lines indexOfObject:line]
        
        ## If the line is empty, iterate upwards to find the start of the block
        if (line.type == empty) {
            NSInteger h = blockBegin - 1
            while (h >= 0) {
                Line *l = lines[h]
                if (l.type == empty) {
                    blockBegin = h + 1
                    break
                }
                h -= 1
            }
        }
        
        ## If the line is part of a dialogue block but NOT a character cue, find the start of the block.
        if ( (line.isDialogueElement or line.isDualDialogueElement) and not line.isAnyCharacter) {
            NSInteger i = blockBegin - 1
            while (i >= 0) {
                ## If the preceding line is not a dialogue element or a dual dialogue element,
                ## or if it has a length of 0, set the block start index accordingly
                Line *precedingLine = lines[i]
                if (not (precedingLine.isDualDialogueElement or precedingLine.isDialogueElement) or precedingLine.length == 0) {
                    blockBegin = i
                    break
                }
                
                i -= 1
            }
        }
        
        ## Add lines until an empty line is found. The empty line belongs to the block too.
        NSInteger i = blockBegin
        while (i < lines.count) {
            Line *l = lines[i]
            [block addObject:l]
            if (l.type == empty or l.length == 0) break
            
            i += 1
        }
        
        return block
    

    def rangeForBlock(block: list[Line]) -> range:
        _range = loc_len(block.firstObject.position, NSMaxRange(block.lastObject.range) - block.firstObject.position) # syntax hurty: RANGE
        return _range'''
    


    #pragma mark - Line position lookup and convenience methods

    ## Cached line for lookup
    '''prevLineAtLocationIndex: int = 0

    ### Returns line at given POSITION, not index.
    def lineAtIndex(position: int) -> Line:
        return self.lineAtPosition(position)
    

    # Returns the index in lines array for given line. This method might be called multiple times, so we'll cache the result.
    # This is a *very* small optimization, we're talking about `0.000001` vs `0.000007`. It's many times faster, but doesn't actually have too big of an effect.
    
    previousIndex = None # ? orphaned assignment?
    def indexOfLine(line: Line) -> int:
        lines: list = self.safeLines
        
        if (previousIndex < lines.count and previousIndex >= 0):
            if (line == lines[previousIndex]):
                return previousIndex
            
        
        
        index: int = [lines indexOfObject:line] # syntax hurty : indexOfObject
        previousIndex = index

        return index
    

    previousSceneIndex: int = None # why is this assignment orphaned between functions?

    def indexOfScene(scene: OutlineScene)-> int:
        outline: list = self.safeOutline
        
        if (previousSceneIndex < len(outline) and previousSceneIndex >= 0):
            if scene == outline[previousSceneIndex]:
                return previousSceneIndex
        
        
        index: int = [outline indexOfObject:scene] # syntax hurty: indexOfObject
        previousSceneIndex = index

        return index
    


    # This method finds an element in array that statisfies a certain condition, compared in the block. To optimize the search, you should provide `searchOrigin`  and the direction.
    # @returns Returns either the found element or None if none was found.
    # @param array The array to be searched.
    # @param searchOrigin Starting index of the search, preferrably the latest result you got from this same method.
    # @param descending Set the direction of the search: true for descending, false for ascending.
    # @param cacheIndex Pointer for retrieving the index of the found element. Set to NSNotFound if the result is None.
    # @param compare The block for comparison, with the inspected element as argument. If the element statisfies your conditions, return true.
    

    # NOTE: Holy shit this func declaration
    def findNeighbourIn(array: list, 
                        searchOrigin: int, 
                        descending: bool,
                        cacheIndex: int, 
                        block:(BOOL (^)(id item, NSInteger idx))compare) # I really need to figure out blocks ...
    
        ## Don't go out of range
        if (NSLocationInRange(searchOrigin, loc_len(-1, array.count))) {
            ## Uh, wtf, how does this work?
            ## We are checking if the search origin is in range from -1 to the full array count,
            ## so I don't understand how and why this could actually work, and why are we getting
            ## the correct behavior. The magician surprised themself, too.
            ##
            return None
        }
        elif (array.count == 0) return None
        
        NSInteger i = searchOrigin
        NSInteger origin = (descending) ? i - 1 : i + 1
        if origin == -1:
            origin = array.count - 1
        
        bool stop = False
        
        do { # syntax hurty: python does not have a do... while loop, only while loops
            if not descending:
                i += 1
                if (i >= array.count) i = 0
            else:
                i -= 1
                if (i < 0) i = array.count - 1
            
                    
            id item = array[i]
            
            if (compare(item, i)) {
                *cacheIndex = i
                return item
            }
            
            ## We have looped around the array (unsuccessfuly)
            if (i == searchOrigin or origin == -1) {
                NSLog(@"Failed to find match for %@ - origin: %lu / searchorigin: %lu   -= 1 %@", self.lines[searchOrigin], origin, searchOrigin, compare)
                break
            }
            
        } while (stop != YES)
        
        cacheIndex = NSNotFound
        return None
    



    # This method returns the line index at given position in document.
    # 
    # It uses a cyclical lookup, so the method won't iterate through all the lines every time.
    # Instead, it first checks the line it returned the last time, and after that, starts to iterate through lines from its position and given direction. Usually we can find
    # the line with 1-2 steps, and as we're possibly iterating through thousands and thousands of lines, it's much faster than finding items by their properties the usual way.
    
    def lineIndexAtPosition(position: int) -> int:
        lines: list = self.safeLines
        actualIndex: int = None
        NSInteger lastFoundPosition = 0
        
        ## First check if we are still on the same line as before
        if (NSLocationInRange(_lastLineIndex, loc_len(0, lines.count))) {
            Line* lastEdited = lines[_lastLineIndex]
            lastFoundPosition = lastEdited.position
            
            if (NSLocationInRange(position, lastEdited.range)) {
                return _lastLineIndex
            }
        }
        
        ## Cyclical array lookup from the last found position
        result: Line = [self findNeighbourIn:lines origin:_lastLineIndex descending:(position < lastFoundPosition) cacheIndex:&actualIndex block:^BOOL(id item, NSInteger idx) {
            l: Line = item
            return NSLocationInRange(position, l.range)
        }]
        
        if (result is not None):
            _lastLineIndex = actualIndex
            _lastEditedLine = result
            
            return actualIndex
        else:
            return self.lines.count - 1 if (self.lines.count > 0) else 0
        

    ### Returns the closest printable (visible) line for given line
    def closestPrintableLineFor(line: Line) -> Line:
        lines: list = self.lines
        
        i: int = [lines indexOfObject:line] # not sure what these three lines of code do...
        if i is None:
            return None
        
        while (i >= 0):
            l: Line = lines[i]
            
            if (l.type == action and i > 0):
                ## This might be part of a joined action paragraph block
                prev: Line = lines[i-1]
                if (prev.type == LineType.empty) and (not l.isInvisible):
                    return l
            elif (not l.isInvisible):
                return l
            
            i -= 1
        
        
        return None
    

    ### Rerturns the line object at given position
    ### (btw, why aren't we using the other method?)
    def lineAtPosition(position: int) -> Line:
    
        ## Let's check the cached line first
        if (NSLocationInRange(position, _prevLineAtLocation.range)) return _prevLineAtLocation
        
        lines: list = self.safeLines; ## Use thread safe lines for this lookup
        if (prevLineAtLocationIndex >= len(lines)) prevLineAtLocationIndex = 0
        
        ## Quick lookup for first object
        if (position == 0):
            return lines[0]
        
        ## We'll use a circular lookup here.
        ## It's HIGHLY possible that we are not just randomly looking for lines,
        ## but that we're looking for close neighbours in a for loop.
        ## That's why we'll either loop the array forward or backward to avoid
        ## unnecessary looping from beginning, which soon becomes very inefficient.
        
        NSUInteger cachedIndex
        
        bool descending = NO
        if (_prevLineAtLocation and position < _prevLineAtLocation.position):
            descending = True
        

        # syntax hurty: BLOCK    
        line: Line = [self findNeighbourIn:lines origin:prevLineAtLocationIndex descending:descending cacheIndex:&cachedIndex block:^BOOL(id item, NSInteger idx) {
            Line *l = item
            if (NSLocationInRange(position, l.range)) return YES
            else return NO
        }]
        
        if (line):
            _prevLineAtLocation = line
            prevLineAtLocationIndex = cachedIndex
            return line
        
        
        return None
    

    ### Returns the lines in given range (even overlapping)
    def linesInRange(_range: range) -> list:
        lines: list = self.safeLines
        linesInRange: list = []
        
        for line in lines:
            if ((NSLocationInRange(line.position, _range) or
                NSLocationInRange(_range.location, line.textRange) or
                NSLocationInRange(_range.location + _range.length, line.textRange)) and
                NSIntersectionRange(_range, line.textRange).length > 0
                ):
                linesInRange.append(line)
        
        return linesInRange
    

    ### Returns the scenes which intersect with given range.
    def scenesInRange(_range: range) -> list:
    
        scenes: list = []
        outline: list = self.safeOutline; ## Thread-safe outline
        
        ## When length is zero, return just the scene at the beginning of range
        if (_range.length == 0):
            scene = [self sceneAtPosition:_range.location]
            return scene if (scene is not None) else []
        
        
        for scene in outline:
            intersection: range = NSIntersectionRange(_range, scene.range) # syntax hurty: NSIntersectionRange
            if (intersection.length > 0) [scenes addObject:scene]
        
        
        return scenes
    

    ### Returns a scene which contains the given character index (position). An alias for `sceneAtPosition` for legacy compatibility.
    def sceneAtIndex(index: int) -> OutlineScene:
        return self.sceneAtPosition(index)
    

    ### Returns a scene which contains the given position
    def sceneAtPosition(index: int) -> OutlineScene:

        for scene in self.safeOutline:
            if (NSLocationInRange(index, scene.range) and scene.line is not None):
                return scene
        
        return None
    

    ### Returns all scenes contained by this section. You should probably use `OutlineScene.children` though.
    ### - note: Legacy compatibility. Remove when possible.
    def scenesInSection(topSection: OutlineScene) -> list:
    
        if (topSection.type != section):
            return []
        return topSection.children
    

    ### Returns the scene with given number (string)
    def sceneWithNumber(sceneNumber: str) -> OutlineScene:
    
        for scene in self.outline:
            if scene.sceneNumber.lower() == sceneNumber.lower():
                return scene
            
        return None'''
    #pragma mark - Line identifiers (UUIDs)  -= 1- BACKBURNER
    '''
    ### Returns every line UUID as an arrayg
    def NSArray*)lineIdentifiers:(NSArray<NSUUID*>*)lines
    {
        if (lines == None) lines = self.lines
        
        NSMutableArray *uuids = NSMutableArray.new
        for (Line *line in lines) {
            [uuids addObject:line.uuid]
        }
        return uuids
    }

    ### Sets the given UUIDs to each line at the same index. Note that you can provide either an array of `NSString`s or __REAL__ `NSUUID`s.
    def setIdentifiers(uuids: list[uuid.uuid4]):
    
        for i in range(0, len(uuids)):
            item = uuids[i]
            ## We can have either strings or real UUIDs in the array. Make sure we're using the correct type.
            _uuid: uuid.uuid4 = [NSUUID.alloc initWithUUIDString:item] if (item.isinstance(str))  else item # syntax hurty: ternary operator
                    
            if (i < self.lines.count and uuid != None):
                Line *line = self.lines[i]
                line.uuid = uuid
            
        
    

    ### Sets the given UUIDs to each outline element at the same index
    def setIdentifiersForOutlineElements:(NSArray*)uuids:
        for (NSInteger i=0; i<self.outline.count; i += 1) {
            if (i >= uuids.count) break
            
            OutlineScene* scene = self.outline[i]
            NSDictionary* item = uuids[i]
            
            NSString* uuidString = item[@"uuid"]
            NSString* string = item[@"string"]
            
            if ([scene.string.lowercaseString isEqualToString:string.lowercaseString]) {
                NSUUID* uuid = [NSUUID.alloc initWithUUIDString:uuidString]
                scene.line.uuid = uuid
            }
        }'''

    #pragma mark - Note parsing  -= 1- BACKBURNER

    ## All hope abandon ye who enter here.
    ## This is not a place of honor. No highly esteemed deed is commemorated here... nothing valued is here.
    ## What is here was dangerous and repulsive to us.


    ''' Parses notes for given line at specified index. You also need to specify the type the line had before we are parsing the notes.
    
    - Note: Note parsing is a bit convoluted. Because note rules are unlike any other element in Fountain (they can appear on any line,
    span across multiple lines and have rules for whitespace), parsing notes on the fly has turned out to be a bit clunky, especially with
    my existing code.
    
    This should probably be harmonized with the other parsing, but I had a hard time doing that. Multi-line notes require multiple passes
    through this method and it isn't exactly the most performant approach.
    
    If a line has an unterminated note (either with closing or opening brackets), we'll find the line which might open the block and
    call `parseNoteOutFrom:(NSInteger)lineIndex positionInLine:(NSInteger)positionInLine` to parse the
    whole block. This is done while in a parsing pass, so lines which require reformatting will be registered correctly.
    
    `BeatNoteData` object is created for each note range and stored into `line.noteData` array. For multi-line notes, only the
    line which begins the note will hold the actual content, and a placeholder `BeatNoteData` is created for subsequent lines.
    Note data object contains an empty string for every other line in the note block.
    '''

    '''def parseNotesFor:(Line*)line at:(NSInteger)lineIndex oldType:(LineType)oldType
    {
        ## TODO: Make some fucking sense to this
        
        ## This was probably a part of a note block. Let's parse the whole block instead of this single line.
        if (line.noteIn and line.noteOut and line.noteRanges.count == line.length) {
            NSInteger positionInLine
            NSInteger i = [self findNoteBlockStartIndexFor:line at:lineIndex positionInLine:&positionInLine]
            
            [self parseNoteOutFrom:i positionInLine:positionInLine]
            return
        }
        
        ## Reset note status
        [line.noteRanges removeAllIndexes]
        line.noteData = NSMutableArray.new
        
        line.noteIn = false
        line.noteOut = false
        
        unichar chrs[line.length]
        [line.string getCharacters:chrs]

        __block NSRange noteRange = loc_len(NSNotFound, 0)
        
        for (NSInteger i = 0; i < line.length - 1; i += 1) {
            unichar c1 = chrs[i]
            unichar c2 = chrs[i + 1]
            
            if (c1 == '[' and c2 == '[') {
                ## A note begins
                noteRange.location = i
            }
            elif (c1 == ']' and c2 == ']' and noteRange.location != NSNotFound) {
                ## We are terminating a normal note
                noteRange.length = i + 2 - noteRange.location
                NSRange contentRange = loc_len(noteRange.location + 2, noteRange.length - 4)
                NSString* content = [line.string substringWithRange:contentRange]
                
                BeatNoteData* note = [BeatNoteData withNote:content range:noteRange]
                [line.noteData addObject:note]
                [line.noteRanges addIndexesInRange:noteRange]
                
                noteRange = loc_len(NSNotFound, 0)
            }
            elif (c1 == ']' and c2 == ']') {
                ## We need to look back to see if this note is part of a note block
                line.noteIn = true; ## We might change this value later.
            }
        }
        
        ## Check if there was an unfinished not (except on the last line)
        if (noteRange.location != NSNotFound and lineIndex != _lines.count-1) {
            line.noteOut = true
        }
        
        ## Get previous line for later
        Line* prevLine = (lineIndex > 0) ? _lines[lineIndex - 1] : None
        
        if (line.noteIn or line.noteOut) {
            ## If this line receives a note, let's find out where the block possibly starts and reparse it.
            NSInteger positionInLine
            NSInteger i = [self findNoteBlockStartIndexFor:line at:lineIndex positionInLine:&positionInLine]
            
            [self parseNoteOutFrom:i positionInLine:positionInLine]
        }
        
        elif ((oldType == empty or line.type == empty or prevLine.noteOut) and lineIndex < self.lines.count ) {
            ## If the line has changed type, let's try to find out if this line creates or cancels an existing note block.
            ## Don't check this when parsing for the first time.
            NSInteger positionInLine
            NSInteger i = [self findNoteBlockStartIndexFor:line at:lineIndex positionInLine:&positionInLine]
            
            if (i == NSNotFound) return

            [self parseNoteOutFrom:i positionInLine:positionInLine]
        }
    }
    # not ? fucntion too much big ?
    def parseNoteOutFrom:(NSInteger)lineIndex positionInLine:(NSInteger)position
    {
        if (lineIndex == NSNotFound) return
        
        NSMutableIndexSet* affectedLines = NSMutableIndexSet.new
        bool cancel = false; ## Check if we should remove the note block from existence
        Line* lastLine
        
        for (NSInteger i=lineIndex; i<_lines.count; i += 1) {
            Line* l = _lines[i]
            
            if (l.type == empty) cancel = true
            
            [affectedLines addIndex:i]
            if (l.canTerminateNoteBlock) {
                lastLine = l
                break
            }
            elif (l.canBeginNoteBlock and i != lineIndex) {
                [affectedLines removeIndex:i]
                break
            }
        }
        
        __block NSMutableString* noteContent = NSMutableString.new
        __block NSString* color = @""
        
        if (lastLine == None) cancel = true
        
        ## Go through the note content
        [affectedLines enumerateIndexesUsingBlock:^(NSUInteger idx, BOOL * _Nonnull stop) {
            Line* l = _lines[idx]
            NSRange range
            
            ## For the first line, we'll use the previously determined position
            NSInteger p = NSNotFound
            if (idx == affectedLines.firstIndex and [l canBeginNoteBlockWithActualIndex:&p]) {
                ## First line
                range = loc_len(p, l.length - p)
                
                ## Find color in the first line of a note
                if (not cancel) {
                    NSString* firstNote = [l.string substringWithRange:range]
                    NSInteger cIndex = [firstNote rangeOfString:@":"].location
                    if (cIndex != NSNotFound) color = [firstNote substringWithRange:loc_len(2, cIndex - 2 )]
                }
                
            } elif ([l canTerminateNoteBlockWithActualIndex:&p]) {
                ## Last line
                range = loc_len(0, p+2)
            } else {
                ## Line in the middle
                range = loc_len(0, l.length)
            }
            
            if (range.location == NSNotFound or range.length == NSNotFound) return
            
            if (cancel) {
                [_changedIndices addIndex:idx]
                
                if (not l.noteIn and idx != affectedLines.firstIndex and l.type != empty) {
                    *stop = true
                    return
                }
                
                [l.noteRanges removeIndexesInRange:range]
            }
            else {
                [l.noteRanges addIndexesInRange:range]
                [_changedIndices addIndex:idx]
                
                ## Add correct noteIn/noteOut properties.
                if (idx == affectedLines.firstIndex) {
                    l.noteOut = true; ## First line always bleeds out
                    if (l.noteData.lastObject.multiline) [l.noteData removeLastObject]
                } elif (idx == affectedLines.lastIndex) {
                    ## Last line always receives a note
                    l.noteIn = true
                    ## Remove the leading multiline note if needed
                    if (l.noteData.firstObject.multiline) [l.noteData removeObjectAtIndex:0]
                } else {
                    l.noteIn = true
                    l.noteOut = true
                    
                    [l.noteData removeAllObjects]
                }
                
            
                if (not cancel) {
                    if (idx > affectedLines.firstIndex) {
                        [noteContent appendString:@"\n"]
                        
                        BeatNoteData* note = [BeatNoteData withNote:@"" range:range]
                        note.multiline = true
                        note.color = color
                        
                        if (idx != affectedLines.firstIndex and idx < affectedLines.lastIndex) [l.noteData addObject:note]
                        elif (idx == affectedLines.lastIndex) [l.noteData insertObject:note atIndex:0]
                    }

                    [noteContent appendString:[l.string substringWithRange:range]]
                }
            }
        }]
            
        ## Remove the last parsed multiline note
        Line* firstLine = _lines[lineIndex]
        BeatNoteData* lastNote = firstLine.noteData.lastObject
        if (lastNote.multiline) [firstLine.noteData removeLastObject]
        
        if (cancel or noteContent.length <= 4) return
        
        ## Create the actual note
        [noteContent setString:[noteContent substringWithRange:loc_len(2, noteContent.length - 4 )]]
        
        BeatNoteData* note = [BeatNoteData withNote:noteContent _range=loc_len(position, firstLine.length - position)]
        note.multiline = true
        note.color = color
        
        [firstLine.noteData addObject:note]
    }

    def findNoteBlockStartIndexFor(
        line, 
        at:(NSInteger)idx, 
        positionInLine:(NSInteger*)position) -> int:
        NSArray* lines = self.lines
        
        if (idx == NSNotFound) idx = [self.lines indexOfObject:line]; ## Get index if needed
        elif (idx == NSNotFound) return NSNotFound
        
        NSInteger noteStartLine = NSNotFound
        
        for (NSInteger i=idx; i>=0; i -= 1) {
            Line* l = lines[i]
            if (l.type == empty and i < idx) break;   ## Stop if we're not in a block
            
            unichar chrs[l.length]
            [l.string getCharacters:chrs]
            
            for (NSInteger k=l.string.length-1; k>=0; k -= 1) {
                if (k > 0) {
                    unichar c1 = chrs[k]
                    unichar c2 = chrs[k-1]
                    
                    if (c1 == ']' and c2 == ']') {
                        break; ## Cancel right away at terminating note
                    }
                    elif (c1 == '[' and c2 == '[') {
                        ## The note opening was found
                        noteStartLine = i
                        *position = k - 1
                        break
                    }
                }
            }
            
            ## We found the line, no reason to look backwards anymore
            if (noteStartLine != NSNotFound) break
        }
            
        return noteStartLine'''



    #pragma mark - Colors

    ### We can't import `BeatColors` here, so let's use generic color names
    def colors() -> list[str]:
        colors: list
        if (colors == None):
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
                    "brown"]
        return colors



    #pragma mark - Debugging tools

    '''def report()
        lastPos = 0
        lastLen = 0
        for (line in self.lines) {
            error = ""
            if (lastPos + lastLen != line.position) error = " 🔴 ERROR"
            
            if (error.length > 0) {
                print(
                    "   (%lu -> %lu): %@ (%lu) %@ (%lu/%lu)", line.position, line.position + line.string.length + 1, line.string, line.string.length, error, lastPos, lastLen
                    )
            }
            lastLen = line.string.length + 1
            lastPos = line.position
        }'''

'''
Thank you, Hendrik Noeller, for making Beat possible.
Without your massive original work, any of this had never happened.
'''
 
