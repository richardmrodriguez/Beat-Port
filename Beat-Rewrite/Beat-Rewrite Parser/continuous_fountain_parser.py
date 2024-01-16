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
 


# import "NSString+CharacterControl.h"
# import "NSMutableIndexSet+Lowest.h"
# import "NSIndexSet+Subset.h"

from line import Line
from outline_scene import OutlineScene
# import <BeatParsing/BeatParsing-Swift.h> # ? doesn't exist in the repoo currently
import "ContinuousFountainParser+Preprocessing.h" # another circular import? or do I just not understand categories in Objective-C?

NEW_OUTLINE: bool = True

#pragma mark - Parser

# @interface ContinuousFountainParser()

changeInOutline: bool
outlineChanges: OutlineChanges()
changedOutlineElements: list
n
### The line which was last edited. We're storing this when asking for a line at caret position.
lastEditedLine: Line
### An index for the last fetched line result when asking for lines in range
lastLineIndex: int
### The range which was edited most recently.
editedRange: range #sytnax hurty - RANGES are different in python!

## Title page parsing
openTitlePageKey: str
previousTitlePageKey: str

## Static parser flag
nonContinuous: bool

## Cached line set for UUID creation
cachedLines: list # syntax hurty: MUTABLE SETS and UUID

macros: BeatMacroParser()

##
prevLineAtLocation: Line


class ContinuousFountainParser:

    patterns: dict = []


    #pragma mark - Initializers

    ### Extracts the title page from given string
    def titlePageForString(string: str) -> list:
        rawLines: list[str] = string.split("\n")
        
        if rawLines.count == 0: 
             return []
        elif ":" not in rawLines[0]:
             return []
        
        text = ""
        
        for l in rawLines:
            ## Break at empty line
            text += l += "\n"
            if l == "":
                break
        
        text += "\n"
        
        parser = [ContinuousFountainParser.alloc initWithString:text]
        parser.updateMacros() ## Resolve macros
        return parser.titlePage
    

    def ContinuousFountainParser*)initStaticParsingWithString:(NSString*)string settings:(BeatDocumentSettings*)settings
    {
        return [self initWithString:string delegate:None settings:settings nonContinuous:YES]
    }
    def ContinuousFountainParser*)initWithString:(NSString*)string delegate:(id<ContinuousFountainParserDelegate>)delegate nonContinuous:(bool)nonContinuous
    {
        return [self initWithString:string delegate:delegate settings:None nonContinuous:nonContinuous]
    }
    def ContinuousFountainParser*)initWithString:(NSString*)string delegate:(id<ContinuousFountainParserDelegate>)delegate
    {
        return [self initWithString:string delegate:delegate settings:None]
    }
    def ContinuousFountainParser*)initWithString:(NSString*)string delegate:(id<ContinuousFountainParserDelegate>)delegate settings:(BeatDocumentSettings*)settings
    {
        return [self initWithString:string delegate:delegate settings:settings nonContinuous:NO]
    }
    def ContinuousFountainParser*)initWithString:(NSString*)string delegate:(id<ContinuousFountainParserDelegate>)delegate settings:(BeatDocumentSettings*)settings nonContinuous:(bool)nonContinuous
    {
        self = [super init]
        
        if (self) {
            _lines = NSMutableArray.array
            _outline = NSMutableArray.array
            _changedIndices = NSMutableIndexSet.indexSet
            _titlePage = NSMutableArray.array
            _storylines = NSMutableSet.set
            
            _delegate = delegate
            _nonContinuous = nonContinuous
            _staticDocumentSettings = settings
            
            ## Inform that this parser is STATIC and not continuous (wtf, why is this done using dual values?)
            if (_nonContinuous) _staticParser = YES
            else _staticParser = NO
            
            [self parseText:string]
            [self updateMacros]
        }
        
        return self
    }
    def ContinuousFountainParser*)initWithString:(NSString*)string
    {
        return [self initWithString:string delegate:None]
    }


    #pragma mark - Document setting getter

    ### Returns either document settings OR static document settings. Note that if static document settings are provided, they are preferred.
    ### TODO: Perhaps the parser should hold the document settings and read them when originally parsing the document? This would be much more sensible.
    def BeatDocumentSettings*)documentSettings
    {
        if (self.staticDocumentSettings != None) return self.staticDocumentSettings
        else return self.delegate.documentSettings
    }


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
            if ((type == heading or type == transitionLine) and
                line.numberOfPrecedingFormattingCharacters == 0):
                 string = string.upper
            
            ## Ensure correct whitespace before elements
            if ((line.isAnyCharacter or line.type == heading) and
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
                string += ine.string
            
        return string
    


    #pragma mark - Parsing

    #pragma mark Bulk parsing

    def parseText(self, text: str):
        _lines = []
        
        if (text == None): text = ""
        text = text.replace("\r\n", "\n") ## Replace MS Word/Windows line breaks with macOS ones # NOTE: Will this break text files on windows if we leave this?
        
        ## Split the text by line breaks
        lines: list = text.splitlines()
        
        position: int = 0; ## To track at which position every line begins
        
        previousLine: Line
        
        for rawLine in lines:
            index: int = len(_lines)
            line: Line = [[Line alloc] initWithString:rawLine position:position parser:self] # syntax hurty
            self.lines.append(line)
            
            self.parseTypeAndFormattingForLine(line, atIndex=index)
            
            ## Quick fix for mistaking an ALL CAPS action for a character cue
            if (previousLine.type == character and (line.string.length < 1 or line.type == empty)):
                
                previousLine.type = self.parseLineTypeFor(line, atIndex=(index - 1))
                if (previousLine.type == character): 
                    previousLine.type = action
            
                    
            position += rawLine.length + 1; ## +1 for newline character # NOTE: since this code adds 1 for newlines, we should NOT use 'keepends' when using str.splitlines()
            previousLine = line
        
        
        ## Reset outline
        _changeInOutline = True
        self.updateOutline()
        self.outlineChanges = OutlineChanges() # ? What or where is OutlineChanges? Is it a struct or a class?
        
        ## Reset changes (to force the editor to reformat each line)

        self.changedIndices.addIndexesInRange(range(0, len(self.lines))) # syntax hurty # RANGE
        
        ## Set identifiers (if applicable)
        self.setIdentifiersForOutlineElements(self.documentSettings.get(DocSettingHeadingUUIDs)) # syntax hurty
    

    ## This sets EVERY INDICE as changed.
    def resetParsing(self):
        index: int = 0
        while (index < self.lines.count):
            self.changedIndices.addIndex(index) # ? What does this func do exactly?
            index += 1
        
    


    #pragma mark - Continuous Parsing

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

    def parseChangeInRange(self, _range: range, withString=""): # NOTE: param name "range" shadowed the range type in python, changed it to _range
    
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
        if (nextLine != None and nextLine.string.length == 0 and
            not NSLocationInRange(_delegate.selectedRange.location, nextLine.range) and
            not NSLocationInRange(_delegate.selectedRange.location, line.range) and
            line.numberOfPrecedingFormattingCharacters == 0
            ):
            
            line.type = action
            self.changedIndices(addIndex=i)
            [_delegate applyFormatChanges] # syntax hurty : what the FUCK is a delegate
        


    #pragma mark Parsing additions

    def NSIndexSet*)parseAddition:(NSString*)string atPosition:(NSUInteger)position
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
        
        for (NSInteger i=0; i<string.length; i++) {
            if (currentRange < 0) currentRange = i
            
            unichar chr = [string characterAtIndex:i]
            
            if (chr == '\n') {
                NSString* addedString = [string substringWithRange:NSMakeRange(currentRange, i - currentRange)]
                line.string = [line.string stringByAppendingString:addedString]
                
                if (lineIndex < self.lines.count - 1) {
                    Line* nextLine = self.lines[lineIndex+1]
                    NSInteger delta = ABS(NSMaxRange(line.range) - nextLine.position)
                    [self decrementLinePositionsFromIndex:lineIndex+1 amount:delta]
                }
                
                [self addLineWithString:@"" atPosition:NSMaxRange(line.range) lineIndex:lineIndex+1]
                
                ## Increment current line index and reset inspected range
                lineIndex++
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
        [changedIndices addIndexesInRange:NSMakeRange(changedIndices.firstIndex + 1, lineIndex - changedIndices.firstIndex)]
        
        return changedIndices
    }


    #pragma mark Parsing removals

    def NSIndexSet*)parseRemovalAt:(NSRange)range {
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
            NSRange localRange = NSMakeRange(intersection.location - line.position, intersection.length)
            
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
                i++
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
    }


    #pragma mark Add / remove lines

    ### Removes a line from the parsed content and decrements positions of other lines
    def removeLineAtIndex(self, index: int):
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
            _prevLineAtLocation = None
    

    ### Adds a new line into the parsed content and increments positions of other lines
    def addLineWithString(self, string: str, position: int, index: int):
        newLine: Line = [Line.alloc initWithString(string=string, position=position, parser=self)]
        
        self.lines.insert(index, newLine)
        self.incrementLinePositionsFromIndex(index+1, amount=1) # syntax hurty: investigate this, this might be wrong now
        
        ## Reset cached line
        _lastEditedLine = None
    


    #pragma mark - Correcting parsed content for existing lines

    ### Intermediate method for `corretParsesInLines` which first finds the indices for line objects and then passes the index set to the main method.
    def correctParsesForLines(lines: list):
        NSMutableIndexSet *indices = NSMutableIndexSet.new
        
        for line in lines: 
            i: int = [lines indexOfObject:line]
            if (i != None): [indices addIndex:i]
        
        
        [self.correctParsesInLines:indices]
    

    ### Corrects parsing in given line indices
    def correctParsesInLines((NSMutableIndexSet*)lineIndices):
        while (lineIndices.count > 0) { # syntax hurty
            [self correctParseInLine:lineIndices.lowestIndex indicesToDo:lineIndices]
        }
    

    ### Corrects parsing in a single line. Once done, it will be removed from `indices`, but note that new indices might be added in the process.
    def correctParseInLine(index: int, indicesToDo:[]): # syntax hurty: indicesToDo: NSMutableIndexSet
    
        ## Do nothing if we went out of range.
        ## Note: for code convenience and clarity, some methods can ask to reformat lineIndex-2 etc.,
        ## so this check is needed.
        if (index < 0) or (index == NSNotFound) or (index >= self.lines.count):
            [indices removeIndex:index]
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
                (oldNotes not = None and not [oldNotes isEqualToIndexSet:currentLine.noteRanges]) or
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
        }


    #pragma mark - Incrementing / decrementing line positions

    ### A replacement for the old, clunky `incrementLinePositions` and `decrementLinePositions`. Automatically adjusts line positions based on line content.
    ### You still have to make sure that you are parsing correct stuff, though.
    def adjustLinePositionsFromm(self, index: int):
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
            index += 1
        
    


    #pragma mark - Macros

    def updateMacros
    {
        BeatMacroParser* parser = BeatMacroParser.new
        NSArray* lines = self.safeLines
        
        for (NSInteger i=0; i<lines.count; i++) {
            Line* l = lines[i]
            if (l.macroRanges.count == 0) continue
            
            [self resolveMacrosOn:l parser:parser]
            if (l.isOutlineElement or l.type == synopse) {
                [self addUpdateToOutlineAtLine:l didChangeType:false]
            }
        }
    }

    def resolveMacrosOn:(Line*)line parser:(BeatMacroParser*)macroParser
    {
        NSDictionary* macros = line.macros
        
        line.resolvedMacros = NSMutableDictionary.new
        
        NSArray<NSValue*>* keys = [macros.allKeys sortedArrayUsingComparator:^NSComparisonResult(NSValue*  _Nonnull obj1, NSValue*  _Nonnull obj2) {
            if (obj1.rangeValue.location > obj2.rangeValue.location) return true
            return false
        }]
        
        for (NSValue* range in keys) {
            NSString* macro = macros[range]
            id value = [macroParser parseMacro:macro]
            
            if (value != None) line.resolvedMacros[range] = [NSString stringWithFormat:@"%@", value]
        }
    }


    #pragma mark - Parsing Core

    ### Parses line type and formatting ranges for current line. This method also takes care of handling possible disabled types.
    ### @note Type and formatting are parsed by iterating through character arrays. Using regexes would be much easier, but also about 10 times more costly in CPU time.
    def parseTypeAndFormattingForLine(self, line: Line, index: int):
        oldType: LineType = line.type
        line.escapeRanges = [] # syntax hurty: NSMutableIndexSet
        line.type = self.parseLineTypeFor(line, atIndex=index)
        
        ## Make sure we didn't receive a disabled type
        if ([self.delegate.disabledTypes containsIndex:(NSUInteger)line.type]): #syntax hurty : wtf is a delegate
            if (line.length > 0): line.type = action
            else: line.type = empty
        
        
        length: int = line.string.length
        unichar charArray[length]
        [line.string getCharacters:charArray]
        
        ## Parse notes
        self.parseNotesFor(line, at=index, oldType=oldType)
        
        ## Omits have stars in them, which can be mistaken for formatting characters.
        ## We store the omit asterisks into the "excluded" index set to avoid this mixup.
        NSMutableIndexSet* excluded = NSMutableIndexSet.new
        
        ## First, we handle notes and omits, which can bleed over multiple lines.
        ## The cryptically named omitOut and noteOut mean that the line bleeds omit/note out on the next line,
        ## while omitIn and noteIn tell that are a part of another omitted/note block.
        
        # previousLine: Line = (index <= self.lines.count and index > 0) ? self.lines[index-1] : None
        previousLine: Line
        if self.lines[index-1]:
            previousLine: Line = (index <= self.lines.count and index > 0)
        else:
            previousLine = None
        
        # syntax hurty : oh my god
        line.omittedRanges = [self rangesOfOmitChars:charArray
                                            ofLength:length
                                            inLine:line
                                    lastLineOmitOut:previousLine.omitOut
                                        saveStarsIn:excluded]
        
        line.boldRanges = [self rangesInChars:charArray
                                    ofLength:length
                                    between:BOLD_CHAR
                                        and:BOLD_CHAR
                                withLength:BOLD_PATTERN_LENGTH
                            excludingIndices:excluded
                                        line:line]
        
        line.italicRanges = [self rangesInChars:charArray
                                    ofLength:length
                                        between:ITALIC_CHAR
                                            and:ITALIC_CHAR
                                    withLength:ITALIC_PATTERN_LENGTH
                            excludingIndices:excluded
                                        line:line]
        
        line.underlinedRanges = [self rangesInChars:charArray
                                        ofLength:length
                                            between:UNDERLINE_CHAR
                                                and:UNDERLINE_CHAR
                                        withLength:UNDERLINE_PATTERN_LENGTH
                                excludingIndices:None
                                            line:line]

        line.macroRanges = [self rangesInChars:charArray
                                    ofLength:length
                                    between:MACRO_OPEN_CHAR
                                        and:MACRO_CLOSE_CHAR
                                    withLength:2
                            excludingIndices:None
                                        line:line]
        
        ## Intersecting indices between bold & italic are boldItalic
        if (line.boldRanges.count and line.italicRanges.count) line.boldItalicRanges = [line.italicRanges indexesIntersectingIndexSet:line.boldRanges].mutableCopy
        else line.boldItalicRanges = NSMutableIndexSet.new
        
        if (line.type == heading) {
            line.sceneNumberRange = [self sceneNumberForChars:charArray ofLength:length]
            
            if (line.sceneNumberRange.length == 0) {
                line.sceneNumber = @""
            } else {
                line.sceneNumber = [line.string substringWithRange:line.sceneNumberRange]
            }
        }
        
        ## set color for outline elements
        if (line.type == heading or line.type == section or line.type == synopse) {
            line.color = [self colorForHeading:line]
        }
        
        ## Markers
        line.marker = [self markerForLine:line]
        
        if (line.isTitlePage) {
            if ([line.string containsString:@":"] and line.string.length > 0) {
                ## If the title doesn't begin with \t or space, format it as key name
                if ([line.string characterAtIndex:0] != ' ' and
                    [line.string characterAtIndex:0] != '\t' ) line.titleRange = NSMakeRange(0, [line.string rangeOfString:@":"].location + 1)
                else line.titleRange = NSMakeRange(0, 0)
            }
        }
    

    ### Parses the line type for given line. It *has* to know its line index.
    ### TODO: This bunch of spaghetti should be refactored and split into smaller functions.
    def LineType)parseLineTypeFor:(Line*)line atIndex:(NSUInteger)index { @synchronized (self) {
        Line *previousLine = (index > 0) ? self.lines[index - 1] : None
        Line *nextLine = (line != self.lines.lastObject and index+1 < self.lines.count) ? self.lines[index+1] : None
        
        bool previousIsEmpty = false
        
        NSString *trimmedString = (line.string.length > 0) ? [line.string stringByTrimmingTrailingCharactersInSet:NSCharacterSet.whitespaceCharacterSet] : @""
        
        ## Check for everything that is considered as empty
        if (previousLine.effectivelyEmpty or index == 0) previousIsEmpty = true
        
        ## Check if this line was forced to become a character cue in editor (by pressing tab)    
        if (line.forcedCharacterCue or _delegate.characterInputForLine == line) {
            line.forcedCharacterCue = NO
            ## 94 = ^ (this is here to avoid issues with Turkish alphabet)
            if (line.lastCharacter == 94) return dualDialogueCharacter
            else return character
        }
        
        ## Handle empty lines first
        if (line.length == 0) {
            if (previousLine.isDialogue or previousLine.isDualDialogue) {
                ## If preceding line is formatted as dialogue BUT it's empty, we'll just return empty.
                if (previousLine.string.length == 0) return empty
                
                ## If preceeded by a character cue, always return dialogue
                if (previousLine.type == character) return dialogue
                elif (previousLine.type == dualDialogueCharacter) return dualDialogue
                
                NSInteger selection = (NSThread.isMainThread) ? self.delegate.selectedRange.location : 0
                
                ## If it's any other dialogue line and we're editing it, return dialogue
                if ((previousLine.isAnyDialogue or previousLine.isAnyParenthetical) and previousLine.length > 0 and (nextLine.length == 0 or nextLine == None) and NSLocationInRange(selection, line.range)) {
                    return (previousLine.isDialogue) ? dialogue : dualDialogue
                }
            }
            
            return empty
        }
        
        ## Check forced elements
        unichar firstChar = [line.string characterAtIndex:0]
        unichar lastChar = line.lastCharacter
        
        ## Also, lets add the first \ as an escape character
        if (firstChar == '\\') [line.escapeRanges addIndex:0]
        
        ## Forced whitespace
        bool containsOnlyWhitespace = line.string.containsOnlyWhitespace; ## Save to use again later
        bool twoSpaces = (firstChar == ' ' and lastChar == ' ' and line.length > 1); ## Contains at least two spaces
        
        if (containsOnlyWhitespace and !twoSpaces) return empty
        
        if ([trimmedString isEqualToString:@"==="]) {
            return pageBreak
        }
        elif (firstChar == '!') {
            ## Action or shot
            if (line.length > 1) {
                unichar secondChar = [line.string characterAtIndex:1]
                if (secondChar == '!') return shot
            }
            return action
        }
        elif (firstChar == '.' and previousIsEmpty) {
            ## '.' forces a heading. Because our American friends love to shoot their guns like we Finnish people love our booze, screenwriters might start dialogue blocks with such "words" as '.44'
            if (line.length > 1) {
                unichar secondChar = [line.string characterAtIndex:1]
                if (secondChar != '.') return heading
            } else {
                return heading
            }
        }
        ## ... and then the rest.
        elif (firstChar == '@'): return character
        elif (firstChar == '>' and lastChar == '<') return centered
        elif (firstChar == '>'): return transitionLine
        elif (firstChar == '~'): return lyrics
        elif (firstChar == '='): return synopse
        elif (firstChar == '#'): return section
        elif (firstChar == '@' and lastChar == 94 and previousIsEmpty) return dualDialogueCharacter
        elif (firstChar == '.' and previousIsEmpty) return heading
        
        ## Title page
        if (previousLine == None or previousLine.isTitlePage) {
            LineType titlePageType = [self parseTitlePageLineTypeFor:line previousLine:previousLine lineIndex:index]
            if (titlePageType != NSNotFound) return titlePageType
        }
        
        ## Check for Transitions
        if (line.length > 2 and line.lastCharacter == ':' and line.string.containsOnlyUppercase and previousIsEmpty) {
            return transitionLine
        }
        
        ## Handle items which require an empty line before them (and we're not forcing character input)
        elif (previousIsEmpty and line.string.length >= 3 and line != self.delegate.characterInputForLine) {
            ## Heading
            NSString* firstChars = [line.string substringToIndex:3].lowercaseString
            
            if ([firstChars isEqualToString:@"int"] or
                [firstChars isEqualToString:@"ext"] or
                [firstChars isEqualToString:@"est"] or
                [firstChars isEqualToString:@"i/e"]) {
                
                ## If it's just under 4 characters, return heading
                if (line.length == 3) {
                    return heading
                } else {
                    ## To avoid words like "international" from becoming headings, the extension HAS to end with either dot, space or slash
                    unichar nextChar = [line.string characterAtIndex:3]
                    if (nextChar == '.' or nextChar == ' ' or nextChar == '/')  return heading
                }
            }
            
            ## Character
            if (line.string.onlyUppercaseUntilParenthesis and !containsOnlyWhitespace and line.noteRanges.firstIndex != 0) {
                ## A character line ending in ^ is a dual dialogue character
                ## (94 = ^, we'll compare the numerical value to avoid mistaking Tuskic alphabet character Ş as ^)
                if (lastChar == 94)
                {
                    ## Note the previous character cue that it's followed by dual dialogue
                    [self makeCharacterAwareOfItsDualSiblingFrom:index]
                    return dualDialogueCharacter
                } else {
                    ## It is possible that this IS NOT A CHARACTER but an all-caps action line
                    if (index + 2 < self.lines.count) {
                        Line* twoLinesOver = (Line*)self.lines[index+2]
                        
                        ## Next line is empty, line after that isn't - and we're not on that particular line
                        if ((nextLine.string.length == 0 and twoLinesOver.string.length > 0) or
                            (nextLine.string.length == 0 and NSLocationInRange(self.delegate.selectedRange.location, nextLine.range))
                            ) {
                            return action
                        }
                    }
                    
                    return character
                }
            }
        }
        
        elif (_delegate.characterInputForLine == line) {
            return character
        }
        
        if ((previousLine.isDialogue or previousLine.isDualDialogue) and previousLine.length > 0) {
            if (firstChar == '(') return (previousLine.isDialogue) ? parenthetical : dualDialogueParenthetical
            return (previousLine.isDialogue) ? dialogue : dualDialogue
        }
        
        ## Fix some parsing mistakes
        if (previousLine.type == action and previousLine.length > 0
            and previousLine.string.onlyUppercaseUntilParenthesis
            and line.length > 0
            and !previousLine.forced
            and [self previousLine:previousLine].type == empty) {
            ## Make all-caps lines with < 2 characters character cues and/or make all-caps actions character cues when the text is changed to have some dialogue follow it.
            ## (94 = ^, we'll use the unichar numerical value to avoid mistaking Turkish alphabet letter 'Ş' as '^')
            if (previousLine.lastCharacter == 94) previousLine.type = dualDialogueCharacter
            else previousLine.type = character
            
            [_changedIndices addIndex:index-1]
            
            if (line.length > 0 and [line.string characterAtIndex:0] == '(') return parenthetical
            else return dialogue
        }
        
        return action
    } }


    def parseTitlePageLineTypeFor(line: Line, previousLine: Line, lineIndex: int) -> LineType:
    
        NSString *key = line.titlePageKey
        
        if (key.length > 0):
            NSString* value = line.titlePageValue
            if (value == None) value = @""
            
            ## Store title page data
            titlePageData: dict = @{ key: [NSMutableArray arrayWithObject:value] }.mutableCopy # syntax hurty: wat
            [_titlePage addObject:titlePageData]
            
            ## Set this key as open (in case there are additional title page lines)
            _openTitlePageKey = key
            
            match key:
                case "title"
                    return titlePageTitle
                case "author" or "authors":
                    return titlePageAuthor
                case credit: 
                    return titlePageCredit
                case "source: 
                    return titlePageSource
                case "contact: 
                    return titlePageContact
                case "contacts: 
                    return titlePageContact
                case "contact info: 
                    return titlePageContact
                case "draft date: 
                    return titlePageDraftDate
                case _: 
                    return titlePageUnknown


                    
        elif (previousLine.isTitlePage):
            key: str = ""
            i: int = index - 1
            while (i >= 0):
                Line *pl = self.lines[i]
                if (pl.titlePageKey.length > 0) {
                    key = pl.titlePageKey
                    break
                }
                i -= 1
            
            if (key.length > 0):
                NSMutableDictionary* dict = _titlePage.lastObject
                [(NSMutableArray*)dict[key] addObject:line.string]
            
            
            return previousLine.type
        
        
        return None
    

    ### Notifies character cue that it has a dual dialogue sibling
    def makeCharacterAwareOfItsDualSiblingFrom(index: int):
        i: int = index - 1
        while (i >= 0) 
            prevLine: Line = self.lines[i]
            
            if (prevLine.type == character):
                prevLine.nextElementIsDualDialogue = YES
                break
            
            if (not prevLine.isDialogueElement and not prevLine.isDualDialogueElement):
                break
            i -= 1
        
    

    def sceneNumberForChars(string: str, length: int) -> range:
        backNumberIndex: int = None
        int note = 0
        
        for(i: int = length - 1; i >= 0; i -= 1):
            unichar c = string[i]
            
            ## Exclude note ranges: [[ Note ]]
            if (c == ' '):
                continue
            if (c == ']' and note < 2) 
                note += 1 
                continue 
            if (c == '[' and note > 0)
                note -= 1 
                continue
            
            ## Inside a note range
            if (note == 2):
                continue
            
            if (backNumberIndex == NSNotFound):
                if (c == '#'):
                    backNumberIndex = i
                else: 
                    break
             else: 
                if (c == '#'):
                    return NSMakeRange(i+1, backNumberIndex-i-1) # syntax hurty: RANGE 
                
            
        
        
        return NSMakeRange(0, 0) # syntax hurty : why return range of 0?
    

    def markerForLine:(Line*)line -> str:
        line.markerRange = (NSRange){0, 0}
        line.marker = ""
        line.markerDescription = ""
        
        NSString *markerColor = ""
        NSString *markerContent = ""
        
        ## Get the last marker. If none is found, just return ""
        marker: list = [line contentAndRangeForLastNoteWithPrefix:@"marker"]
        if (marker == None) return @""
        
        ## The correct way to add a marker is to write [[marker color:Content]], but we'll be gratitious here.
        NSRange range = ((NSNumber*)marker[0]).rangeValue
        NSString* string = marker[1]
        
        if (![string containsString:@":"] and [string containsString:@" "]) {
            ## No colon, let's separate components.
            ## First words will always be "marker", so get the second word and see if it's a color
            NSArray<NSString*>* words = [string componentsSeparatedByString:@" "]
            NSInteger descriptionStart = @"marker ".length
            
            if (words.count > 1) {
                NSString* potentialColor = words[1].lowercaseString
                if ([[self colors] containsObject:potentialColor]) {
                    markerColor = potentialColor
                }
            }
            
            ## Get the content after we've checked for potential color for this marker
            markerContent = [string substringFromIndex:descriptionStart + markerColor.length]
        }
        elif ([string containsString:@":"]) {
            NSInteger l = [string rangeOfString:@":"].location
            markerContent = [string substringFromIndex:l+1]
            
            NSString* left = [string substringToIndex:l]
            NSArray* words = [left componentsSeparatedByString:@" "]
            
            if (words.count > 1) markerColor = words[1]
        }
        
        ## Use default as marker color if no applicable color found
        line.marker = (markerColor.length > 0) ? markerColor.lowercaseString : @"default"
        line.markerDescription = [markerContent stringByTrimmingCharactersInSet:NSCharacterSet.whitespaceCharacterSet]
        line.markerRange = range
        
        return markerColor
    

    ### Finds and sets the color for given outline-level line. Only the last one is used, preceding color notes are ignored.
    def colorForHeading(line: Line)-> str:
    {
        NSArray *colors = self.colors
        
        __block NSString* headingColor = @""
        line.colorRange = NSMakeRange(0, 0)
        
        NSDictionary<NSValue*, NSString*>* noteContents = line.noteContentsAndRanges
        for (NSNumber* key in noteContents.allKeys) {
            NSRange range = key.rangeValue
            NSString* content = noteContents[key].lowercaseString
            
            ## We only want the last color on the line, which DOESN'T bleed out.
            ## The values come from a dictionary, so we can't be sure, so just skip it if it's an earlier one.
            if (line.colorRange.location > range.location or
                (NSMaxRange(range) == line.length and line.noteOut) ) continue
            
            ## We can define a color using both [[color red]] or just [[red]], or #ffffff
            if ([content containsString:@"color "]) {
                ## "color red"
                headingColor = [content substringFromIndex:@"color ".length]
                line.colorRange = range
            }
            elif ([colors containsObject:content] or
                    (content.length == 7 and [content characterAtIndex:0] == '#')) {
                ## pure "red" or "#ff0000"
                headingColor = content
                line.colorRange = range
            }
        }
        
        return headingColor
    }



    '''def NSArray *)beatsFor:(Line *)line {
        if (line.length == 0) return @[]
        
        NSUInteger length = line.string.length
        unichar string[length]
        [line.string.lowercaseString getCharacters:string]; ## Make it lowercase for range enumeration
        
        NSMutableIndexSet *set = [self asymRangesInChars:string ofLength:length between:"[[beat" and:"]]" startLength:@"[[beat".length endLength:2 excludingIndices:None line:line]
        
        NSMutableArray *beats = NSMutableArray.array
        
        [set enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            NSString *storylineStr = [line.string substringWithRange:range]
            NSUInteger loc = @"[[beat".length
            NSString *rawBeats = [storylineStr substringWithRange:(NSRange){ loc, storylineStr.length - loc - 2 }]
            
            NSArray *components = [rawBeats componentsSeparatedByString:@","]
            for (NSString *component in components) {
                Storybeat *beat = [Storybeat line:line scene:None string:component range:range]
                [beats addObject:beat]
            }
            
            [line.beatRanges addIndexesInRange:range]
        }]
        
        return beats
    }
    def NSArray *)storylinesFor:(Line *)line {
        ## This is here for backwards-compatibility with older documents.
        ## These are nowadays called BEATS.
        NSUInteger length = line.string.length
        unichar string[length]
        [line.string.lowercaseString getCharacters:string]; ## Make it lowercase for range enumeration
            
        NSMutableIndexSet *set = [self asymRangesInChars:string ofLength:length between:"[[storyline" and:"]]" startLength:@"[[storyline".length endLength:2 excludingIndices:None line:line]
        
        NSMutableArray *beats = NSMutableArray.array
        
        [set enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            NSString *storylineStr = [line.string substringWithRange:range]
            NSUInteger loc = @"[[storyline".length
            NSString *rawStorylines = [storylineStr substringWithRange:(NSRange){ loc, storylineStr.length - loc - 2 }]
            
            NSArray *components = [rawStorylines componentsSeparatedByString:@","]
            
            for (NSString *component in components) {
                Storybeat *beat = [Storybeat line:line scene:None string:component range:range]
                [beats addObject:beat]
            }
            
            [line.beatRanges addIndexesInRange:range]
        }]
        
        return beats
    }
    '''



    #pragma mark - Title page

    ### Returns the title page lines as string
    def NSString*)titlePageAsString
    {
        NSMutableString *string = NSMutableString.new
        for (Line* line in self.safeLines) {
            if (!line.isTitlePage) break
            [string appendFormat:@"%@\n", line.string]
        }
        return string
    }

    ### Returns just the title page lines
    def NSArray<Line*>*)titlePageLines
    {
        NSMutableArray *lines = NSMutableArray.new
        for (Line* line in self.safeLines) {
            if (!line.isTitlePage) break
            [lines addObject:line]
        }
        
        return lines
    }

    ### Re-parser the title page and returns a weird array structure: `[ { "key": "value }, { "key": "value }, { "key": "value } ]`.
    ### This is because we want to maintain the order of the keys, and though ObjC dictionaries sometimes stay in the correct order, things don't work like that in Swift.
    def NSArray<NSDictionary<NSString*,NSArray<Line*>*>*>*)parseTitlePage
    {
        [self.titlePage removeAllObjects]
        
        ## Store the latest key
        NSString *key = @""
        BeatMacroParser* titlePageMacros = BeatMacroParser.new
        
        ## Iterate through lines and break when we encounter a non- title page line
        for (Line* line in self.safeLines) {
            if (!line.isTitlePage) break
            
            [self resolveMacrosOn:line parser:titlePageMacros]
            
            ## Reset flags
            line.beginsTitlePageBlock = false
            line.endsTitlePageBlock = false
            
            ## Determine if the line is empty
            bool empty = false
            
            ## See if there is a key present on the line ("Title: ..." -> "Title")
            if (line.titlePageKey.length > 0) {
                key = line.titlePageKey.lowercaseString
                if ([key isEqualToString:@"author"]) key = @"authors"
                
                line.beginsTitlePageBlock = true
                
                NSMutableDictionary* titlePageValue = [NSMutableDictionary dictionaryWithDictionary:@{ key: NSMutableArray.new }]
                [self.titlePage addObject:titlePageValue]
                
                ## Add the line into the items of the current line, IF IT'S NOT EMPTY
                NSString* trimmed = [line.string substringFromIndex:line.titlePageKey.length+1].trim
                if (trimmed.length == 0) empty = true
            }
            
            ## Find the correct item in an array of dictionaries
            ## [ { "title": [Line] } , { ... }, ... ]
            NSMutableArray *items = [self titlePageArrayForKey:key]
            if (items == None) continue
            
            ## Add the line if it's not empty
            if (!empty) [items addObject:line]
        }
        
        ## After we've gathered all the elements, lets iterate them once more to determine where blocks end.
        for (NSDictionary<NSString*,NSArray<Line*>*>* element in self.titlePage) {
            NSArray<Line*>* lines = element.allValues.firstObject
            lines.firstObject.beginsTitlePageBlock = true
            lines.lastObject.endsTitlePageBlock = true
        }
        
        return self.titlePage
    }

    ### Returns the lines for given title page key. For example,`Title` would return something like `["My Film"]`.
    def NSMutableArray<Line*>*)titlePageArrayForKey:(NSString*)key
    {
        for (NSMutableDictionary* d in self.titlePage) {
            if ([d.allKeys.firstObject isEqualToString:key]) return d[d.allKeys.firstObject]
        }
        return None
    }


    #pragma mark - Finding character ranges

    def NSMutableIndexSet*)rangesInChars:(unichar*)string ofLength:(NSUInteger)length between:(char*)startString and:(char*)endString withLength:(NSUInteger)delimLength excludingIndices:(NSMutableIndexSet*)excludes line:(Line*)line
    {
        ## Let's use the asym method here, just put in our symmetric delimiters.
        return [self asymRangesInChars:string ofLength:length between:startString and:endString startLength:delimLength endLength:delimLength excludingIndices:excludes line:line]
    }


    # @note This is a confusing method name, but only because it is based on the old rangesInChars method. However, it's basically the same code, but I've put in the ability to seek ranges between two delimiters that are **not** the same, and can have asymmetrical length.  The original method now just calls this using the symmetrical delimiters.

    def NSMutableIndexSet*)asymRangesInChars:(unichar*)string ofLength:(NSUInteger)length between:(char*)startString and:(char*)endString startLength:(NSUInteger)startLength endLength:(NSUInteger)delimLength excludingIndices:(NSMutableIndexSet*)excludes line:(Line*)line
    {
        NSMutableIndexSet* indexSet = NSMutableIndexSet.new
        if (length < startLength + delimLength) return indexSet
        
        NSRange range = NSMakeRange(-1, 0)
        
        for (NSInteger i=0; i <= length - delimLength; i++) {
            ## If this index is contained in the omit character indexes, skip
            if ([excludes containsIndex:i]) continue
            
            ## First check for escape character
            if (i > 0) {
                unichar prevChar = string[i-1]
                if (prevChar == '\\') {
                    [line.escapeRanges addIndex:i - 1]
                    continue
                }
            }
            
            if (range.location == -1) {
                ## Next, see if we can find the whole start string
                bool found = true
                for (NSInteger k=0; k<startLength; k++) {
                    if (i+k >= length) {
                        break
                    } elif (startString[k] != string[i+k]) {
                        found = false
                        break
                    }
                }
                
                if (!found) continue
                
                ## Success! We found a matching string
                range.location = i
                
                ## Pass the starting string
                i += startLength-1
                
            } else {
                ## We have found a range, let's see if we find a closing string.
                bool found = true
                for (NSInteger k=0; k<delimLength; k++) {
                    if (endString[k] != string[i+k]) {
                        found = false
                        break
                    }
                }
                
                if (!found) continue
                
                ## Success, we found a closing string.
                range.length = i + delimLength - range.location
                [indexSet addIndexesInRange:range]
                
                ## Add the current formatting ranges to future excludes
                [excludes addIndexesInRange:(NSRange){ range.location, startLength }]
                [excludes addIndexesInRange:(NSRange){ i, delimLength }]
                
                range.location = -1
                
                ## Move past the ending string
                i += delimLength - 1
            }
        }
        
        return indexSet
    }

    def NSMutableIndexSet*)rangesOfOmitChars:(unichar*)string ofLength:(NSUInteger)length inLine:(Line*)line lastLineOmitOut:(bool)lastLineOut saveStarsIn:(NSMutableIndexSet*)stars
    {
        line.omitIn = lastLineOut
        
        NSMutableIndexSet* indexSet = NSMutableIndexSet.new
        NSRange range = (line.omitIn) ? NSMakeRange(0, 0) : NSMakeRange(NSNotFound, 0)
        
        for (NSUInteger i=0; i < length-1; i++) {
            if (i+1 > length) break
            unichar c1 = string[i]
            unichar c2 = string[i+1]
            
            if (c1 == '/' and c2 == '*' and range.location == NSNotFound) {
                [stars addIndex:i+1]
                range.location = i
                
            } elif (c1 == '*' and c2 == '/') {
                if (range.location == NSNotFound) continue
                
                [stars addIndex:i]
                
                range.length = i - range.location + OMIT_PATTERN_LENGTH
                [indexSet addIndexesInRange:range]
                
                range = NSMakeRange(NSNotFound, 0)
            }
        }
        
        if (range.location != NSNotFound) {
            line.omitOut = true
            [indexSet addIndexesInRange:NSMakeRange(range.location, line.length - range.location + 1)]
        } else {
            line.omitOut = false
        }
        
        return indexSet
    }


    #pragma mark - Fetching Outline Data

    ### Returns a tree structure for the outline. Only top-level elements are included, get the rest using `element.chilren`.
    def NSArray*)outlineTree
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
                for (NSInteger i=0; i<postfixes.count; i++) {
                    s = [NSString stringWithFormat:@"%lu%@", sceneNumber, postfixes[i]]
                    if (![forcedNumbers containsObject:s]) break
                }
            }
            
            if (![oldSceneNumber isEqualToString:s]) {
                if (scene != None) [self.outlineChanges.updated addObject:scene]
            }

            line.sceneNumber = s
            sceneNumber++
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
    def OutlineChanges*)changesInOutline
    {
        ## Refresh the changed outline elements
        for (OutlineScene* scene in self.outlineChanges.updated) {
            [self updateScene:scene at:NSNotFound lineIndex:NSNotFound]
        }
        for (OutlineScene* scene in self.outlineChanges.added) {
            [self updateScene:scene at:NSNotFound lineIndex:NSNotFound]
        }
        
        ## If any changes were made to the outline, rebuild the hierarchy.
        if (self.outlineChanges.hasChanges) [self updateOutlineHierarchy]
        
        OutlineChanges* changes = self.outlineChanges.copy
        self.outlineChanges = OutlineChanges.new
        
        return changes
    }

    ### Returns an array of dictionaries with UUID mapped to the actual string.
    -(NSArray<NSDictionary<NSString*,NSString*>*>*)outlineUUIDs
    {
        NSMutableArray* outline = NSMutableArray.new
        for (OutlineScene* scene in self.outline) {
            [outline addObject:@{
                @"uuid": scene.line.uuid.UUIDString,
                @"string": scene.line.string
            }]
        }
        
        return outline
    }


    #pragma mark - Handling changes to outline
    ## TODO: Maybe make this a separate class, or are we stepping into the dangerous parts of OOP?

    ### Updates the current outline from scratch. Use sparingly.
    def updateOutline
    {
        [self updateOutlineWithLines:self.safeLines]
    }

    ### Updates the whole outline from scratch with given lines.
    def updateOutlineWithLines:(NSArray<Line*>*)lines
    {
        self.outline = NSMutableArray.new
            
        for (NSInteger i=0; i<lines.count; i++) {
            Line* line = self.lines[i]
            if (!line.isOutlineElement) continue
            
            [self updateSceneForLine:line at:self.outline.count lineIndex:i]
        }
        
        [self updateOutlineHierarchy]
    }

    ### Adds an update to this line, but only if needed
    def addUpdateToOutlineIfNeededAt:(NSInteger)lineIndex
    {
        ## Don't go out of range
        if (self.lines.count == 0) return
        elif (lineIndex >= self.lines.count) lineIndex = self.lines.count - 1
        
        Line* line = self.safeLines[lineIndex]

        ## Nothing to update
        if (line.type != synopse and !line.isOutlineElement and line.noteRanges.count == 0 and line.markerRange.length == 0) return

        ## Find the containing outline element and add an update to it
        NSArray* lines = self.safeLines
        
        for (NSInteger i = lineIndex; i >= 0; i--) {
            Line* line = lines[i]
            
            if (line.isOutlineElement) {
                [self addUpdateToOutlineAtLine:line didChangeType:false]
                return
            }
        }
    }


    ### Forces an update to the outline element which contains the given line. No additional checks.
    def addUpdateToOutlineAtLine:(Line*)line didChangeType:(bool)didChangeType
    {
        OutlineScene* scene = [self outlineElementInRange:line.textRange]
        if (scene) [_outlineChanges.updated addObject:scene]
        
        ## In some cases we also need to update the surrounding elements
        if (didChangeType) {
            OutlineScene* previousScene = [self outlineElementInRange:NSMakeRange(line.position - 1, 0)]
            OutlineScene* nextScene = [self outlineElementInRange:NSMakeRange(NSMaxRange(scene.range) + 1, 0)]
            
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
        
        for (NSInteger i=lineIndex; i<self.lines.count; i++) {
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

        for (NSInteger i=0; i<self.outline.count; i++) {
            OutlineScene* scene = self.outline[i]

            if (line.position <= scene.position) {
                index = i
                break
            }
        }

        _changeInOutline = YES

        OutlineScene* scene = [OutlineScene withLine:line delegate:self]
        if (index == NSNotFound) [self.outline addObject:scene]
        else [self.outline insertObject:scene atIndex:index]

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
        for (NSInteger i=0; i<self.outline.count; i++) {
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
    def updateOutlineHierarchy
    {
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
    }

    ### NOTE: This method is used by line preprocessing to avoid recreating the outline. It has some overlapping functionality with `updateOutlineHierarchy` and `updateSceneNumbers:forcedNumbers:`.
    def updateSceneNumbersInLines
    {
        NSMutableArray* autoNumbered = NSMutableArray.new
        NSMutableSet<NSString*>* forcedNumbers = NSMutableSet.new
        for (Line* line in self.safeLines) {
            if (line.type == heading and !line.omitted) {
                if (line.sceneNumberRange.length > 0) [forcedNumbers addObject:line.sceneNumber]
                else [autoNumbered addObject:line]
            }
        }
        
        ### `updateSceneNumbers` supports both `Line` and `OutlineScene` objects.
        [self updateSceneNumbers:autoNumbered forcedNumbers:forcedNumbers]
    }


    #pragma mark - Thread-safety for arrays


    
    ''' `safeLines` and `safeOutline` create a copy of the respective array when called from a background thread.
    
    Because Beat now supports plugins with direct access to the parser, we need to be extra careful with our threads.
    Almost any changes to the screenplay in editor will mutate the `.lines` array, so a background process
    calling something that enumerates the array (ie. `linesForScene:`) will cause an immediate crash.
    
    '''

    def NSArray*)safeLines
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
            ## Return the cached version when possible -- or when we are not in the main thread.
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
    }


    #pragma mark - Convenience methods

    def NSInteger)numberOfScenes
    {
        NSArray *lines = self.safeLines
        NSInteger scenes = 0
        
        for (Line *line in lines) {
            if (line.type == heading) scenes++
        }
        
        return scenes
    }

    def NSArray*)scenes
    {
        NSArray *outline = self.safeOutline; ## Use thread-safe lines
        NSMutableArray *scenes = NSMutableArray.new
        
        for (OutlineScene *scene in outline) {
            if (scene.type == heading) [scenes addObject:scene]
        }
        return scenes
    }

    ### Returns the lines in given scene
    def NSArray*)linesForScene:(OutlineScene*)scene
    {
        ## Return minimal results for non-scene elements
        if (scene == None) return @[]
        elif (scene.type == synopse) return @[scene.line]
        
        NSArray *lines = self.safeLines
            
        NSInteger lineIndex = [self indexOfLine:scene.line]
        if (lineIndex == NSNotFound) return @[]
        
        ## Automatically add the heading line and increment the index
        NSMutableArray *linesInScene = NSMutableArray.new
        [linesInScene addObject:scene.line]
        lineIndex++
        
        ## Iterate through scenes and find the next terminating outline element.
        @try {
            while (lineIndex < lines.count) {
                Line *line = lines[lineIndex]

                if (line.type == heading or line.type == section) break
                [linesInScene addObject:line]
                
                lineIndex++
            }
        }
        @catch (NSException *e) {
            NSLog(@"No lines found")
        }
        
        return linesInScene
    }

    ### Returns the previous line from the given line
    def Line*)previousLine:(Line*)line
    {
        NSInteger i = [self lineIndexAtPosition:line.position]; ## Note: We're using lineIndexAtPosition because it's *way* faster
        
        if (i > 0 and i != NSNotFound) return self.safeLines[i - 1]
        else return None
    }

    ### Returns the following line from the given line
    def Line*)nextLine:(Line*)line
    {
        NSArray* lines = self.safeLines
        NSInteger i = [self lineIndexAtPosition:line.position]; ## Note: We're using lineIndexAtPosition because it's *way* faster
        
        if (i != NSNotFound and i < lines.count - 1) return lines[i + 1]
        else return None
    }

    ### Returns the next outline item of given type
    ### @param type Type of the outline element (heading/section)
    ### @param position Position where to start the search
    def Line*)nextOutlineItemOfType:(LineType)type from:(NSInteger)position
    {
        return [self nextOutlineItemOfType:type from:position depth:NSNotFound]
    }

    ### Returns the next outline item of given type
    ### @param type Type of the outline element (heading/section)
    ### @param position Position where to start the search
    ### @param depth Desired hierarchical depth (ie. 0 for top level objects of this type)
    def Line*)nextOutlineItemOfType:(LineType)type from:(NSInteger)position depth:(NSInteger)depth
    {
        NSInteger idx = [self lineIndexAtPosition:position] + 1
        NSArray* lines = self.safeLines
        
        for (NSInteger i=idx; i<lines.count; i++) {
            Line* line = lines[i]
            
            ## If no depth was specified, we'll just pass this check.
            NSInteger wantedDepth = (depth == NSNotFound) ? line.sectionDepth : depth
            
            if (line.type == type and wantedDepth == line.sectionDepth) {
                return line
            }
        }
        
        return None
    }

    ### Returns the previous outline item of given type
    ### @param type Type of the outline element (heading/section)
    ### @param position Position where to start the seach
    def Line*)previousOutlineItemOfType:(LineType)type from:(NSInteger)position {
        return [self previousOutlineItemOfType:type from:position depth:NSNotFound]
    }
    ### Returns the previous outline item of given type
    ### @param type Type of the outline element (heading/section)
    ### @param position Position where to start the search
    ### @param depth Desired hierarchical depth (ie. 0 for top level objects of this type)
    def Line*)previousOutlineItemOfType:(LineType)type from:(NSInteger)position depth:(NSInteger)depth
    {
        NSInteger idx = [self lineIndexAtPosition:position] - 1
        if (idx == NSNotFound or idx < 0) return None
        
        NSArray* lines = self.safeLines
        
        for (NSInteger i=idx; i>=0; i--) {
            Line* line = lines[i]

            ## If no depth was specified, we'll just pass this check.
            NSInteger wantedDepth = (depth == NSNotFound) ? line.sectionDepth : depth
            
            if (line.type == type and wantedDepth == line.sectionDepth) {
                return line
            }
        }
        
        return None
    }

    def Line *)lineWithUUID:(NSString *)uuid
    {
        for (Line* line in self.lines) {
            if ([line.uuidString isEqualToString:uuid]) return line
        }
        return None
    }


    #pragma mark - Element blocks

    ### Returns the lines for a full dual dialogue block
    def NSArray<NSArray<Line*>*>*)dualDialogueFor:(Line*)line isDualDialogue:(bool*)isDualDialogue {
        if (!line.isDialogue and !line.isDualDialogue) return @[]
        
        NSMutableArray<Line*>* left = NSMutableArray.new
        NSMutableArray<Line*>* right = NSMutableArray.new
        
        NSInteger i = [self indexOfLine:line]
        if (i == NSNotFound) return @[]
        
        NSArray* lines = self.safeLines
        
        while (i >= 0) {
            Line* l = lines[i]
            
            ## Break at first normal character
            if (l.type == character) break
            
            i--
        }
        
        ## Iterate forward
        for (NSInteger j = i; j < lines.count; j++) {
            Line* l = lines[j]
            
            ## Break when encountering a character cue (which is not the first line), and whenever seeing anything else than dialogue.
            if (j > i and l.type == character) break
            elif (!l.isDialogue and !l.isDualDialogue and l.type != empty) break
            
            if (l.isDialogue) [left addObject:l]
            else [right addObject:l]
        }
        
        ## Trim left & right
        while (left.firstObject.type == empty and left.count > 0) [left removeObjectAtIndex:0]
        while (right.lastObject.length == 0 and right.count > 0) [right removeObjectAtIndex:right.count-1]
        
        *isDualDialogue = (left.count > 0 and right.count > 0)
        
        return @[left, right]
    }

    ### Returns the lines for screenplay block in given range.
    def NSArray<Line*>*)blockForRange:(NSRange)range {
        NSMutableArray *blockLines = NSMutableArray.new
        NSArray *lines
        
        if (range.length > 0) lines = [self linesInRange:range]
        else lines = @[ [self lineAtPosition:range.location] ]

        for (Line *line in lines) {
            if ([blockLines containsObject:line]) continue
            
            NSArray *block = [self blockFor:line]
            [blockLines addObjectsFromArray:block]
        }
        
        return blockLines
    }

    ### Returns the lines for full screenplay block associated with this line – a dialogue block, for example.
    def NSArray<Line*>*)blockFor:(Line*)line
    {
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
                h--
            }
        }
        
        ## If the line is part of a dialogue block but NOT a character cue, find the start of the block.
        if ( (line.isDialogueElement or line.isDualDialogueElement) and !line.isAnyCharacter) {
            NSInteger i = blockBegin - 1
            while (i >= 0) {
                ## If the preceding line is not a dialogue element or a dual dialogue element,
                ## or if it has a length of 0, set the block start index accordingly
                Line *precedingLine = lines[i]
                if (!(precedingLine.isDualDialogueElement or precedingLine.isDialogueElement) or precedingLine.length == 0) {
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
            
            i++
        }
        
        return block
    }

    def NSRange)rangeForBlock:(NSArray<Line*>*)block
    {
        NSRange range = NSMakeRange(block.firstObject.position, NSMaxRange(block.lastObject.range) - block.firstObject.position)
        return range
    }


    #pragma mark - Line position lookup and convenience methods

    ## Cached line for lookup
    NSUInteger prevLineAtLocationIndex = 0

    ### Returns line at given POSITION, not index.
    def Line*)lineAtIndex:(NSInteger)position
    {
        return [self lineAtPosition:position]
    }


    ''' Returns the index in lines array for given line. This method might be called multiple times, so we'll cache the result.
    This is a *very* small optimization, we're talking about `0.000001` vs `0.000007`. It's many times faster, but doesn't actually have too big of an effect.
    '''
    NSInteger previousIndex = NSNotFound
    def NSUInteger)indexOfLine:(Line*)line
    {
        NSArray *lines = self.safeLines
        
        if (previousIndex < lines.count and previousIndex >= 0) {
            if (line == (Line*)lines[previousIndex]) {
                return previousIndex
            }
        }
        
        NSInteger index = [lines indexOfObject:line]
        previousIndex = index

        return index
    }

    NSInteger previousSceneIndex = NSNotFound
    def NSUInteger)indexOfScene:(OutlineScene*)scene
    {
        NSArray *outline = self.safeOutline
        
        if (previousSceneIndex < outline.count and previousSceneIndex >= 0) {
            if (scene == outline[previousSceneIndex]) return previousSceneIndex
        }
        
        NSInteger index = [outline indexOfObject:scene]
        previousSceneIndex = index

        return index
    }


    '''This method finds an element in array that statisfies a certain condition, compared in the block. To optimize the search, you should provide `searchOrigin`  and the direction.
    @returns Returns either the found element or None if none was found.
    @param array The array to be searched.
    @param searchOrigin Starting index of the search, preferrably the latest result you got from this same method.
    @param descending Set the direction of the search: true for descending, false for ascending.
    @param cacheIndex Pointer for retrieving the index of the found element. Set to NSNotFound if the result is None.
    @param compare The block for comparison, with the inspected element as argument. If the element statisfies your conditions, return true.
    '''
    def id _Nullable)findNeighbourIn:(NSArray*)array origin:(NSUInteger)searchOrigin descending:(bool)descending cacheIndex:(NSUInteger*)cacheIndex block:(BOOL (^)(id item, NSInteger idx))compare
    {
        ## Don't go out of range
        if (NSLocationInRange(searchOrigin, NSMakeRange(-1, array.count))) {
            ''' Uh, wtf, how does this work?
                We are checking if the search origin is in range from -1 to the full array count,
                so I don't understand how and why this could actually work, and why are we getting
                the correct behavior. The magician surprised themself, too.
            '''
            return None
        }
        elif (array.count == 0) return None
        
        NSInteger i = searchOrigin
        NSInteger origin = (descending) ? i - 1 : i + 1
        if (origin == -1) origin = array.count - 1
        
        bool stop = NO
        
        do {
            if (!descending) {
                i++
                if (i >= array.count) i = 0
            } else {
                i--
                if (i < 0) i = array.count - 1
            }
                    
            id item = array[i]
            
            if (compare(item, i)) {
                *cacheIndex = i
                return item
            }
            
            ## We have looped around the array (unsuccessfuly)
            if (i == searchOrigin or origin == -1) {
                NSLog(@"Failed to find match for %@ - origin: %lu / searchorigin: %lu  -- %@", self.lines[searchOrigin], origin, searchOrigin, compare)
                break
            }
            
        } while (stop != YES)
        
        *cacheIndex = NSNotFound
        return None
    }



    ''' This method returns the line index at given position in document. It uses a cyclical lookup, so the method won't iterate through all the lines every time.
    Instead, it first checks the line it returned the last time, and after that, starts to iterate through lines from its position and given direction. Usually we can find
    the line with 1-2 steps, and as we're possibly iterating through thousands and thousands of lines, it's much faster than finding items by their properties the usual way.
    '''
    def NSUInteger)lineIndexAtPosition:(NSUInteger)position
    {
        NSArray* lines = self.safeLines
        NSUInteger actualIndex = NSNotFound
        NSInteger lastFoundPosition = 0
        
        ## First check if we are still on the same line as before
        if (NSLocationInRange(_lastLineIndex, NSMakeRange(0, lines.count))) {
            Line* lastEdited = lines[_lastLineIndex]
            lastFoundPosition = lastEdited.position
            
            if (NSLocationInRange(position, lastEdited.range)) {
                return _lastLineIndex
            }
        }
        
        ## Cyclical array lookup from the last found position
        Line* result = [self findNeighbourIn:lines origin:_lastLineIndex descending:(position < lastFoundPosition) cacheIndex:&actualIndex block:^BOOL(id item, NSInteger idx) {
            Line* l = item
            return NSLocationInRange(position, l.range)
        }]
        
        if (result != None) {
            _lastLineIndex = actualIndex
            _lastEditedLine = result
            
            return actualIndex
        } else {
            return (self.lines.count > 0) ? self.lines.count - 1 : 0
        }
    }

    ### Returns the closest printable (visible) line for given line
    def Line*)closestPrintableLineFor:(Line*)line
    {
        NSArray <Line*>* lines = self.lines
        
        NSInteger i = [lines indexOfObject:line]
        if (i == NSNotFound) return None
        
        while (i >= 0) {
            Line *l = lines[i]
            
            if (l.type == action and i > 0) {
                ## This might be part of a joined action paragraph block
                Line *prev = lines[i-1]
                if (prev.type == empty and !l.isInvisible) return l
            } elif (!l.isInvisible) {
                return l
            }
            i--
        }
        
        return None
    }

    ### Rerturns the line object at given position
    ### (btw, why aren't we using the other method?)
    def Line*)lineAtPosition:(NSInteger)position
    {
        ## Let's check the cached line first
        if (NSLocationInRange(position, _prevLineAtLocation.range)) return _prevLineAtLocation
        
        NSArray *lines = self.safeLines; ## Use thread safe lines for this lookup
        if (prevLineAtLocationIndex >= lines.count) prevLineAtLocationIndex = 0
        
        ## Quick lookup for first object
        if (position == 0) return lines.firstObject
        
        ## We'll use a circular lookup here.
        ## It's HIGHLY possible that we are not just randomly looking for lines,
        ## but that we're looking for close neighbours in a for loop.
        ## That's why we'll either loop the array forward or backward to avoid
        ## unnecessary looping from beginning, which soon becomes very inefficient.
        
        NSUInteger cachedIndex
        
        bool descending = NO
        if (_prevLineAtLocation and position < _prevLineAtLocation.position) {
            descending = YES
        }
            
        Line *line = [self findNeighbourIn:lines origin:prevLineAtLocationIndex descending:descending cacheIndex:&cachedIndex block:^BOOL(id item, NSInteger idx) {
            Line *l = item
            if (NSLocationInRange(position, l.range)) return YES
            else return NO
        }]
        
        if (line) {
            _prevLineAtLocation = line
            prevLineAtLocationIndex = cachedIndex
            return line
        }
        
        return None
    }

    ### Returns the lines in given range (even overlapping)
    def NSArray*)linesInRange:(NSRange)range
    {
        NSArray *lines = self.safeLines
        NSMutableArray *linesInRange = NSMutableArray.array
        
        for (Line* line in lines) {
            if ((NSLocationInRange(line.position, range) or
                NSLocationInRange(range.location, line.textRange) or
                NSLocationInRange(range.location + range.length, line.textRange)) and
                NSIntersectionRange(range, line.textRange).length > 0) {
                [linesInRange addObject:line]
            }
        }
        
        return linesInRange
    }

    ### Returns the scenes which intersect with given range.
    def NSArray*)scenesInRange:(NSRange)range
    {
        NSMutableArray *scenes = NSMutableArray.new
        NSArray *outline = self.safeOutline; ## Thread-safe outline
        
        ## When length is zero, return just the scene at the beginning of range
        if (range.length == 0) {
            OutlineScene* scene = [self sceneAtPosition:range.location]
            return (scene != None) ? @[scene] : @[]
        }
        
        for (OutlineScene* scene in outline) {
            NSRange intersection = NSIntersectionRange(range, scene.range)
            if (intersection.length > 0) [scenes addObject:scene]
        }
        
        return scenes
    }

    ### Returns a scene which contains the given character index (position). An alias for `sceneAtPosition` for legacy compatibility.
    def OutlineScene*)sceneAtIndex:(NSInteger)index { return [self sceneAtPosition:index]; }

    ### Returns a scene which contains the given position
    def OutlineScene*)sceneAtPosition:(NSInteger)index
    {
        for (OutlineScene *scene in self.safeOutline) {
            if (NSLocationInRange(index, scene.range) and scene.line != None) return scene
        }
        return None
    }

    ### Returns all scenes contained by this section. You should probably use `OutlineScene.children` though.
    ### - note: Legacy compatibility. Remove when possible.
    def NSArray*)scenesInSection:(OutlineScene*)topSection
    {
        if (topSection.type != section) return @[]
        return topSection.children
    }

    ### Returns the scene with given number (string)
    def OutlineScene*)sceneWithNumber:(NSString*)sceneNumber
    {
        for (OutlineScene *scene in self.outline) {
            if ([scene.sceneNumber.lowercaseString isEqualToString:sceneNumber.lowercaseString]) {
                return scene
            }
        }
        return None
    }



    #pragma mark - Line identifiers (UUIDs)

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
    def setIdentifiers:(NSArray*)uuids
    {
        for (NSInteger i = 0; i < uuids.count; i++) {
            id item = uuids[i]
            ## We can have either strings or real UUIDs in the array. Make sure we're using the correct type.
            NSUUID *uuid = ([item isKindOfClass:NSString.class]) ? [NSUUID.alloc initWithUUIDString:item] : item
                    
            if (i < self.lines.count and uuid != None) {
                Line *line = self.lines[i]
                line.uuid = uuid
            }
        }
    }

    ### Sets the given UUIDs to each outline element at the same index
    def setIdentifiersForOutlineElements:(NSArray*)uuids:
        for (NSInteger i=0; i<self.outline.count; i++) {
            if (i >= uuids.count) break
            
            OutlineScene* scene = self.outline[i]
            NSDictionary* item = uuids[i]
            
            NSString* uuidString = item[@"uuid"]
            NSString* string = item[@"string"]
            
            if ([scene.string.lowercaseString isEqualToString:string.lowercaseString]) {
                NSUUID* uuid = [NSUUID.alloc initWithUUIDString:uuidString]
                scene.line.uuid = uuid
            }
        }




    #pragma mark - Note parsing

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

    def parseNotesFor:(Line*)line at:(NSInteger)lineIndex oldType:(LineType)oldType
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

        __block NSRange noteRange = NSMakeRange(NSNotFound, 0)
        
        for (NSInteger i = 0; i < line.length - 1; i++) {
            unichar c1 = chrs[i]
            unichar c2 = chrs[i + 1]
            
            if (c1 == '[' and c2 == '[') {
                ## A note begins
                noteRange.location = i
            }
            elif (c1 == ']' and c2 == ']' and noteRange.location != NSNotFound) {
                ## We are terminating a normal note
                noteRange.length = i + 2 - noteRange.location
                NSRange contentRange = NSMakeRange(noteRange.location + 2, noteRange.length - 4)
                NSString* content = [line.string substringWithRange:contentRange]
                
                BeatNoteData* note = [BeatNoteData withNote:content range:noteRange]
                [line.noteData addObject:note]
                [line.noteRanges addIndexesInRange:noteRange]
                
                noteRange = NSMakeRange(NSNotFound, 0)
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
    # !? fucntion too much big ?
    def parseNoteOutFrom:(NSInteger)lineIndex positionInLine:(NSInteger)position
    {
        if (lineIndex == NSNotFound) return
        
        NSMutableIndexSet* affectedLines = NSMutableIndexSet.new
        bool cancel = false; ## Check if we should remove the note block from existence
        Line* lastLine
        
        for (NSInteger i=lineIndex; i<_lines.count; i++) {
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
                range = NSMakeRange(p, l.length - p)
                
                ## Find color in the first line of a note
                if (!cancel) {
                    NSString* firstNote = [l.string substringWithRange:range]
                    NSInteger cIndex = [firstNote rangeOfString:@":"].location
                    if (cIndex != NSNotFound) color = [firstNote substringWithRange:NSMakeRange(2, cIndex - 2 )]
                }
                
            } elif ([l canTerminateNoteBlockWithActualIndex:&p]) {
                ## Last line
                range = NSMakeRange(0, p+2)
            } else {
                ## Line in the middle
                range = NSMakeRange(0, l.length)
            }
            
            if (range.location == NSNotFound or range.length == NSNotFound) return
            
            if (cancel) {
                [_changedIndices addIndex:idx]
                
                if (!l.noteIn and idx != affectedLines.firstIndex and l.type != empty) {
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
                
            
                if (!cancel) {
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
        [noteContent setString:[noteContent substringWithRange:NSMakeRange(2, noteContent.length - 4 )]]
        
        BeatNoteData* note = [BeatNoteData withNote:noteContent range:NSMakeRange(position, firstLine.length - position)]
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
        
        for (NSInteger i=idx; i>=0; i--) {
            Line* l = lines[i]
            if (l.type == empty and i < idx) break;   ## Stop if we're not in a block
            
            unichar chrs[l.length]
            [l.string getCharacters:chrs]
            
            for (NSInteger k=l.string.length-1; k>=0; k--) {
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
            
        return noteStartLine



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

    def report()
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
        }





 '''
 Thank you, Hendrik Noeller, for making Beat possible.
 Without your massive original work, any of this had never happened.
 '''
 
