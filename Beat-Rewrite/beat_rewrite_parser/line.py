##
##  Line.m
##  Beat
##
##  Created by Hendrik Noeller on 01.04.16.
##  Copyright © 2016 Hendrik Noeller. All rights reserved.
##  (most) parts copyright © 2019-2021 Lauri-Matti Parppei / Lauri-Matti Parppei. All Rights reserved.

# Line Object

# Each parsed line is represented by a `Line` object, which holds the string, formatting ranges and other metadata. 

import uuid
from enum import Enum, auto
from dataclasses import dataclass

from helper_funcs import *
from helper_dataclasses import LocationAndLength as loc_len

from parser_data_classes.formatting_characters import FormattingCharacters

# from screenplay_data.beat_export_settings import BeatExportSettings

### Line type enum
### Some types are only used in static parsing and/or exporting, such as `more` and `dualDialogueMore`. 
### `BeatFormatting` class also introduces supplementary types for internal use.

@dataclass
class LineType(Enum):
    (
        empty,
        section,
        synopse,
        titlePageTitle,
        titlePageAuthor,
        titlePageCredit,
        titlePageSource,
        titlePageContact,
        titlePageDraftDate,
        titlePageUnknown,
        heading,
        action,
        character,
        parenthetical,
        dialogue,
        dualDialogueCharacter,
        dualDialogueParenthetical,
        dualDialogue,
        transitionLine,
        lyrics,
        pageBreak,
        centered,
        shot,
        more,               ### fake element for exporting
        dualDialogueMore,   ### fake element for exporting
        typeCount           ### This is the the max number of line types, used in `for` loops and enumerations, can be ignored
        ) = range(0, 26) 
    
# TODO: determine if we can or should separate the Line class into two: LineBehavior and LineData class

class Line:

    ### Line type (integer enum)
    type: LineType
    ### String content of this line
    string: str
    ### The string value when this line was initialized
    originalString: str
    ### Position (starting index) )in document
    position: int
    ### Getter for string length
    length: int

    ### If the line is an outline element (section/heading) this value contains the section depth
    sectionDepth: int
    ### If the line is an outline element, this value contains the scene number, but only after the outline structure has been updated
    sceneNumber: str
    ### Color for outline element (`nil` or empty if no color is set)
    color: str
    ### This line was forced to be a character cue in editor
    forcedCharacterCue: bool = False
 
    # @interface Line() # syntax hurty : these 3 properties are private properties I guess
    oldHash: int
    cachedString: str
    beatRangesAndContents: dict
    lt: LineType # ? does this need to be here idk lol

    # the above props were part of an interface, now moved into the class
    
    BeatFormattingKeyNone = "BeatNoFormatting"
    BeatFormattingKeyItalic = "BeatItalic"
    BeatFormattingKeyBold = "BeatBold"
    BeatFormattingKeyBoldItalic = "BeatBoldItalic"
    BeatFormattingKeyUnderline = "BeatUnderline"

    string: str
    type: LineType
    position: int
    formattedAs: any
    parser: any
    
    boldRanges: set
    italicRanges: set
    underlinedRanges: set
    boldItalicRanges: set
    strikeoutRanges: set
    noteRanges: set
    omittedRanges: set
    escapeRanges: set
    removalSuggestionRanges: set
    _uuid: uuid.uuid4()
    
    originalString: str

    #pragma mark - Initialization

    def __init__(self, 
                       string: str = "", 
                       position: int = 0, 
                       parser: any = None, # parser takes in a type of LineDelegate ?
                       type: any = LineType.empty, # this is wrong, this is not how type hinting should work
                       ): 

        if string is None:
            string = ""
        
        self.string = string
        self.type = type
        self.position = position
        self.formattedAs = -1
        self.parser = parser
        
        self.boldRanges = set()
        self.italicRanges = set()
        self.underlinedRanges = set()
        self.boldItalicRanges = set()
        self.strikeoutRanges = set()
        self.noteRanges = set()
        self.omittedRanges = set()
        self.escapeRanges = set()
        self.removalSuggestionRanges = set()
        self._uuid = uuid.uuid4()
        
        self.originalString = string
        
        # return self
    

    '''### Use this ONLY for creating temporary lines while paginating.
    def Line*)initWithString:(NSString *)string type:(LineType)type pageSplit:(bool)pageSplit {
        self = [super init]
        if (self) {
            _string = string
            _type = type
            _unsafeForPageBreak = True
            _formattedAs = -1
            _uuid = NSUUID.UUID
            _nextElementIsDualDialogue = False
            
            _beginsNewParagraph = False
            
            if (pageSplit) [self resetFormatting]
        }
        return self
    }'''
 
    #pragma mark - Shorthands  --- BACKBURNER

    '''

    ### Use this ONLY for creating temporary lines while paginating
    def withString(self, string: str, type: LineType, pageSplit: bool):
        return self.initWithString(string=string, type=type, pageSplit=True)
    
    # why this function?
    def markupCharacters() -> list:
        return [".", "@", "~", "!"]'''
    

    #pragma mark - Type

    ### Used by plugin API to create constants for matching line types to enumerated integer values
    def typeDictionary(self) -> dict:
        types: dict = {}
        
        max: int = LineType.typeCount # not sure if LineType.typeCount is correct this may be a local variable or smth
        for i in range(0, max):
            type = i
            typeName = self.typeName(type)
            
            types[typeName] = i
        
        
        return types
    

    def typeName(self, type: LineType) -> str:
        match type:
            case LineType.empty:
                return "empty"
            case LineType.section:
                return "section"
            case LineType.synopse:
                return "synopsis"
            case LineType.titlePageTitle:
                return "titlePageTitle"
            case LineType.titlePageAuthor:
                return "titlePageAuthor"
            case LineType.titlePageCredit:
                return "titlePageCredit"
            case LineType.titlePageSource:
                return "titlePageSource"
            case LineType.titlePageContact:
                return "titlePageContact"
            case LineType.titlePageDraftDate:
                return "titlePageDraftDate"
            case LineType.titlePageUnknown:
                return "titlePageUnknown"
            case LineType.heading:
                return "heading"
            case LineType.action:
                return "action"
            case LineType.character:
                return "character"
            case LineType.parenthetical:
                return "parenthetical"
            case LineType.dialogue:
                return "dialogue"
            case LineType.dualDialogueCharacter:
                return "dualDialogueCharacter"
            case LineType.dualDialogueParenthetical:
                return "dualDialogueParenthetical"
            case LineType.dualDialogue:
                return "dualDialogue"
            case LineType.transitionLine:
                return "transition"
            case LineType.lyrics:
                return "lyrics"
            case LineType.pageBreak:
                return "pageBreak"
            case LineType.centered:
                return "centered"
            case LineType.more:
                return "more"
            case LineType.dualDialogueMore:
                return "dualDialogueMore"
            case LineType.shot:
                return "shot"
            case LineType.typeCount:
                return ""

    def getTypeName(self) -> str:
        return self.typeName(self.type)


    ### Returns line type as string
    def typeAsString(self, type: LineType):
        match type:
            case LineType.empty:
                return "Empty"
            case LineType.section:
                return "Section"
            case LineType.synopse:
                return "Synopse"
            case LineType.titlePageTitle:
                return "Title Page Title"
            case LineType.titlePageAuthor:
                return "Title Page Author"
            case LineType.titlePageCredit:
                return "Title Page Credit"
            case LineType.titlePageSource:
                return "Title Page Source"
            case LineType.titlePageContact:
                return "Title Page Contact"
            case LineType.titlePageDraftDate:
                return "Title Page Draft Date"
            case LineType.titlePageUnknown:
                return "Title Page Unknown"
            case LineType.heading:
                return "Heading"
            case LineType.action:
                return "Action"
            case LineType.character:
                return "Character"
            case LineType.parenthetical:
                return "Parenthetical"
            case LineType.dialogue:
                return "Dialogue"
            case LineType.dualDialogueCharacter:
                return "DD Character"
            case LineType.dualDialogueParenthetical:
                return "DD Parenthetical"
            case LineType.dualDialogue:
                return "DD Dialogue"
            case LineType.transitionLine:
                return "Transition"
            case LineType.lyrics:
                return "Lyrics"
            case LineType.pageBreak:
                return "Page Break"
            case LineType.centered:
                return "Centered"
            case LineType.shot:
                return "Shot"
            case LineType.more:
                return "More"
            case LineType.dualDialogueMore:
                return "DD More"
            case LineType.typeCount:
                return ""

    ### Retuns current line type as string
    def getTypeAsString(self):
    
        return self.typeAsString(self.type)
    

    ### Returns line type for string
    def typeFromName(name: str) -> LineType:
    
        match type:
            case "Empty":
                return LineType.empty
            case "Section":
                return LineType.section
            case "Synopse":
                return LineType.synopse
            case "Title Page Title":
                return LineType.titlePageTitle
            case "Title Page Author":
                return LineType.titlePageAuthor
            case "Title Page Credit":
                return LineType.titlePageCredit
            case "Title Page Source":
                return LineType.titlePageSource
            case "Title Page Contact":
                return LineType.titlePageContact
            case "Title Page Draft Date":
                return LineType.titlePageDraftDate
            case "Title Page Unknown":
                return LineType.titlePageUnknown
            case "Heading":
                return LineType.heading
            case "Action":
                return LineType.action
            case "Character":
                return LineType.character
            case "Parenthetical":
                return LineType.parenthetical
            case "Dialogue":
                return LineType.dialogue
            case "DD Character":
                return LineType.dualDialogueCharacter
            case "DD Parenthetical":
                return LineType.dualDialogueParenthetical
            case "DD Dialogue":
                return LineType.dualDialogue
            case "Transition":
                return LineType.transitionLine
            case "Lyrics":
                return LineType.lyrics
            case "Page Break":
                return LineType.pageBreak
            case "Centered":
                return LineType.centered
            case "Shot":
                return LineType.shot
            case "More":
                return LineType.more
            case "DD More":
                return LineType.dualDialogueMore
            case _:
                return LineType.typeCount
    

    #pragma mark - Thread-safe getters --- BACKBURNER --- COMPREHENSION ISSUE

    '''### Length of the string
    def length() -> int:
        @synchronized (self.string) {
            return self.string.length
        }
    

    ### Range for the full line (incl. line break)
    -(NSRange)range
    {
        @synchronized (self) {
            return NSMakeRange(self.position, self.length + 1)
        }
    }

    ### Range for text content only (excl. line break)
    -(NSRange)textRange
    {
        @synchronized (self) {
            return NSMakeRange(self.position, self.length)
        }
    }

    ### Returns the line position in document
    -(NSInteger)position
    {
        if (_representedLine == nil) {
            @synchronized (self) {
                return _position
            }
        } else {
            return _representedLine.position
        }
    }'''

    #pragma mark - Delegate methods --- BACKBURNER --- COMPREHENSION ISSUE

    ### Returns the index of this line in the parser.
    ### @warning VERY slow, this should be fixed to conform with the new, circular search methods.
    '''def NSUInteger)index {
        if (not self.parser) return NSNotFound
        return [self.parser.lines indexOfObject:self] # ?? syntax hurty
    }'''

    #pragma mark - String Modification methods --- BACKBURNER --- SHIFT RESPONSIBILITY

    '''def stringForDisplay(self) -> str:
        if (not self.omitted):
            return [self.stripFormatting stringByTrimmingCharactersInSet:NSCharacterSet.whitespaceCharacterSet]
        else:
            Line *line = self.clone
            [line.omittedRanges removeAllIndexes]
            return [line.stripFormatting stringByTrimmingCharactersInSet:NSCharacterSet.whitespaceCharacterSet]
        
    

    ### @warning Legacy method. Use `line.stripFormatting`
    def NSString*)textContent {
        return self.stripFormatting
    }

    ### Returns the last character as `unichar`
    # -- deleted --

    ### Returns `true` if the stored original content is equal to current string
    def matchesOriginal(self) -> bool:
        return self.string == self.originalString'''
    

    #pragma mark - Strip formatting --- BACKBURNER --- SHIFT RESPONSIBILITY

    ### Strip any Fountain formatting from the line
    ### ## Strip any Fountain formatting from the line
    '''
    def stripFormatting(self) -> str:
        return self.stripFormattingWithSettings(None)
    
    def stripFormattingWithSettings(self, settings: BeatExportSettings) -> str:
    
        contentRanges: list = self.contentRanges
        if (settings.printNotes):
            contentRanges.append(self.noteRanges)# ?? syntax hurty

        __block NSMutableString *content = NSMutableString.string ## ?? syntax hurty
        macros: list = self.resolvedMacros
        
        [contentRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            ## Let's make sure we don't have bad data here (can happen in some multithreaded instances)
            if (NSMaxRange(range) > self.string.length) {
                range.length = self.string.length - NSMaxRange(range)
                if (range.length <= 0) return
            }
            
            strippedContent: str = ""

            ## We need to replace macros. This is a more efficient way than using attributed strings.
            for (NSValue *macroRange in macros) {
                NSRange replacementRange = macroRange.rangeValue
                NSString *macroValue = macros[macroRange]
                
                ## Check if the replacement range intersects with the current range
                NSRange intersectionRange = NSIntersectionRange(range, replacementRange)
                
                if (intersectionRange.length > 0) {
                    ## There is an intersection, so replace the intersecting part with the replacement string
                    if (intersectionRange.location > range.location) {
                        NSRange prefixRange = NSMakeRange(range.location, intersectionRange.location - range.location)
                        [strippedContent appendString:[self.string substringWithRange:prefixRange]]
                    }
                    
                    [strippedContent appendString:macroValue]
                    
                    ## Update the range for the next iteration
                    NSInteger remainder = NSMaxRange(range) - NSMaxRange(intersectionRange)
                    range.location = NSMaxRange(intersectionRange)
                    range.length = remainder
                }
            }
            
            ## Append any remaining content after replacements
            if (range.location < NSMaxRange(_range)):
                remainingRange: range = NSMakeRange(range.location, NSMaxRange(range) - range.location)
                strippedContent += self.string[:remainingRange] # NOTE: syntax hurty: RANGE
            
            
            [content appendString:strippedContent]
        }]
        
        return content
    

    ### Returns a string with notes removed
    def stripNotes() -> str:
        __block NSMutableString *string = [NSMutableString stringWithString:self.string]
        __block NSUInteger offset = 0
        
        [self.noteRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            if (range.location - offset + range.length > string.length) {
                range = NSMakeRange(range.location, string.length - range.location - offset)
            }
            
            @try {
                [string replaceCharactersInRange:NSMakeRange(range.location - offset, range.length) withString:@""]
            }
            @catch (NSException* exception) {
                NSLog(@"cleaning out of range: %@ / (%lu, %lu) / offset %lu", self.string, range.location, range.length, offset)
            }
            @finally {
                offset += range.length
            }
        }]
        
        return string
    

    ### Returns a string with the scene number stripped
    def stripSceneNumber(self) -> str:
        result: str = [self.string stringByReplacingOccurrencesOfString:[NSString stringWithFormat:@"#%@#", self.sceneNumber] withString:@"" options:NSCaseInsensitiveSearch range:NSMakeRange(0, self.string.length)]
        return [result stringByTrimmingCharactersInSet:NSCharacterSet.whitespaceCharacterSet]'''
    
    #pragma mark - Element booleans
    

    def canBeSplitParagraph(self) -> bool:
        return (
            (self.type == LineType.action) 
            or (self.type == LineType.lyrics) 
            or (self.type == LineType.centered))
    
    ### Returns TRUE for scene, section and synopsis elements
    def isOutlineElement(self) -> bool:
        return (self.type == LineType.heading) or (self.type == LineType.section)
    

    ### Returns TRUE for any title page element
    # NOTE: maybe rename this func to isTitlePageElement to be more explicit
    def isTitlePage(self) -> bool:
        return (self.type == LineType.titlePageTitle or
                self.type == LineType.titlePageCredit or
                self.type == LineType.titlePageAuthor or
                self.type == LineType.titlePageDraftDate or
                self.type == LineType.titlePageContact or
                self.type == LineType.titlePageSource #or
                #self.type == LineType.titlePageUnknown
                )
    

    ### Checks if the line is completely non-printing __in the eyes of parsing__.
    def isInvisible(self) -> bool:
        return (self.omitted 
                or self.type == LineType.section 
                or self.type == LineType.synopse 
                or self.isTitlePage)
    

    ### Returns TRUE if the line type is forced
    def forced(self) -> bool:
        return (self.numberOfPrecedingFormattingCharacters > 0)
    


    #pragma mark Dialogue

    ### Returns `true` for ANY SORT OF dialogue element, including dual dialogue
    def isAnySortOfDialogue(self) -> bool:
        return (self.isDialogue or self.isDualDialogue)
    

    ### Returns `true` for any dialogue element, including character cue
    def isDialogue(self) -> bool:
        return (self.type == LineType.character 
                or self.type == LineType.parenthetical 
                or self.type == LineType.dialogue 
                or self.type == LineType.more)
    

    ### Returns `true` for dialogue block elements, excluding character cues
    def isDialogueElement(self) -> bool:
        ## Is SUB-DIALOGUE element
        return (self.type == LineType.parenthetical or self.type == LineType.dialogue)
    

    ### Returns `true` for any dual dialogue element, including character cue
    def isDualDialogue(self) -> bool: 
        return (self.type == LineType.dualDialogue 
                or self.type == LineType.dualDialogueCharacter 
                or self.type == LineType.dualDialogueParenthetical 
                or self.type == LineType.dualDialogueMore)
    

    ### Returns `true` for dual dialogue block elements, excluding character cues
    def isDualDialogueElement(self) -> bool: 
        return (self.type == LineType.dualDialogueParenthetical 
                or self.type == LineType.dualDialogue 
                or self.type == LineType.dualDialogueMore)
    

    ### Returns `true` for ANY character cue (single or dual)
    def isAnyCharacter(self) -> bool: 
        return (self.type == LineType.character 
                or self.type == LineType.dualDialogueCharacter)
    

    ### Returns `true` for ANY parenthetical line (single or dual)
    def isAnyParenthetical(self) -> bool: 
        return (self.type == LineType.parenthetical 
                or self.type == LineType.dualDialogueParenthetical)
    

    ### Returns `true` for ANY dialogue line (single or dual)
    def isAnyDialogue(self) -> bool:
    
        return (self.type == LineType.dialogue 
                or self.type == LineType.dualDialogue)
    
    #pragma mark Omissions & notes
    ## What a silly mess. TODO: Please fix this.

    ### Returns `true` for ACTUALLY omitted lines, so not only for effectively omitted. This is a silly thing for legacy compatibility.
    '''def isOmitted(self) -> bool:
        return (self.omittedRanges.count >= self.string.length)
    

    ### Returns `true` if the line is omitted, kind of. This is a silly mess because of historical reasons.
    ### @warning This also includes lines that have 0 length or are completely a note, meaning the method will return True for empty and/or note lines too.
    def omitted(self) -> bool:
        return (self.omittedRanges.count + self.noteRanges.count >= self.string.length)


    # Returns true for a line which is a note. Should be used only in conjuction with .omited to check that, yeah, it's omited but it's a note:
    # `if (line.omited && !line.note) { ... }`
    # 
    # Checked using trimmed length, to make lines like `  [[note]]` be notes.

    def note(self) -> bool:
        return (self.noteRanges.count >= self.trimmed.length  
                and self.noteRanges.count  
                and self.string.length >= 2)


    ### Returns `true` if the note is able to succesfully terminate a multi-line note block (contains `]]`)
    def canTerminateNoteBlock(self) -> bool: 
        return self.canTerminateNoteBlockWithActualIndex(None)
    
    def canTerminateNoteBlockWithActualIndex(self, position: int) -> bool:
    
        if (self.length > 30000): 
            return False
        elif not ("]]" in self.string):
            return False
        
        unichar chrs[self.string.length] # syntax hurty
        [self.string getCharacters:chrs]
        
        for i in range(0, self.length-1):
            unichar c1 = chrs[i]
            unichar c2 = chrs[i+1]
            
            if (c1 == ']'  and c2 == ']'):
                if position is not None:
                    position = i
                return True
            
            elif (c1 == '[' and c2 == '['):
                return False
        
        
        return False
    

    ### Returns `true` if the line can begin a note block
    def canBeginNoteBlock(self) -> bool:
        return self.canBeginNoteBlockWithActualIndex(None)
    

    ### Returns `true` if the line can begin a note block
    ### @param index Pointer to the index where the potential note block begins.
    def canBeginNoteBlockWithActualIndex(self, index: int) -> bool:
        if (self.length > 30000):
            return False
        
        unichar chrs[self.string.length]
        [self.string getCharacters:chrs]
        
        for i in range(0, self.length-1):
            unichar c1 = chrs[i]
            unichar c2 = chrs[i-1]
            
            if (c1 == '[' and c2 == '['):
                if (index != None):
                    index = i - 1
                return True
            
            elif (c1 == ']' and c2 == ']'):
                return False
        
        
        return False
    

    def noteContents(self) -> list:
        return self.noteContentsWithRanges(False)

    def noteContentsAndRanges(self) -> dict[any:str]:
        return self.noteContentsWithRanges(True)
    
    def contentAndRangeForLastNoteWithPrefix(self, string: str) -> list:
    
        string = string.lower()

        notes: dict = self.noteContentsAndRanges
        noteRange: range = range(0, 0) # syntax hurty: RANGE
        noteContent: str = ""
        
        ## Iterate through notes and only accept the last one.
        for r in notes.keys():
            _range = r.rangeValue # syntax hurty: RANGE
            noteString: str = notes[r]
            location: int = noteString.lower().find(string)
            
            ## Only accept notes which are later than the one already saved, and which begin with the given string
            if (range.location < noteRange.location or location != 0 ):
                continue
            
            ## Check the last character, which can be either ' ' or ':'. If it's note, carry on.
            if (noteString.length > string.length):
                unichar followingChr = [noteString characterAtIndex:string.length]
                if (followingChr != ' ' and followingChr != ':'):
                    continue
            
            
            noteRange = _range
            noteContent = noteString
        
        
        if (noteContent is not None) or (noteContent != ""):
            ## For notes with a prefix, we need to check that the note isn't bleeding out.
            if (NSMaxRange(noteRange) == self.length and self.noteOut):
                return None
            else:
                return [ [NSValue valueWithRange:noteRange], noteContent ] # ?? syntax hurty
        else:
            return None
        
    

    def noteContentsWithRanges(self, withRanges: bool):
        rangesAndStrings: dict[any: str]
        strings: list = []
        notes = self.noteData
        for note in notes:
            if withRanges:
                rangesAndStrings[note.range] = note.content # syntax hurty ?
            else: 
                strings.append(note.content)
        
        
        if withRanges:
            return rangesAndStrings
        else:
            return strings

    def notes(self) -> list:
        return self.noteData
    

    def notesAsJSON(self) -> list:
        notes: list = []
        for note in self.noteData:
            notes.append(note.json) # syntax hurty: what is this note.json ?????
        
        return notes'''

    #pragma mark Centered

    ### Returns TRUE if the line is *actually* centered. --- SHIFT RESPONSIBILITY
    def centered(self) -> bool: # The Line class should be a totally passive data container, should not have to do this calculation
        if (len(self.string) < 2): 
            return False
        return (self.string[0] == '>' 
                and self.string[-1] == '<')
    
    #pragma mark - Section depth --- BACKBURNER

    def sectionDepth(self) -> int:
        depth: int = 0

        for c in range(0, len(self.string)):
            if ([self.string[c]] == '#'):
                depth += 1
            else:
                break
        
        return depth

    #pragma mark - Story beats --- BACKBURNER

    '''def beats(self) -> list[Storybeat]:
        _beatRanges: list = []
        beats: list = []
        
        for note in self.noteData:
            if (note.type != NoteType.NoteTypeBeat):
                continue
            self.beatRanges.append(note.range)
            
            ## This is an empty note, ignore
            i = note.content.find(" ")
            if (i == None):
                continue
            
            beatContents: str = note.content[i]
            singleBeats: list = beatContents.split(",") # NOTE: must re-investigaet componentsSeparatedByString in other files...
            
            for b in singleBeats: 
                beat = Storybeat(line=self, 
                                 scene=None, 
                                 string=b.upper(), 
                                 _range=note.range)
                beats.append(beat)
            
        
        
        return beats

    def beatRanges(self) -> list: # ?? syntax hurty: WTF even is happening here lmao
        if (self.beatRanges == None):
            return self.beats
        return self.beatRanges

    def hasBeat(self) -> bool:
        if ("[[beat " in self.string.lower() or "[[storyline" in self.string.lower()):
            return True
        else:
            return False
    
    def hasBeatForStoryline(self, storyline: str) -> bool:
        for beat in self.beats:
            if storyline.lower() in beat.storyline.lower():
                return True
        
        return False
    

    def storylines(self) -> list[str]:
        storylines: list = []
        for beat in self.beats:
            storylines.append(beat.storyline)
        
        return storylines
    

    def storyBeatWithStoryline(self, storyline: str) -> Storybeat:
        for beat in self.beats:
            if storyline.lower() in beat.storyline.lower():
                return beat
        
        return None
    
    
    def firstBeatRange() -> range:
        __block NSRange beatRange = NSMakeRange(NSNotFound, 0)
        
        [self.beatRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            ## Find first range
            if (range.length > 0) {
                beatRange = range
                *stop = True
            }
        }]
        
        return beatRange'''
    
    #pragma mark - Formatting & attribution --- BACKBURNER --- SHIFT RESPONSIBILITY

    ### Parse and apply Fountain stylization inside the string contained by this line.
    '''def resetFormatting(self):
        length: int = self.string.length
        ## Let's not do this for extremely long lines. I don't know how many symbols a unichar array can hold.
        ## I guess there should be a fallback for insanely long strings, but this is a free and open source app, so if your
        ## unique artwork requires 300 000 unicode symbols on a single lines, please use some other software.
        if (length > 300000):
            return
        
        @try {
            ## Store the line as a char array to avoid calling characterAtIndex: at each iteration.
            unichar charArray[length]
            [self.string getCharacters:charArray]
            
            self.boldRanges = [self rangesInChars:charArray
                                        ofLength:length
                                        between:BOLD_CHAR
                                            and:BOLD_CHAR
                                    withLength:2]
            self.italicRanges = [self rangesInChars:charArray
                                        ofLength:length
                                        between:ITALIC_CHAR
                                            and:ITALIC_CHAR
                                    withLength:1]
            
            self.underlinedRanges = [self rangesInChars:charArray
                                            ofLength:length
                                                between:UNDERLINE_CHAR
                                                    and:UNDERLINE_CHAR
                                            withLength:1]
            
            self.noteRanges = [self rangesInChars:charArray
                                        ofLength:length
                                        between:NOTE_OPEN_CHAR
                                            and:NOTE_CLOSE_CHAR
                                    withLength:2]
            
            self.macroRanges = [self rangesInChars:charArray
                                        ofLength:length
                                        between:MACRO_OPEN_CHAR
                                            and:MACRO_CLOSE_CHAR
                                        withLength:2]
        }
        @catch (NSException* e) {
            NSLog(@"Error when trying to reset formatting: %@", e)
            return
        }'''
        
    # NOTE: a bunch of AttributedString related funcs, not going to deal with any of that unitl absolutely necessary
    ### Converts an FDX-style attributed string back to Fountain
    '''def NSString*)attributedStringToFountain:(NSAttributedString*)attrStr
    {
        ## NOTE! This only works with the FDX attributed string
        NSMutableString *result = NSMutableString.string
        
        __block NSInteger pos = 0
        
        [attrStr enumerateAttributesInRange:(NSRange){0, attrStr.length} options:0 usingBlock:^(NSDictionary<NSAttributedStringKey,id> * _Nonnull attrs, NSRange range, BOOL * _Nonnull stop) {
            NSString *string = [attrStr attributedSubstringFromRange:range].string
                    
            NSMutableString *open = [NSMutableString stringWithString:@""]
            NSMutableString *close = [NSMutableString stringWithString:@""]
            NSMutableString *openClose = [NSMutableString stringWithString:@""]
            
            NSSet *styles = attrs[@"Style"]
            
            if ([styles containsObject:BOLD_STYLE]) [openClose appendString:BOLD_PATTERN]
            if ([styles containsObject:ITALIC_STYLE]) [openClose appendString:ITALIC_PATTERN]
            if ([styles containsObject:UNDERLINE_STYLE]) [openClose appendString:UNDERLINE_PATTERN]
            if ([styles containsObject:NOTE_STYLE]) {
                [open appendString:[NSString stringWithFormat:@"%s", NOTE_OPEN_CHAR]]
                [close appendString:[NSString stringWithFormat:@"%s", NOTE_CLOSE_CHAR]]
            }
                            
            [result appendString:open]
            [result appendString:openClose]
            [result appendString:string]
            [result appendString:openClose]
            [result appendString:close]

            pos += open.length + openClose.length + string.length + openClose.length + close.length
        }]
        
        return [result stringByTrimmingCharactersInSet:NSCharacterSet.whitespaceCharacterSet]
    }

    ### Creates and stores a string with style attributes. Please don't use in editor, only for static parsing.
    ### - note N.B. This is NOT a Cocoa-compatible attributed string. The attributes are used to create a string for screenplay rendering or FDX export.
    def NSAttributedString*)attrString
    {
        if (_attrString == nil) {
            NSAttributedString *string = [self attributedStringForFDX]
            NSMutableAttributedString *result = NSMutableAttributedString.new
            
            [self.contentRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
                [result appendAttributedString:[string attributedSubstringFromRange:range]]
            }]
            
            _attrString = result
        }
        
        return _attrString
    }

    def NSAttributedString*)attributedStringForFDX
    {
        return [self attributedString]
    }

    ### Returns a string with style attributes.
    ### - note N.B. Does NOT return a Cocoa-compatible attributed string. The attributes are used to create a string for screenplay rendering or FDX export.
    def NSAttributedString*)attributedString
    {
        NSMutableAttributedString *string = [[NSMutableAttributedString alloc] initWithString:(self.string) ? self.string : @""]
            
        ## Make (forced) character names uppercase
        if (self.type == character or self.type == dualDialogueCharacter) {
            NSString *name = [self.string substringWithRange:self.characterNameRange].uppercaseString
            if (name) [string replaceCharactersInRange:self.characterNameRange withString:name]
        }
        
        ## Add font stylization
        [self.italicRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            if (range.length > ITALIC_PATTERN.length * 2) {
                if ([self rangeInStringRange:range]) [self addStyleAttr:ITALIC_STYLE toString:string range:range]
            }
        }]

        [self.boldRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            if (range.length > BOLD_PATTERN.length * 2) {
                if ([self rangeInStringRange:range]) [self addStyleAttr:BOLD_STYLE toString:string range:range]
            }
        }]
        
        [self.boldItalicRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            if (range.length > ITALIC_PATTERN.length * 2) {
                if ([self rangeInStringRange:range]) [self addStyleAttr:BOLDITALIC_STYLE toString:string range:range]
            }
        }]
        
        [self.underlinedRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            if (range.length > UNDERLINE_PATTERN.length * 2) {
                if ([self rangeInStringRange:range]) [self addStyleAttr:UNDERLINE_STYLE toString:string range:range]
            }
        }]
            
        [self.omittedRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            if (range.length > OMIT_PATTERN.length * 2) {
                if ([self rangeInStringRange:range]) [self addStyleAttr:OMIT_STYLE toString:string range:range]
            }
        }]
        
        [self.noteRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            if (range.length > NOTE_PATTERN.length * 2) {
                if ([self rangeInStringRange:range]) [self addStyleAttr:NOTE_STYLE toString:string range:range]
            }
        }]

        [self.escapeRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            if ([self rangeInStringRange:range]) [self addStyleAttr:OMIT_STYLE toString:string range:range]
        }]
            
        [self.removalSuggestionRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            if ([self rangeInStringRange:range]) [self addStyleAttr:@"RemovalSuggestion" toString:string range:range]
        }]
            
        ## Add macro attributes
        if (self.macroRanges.count > 0) {
            for (NSValue* r in self.macros.allKeys) {
                NSString* resolvedMacro = self.resolvedMacros[r]
                
                NSRange range = r.rangeValue
                [string addAttribute:@"Macro" value:(resolvedMacro) ? resolvedMacro : @"" range:range]
            }
        }
        
        if (self.revisedRanges.count) {
            for (NSString *key in _revisedRanges.allKeys) {
                [_revisedRanges[key] enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
                    if ([self rangeInStringRange:range]) {
                        [string addAttribute:@"Revision" value:key range:range]
                    }
                }]
            }
        }
        
        ## Loop through tags and apply
        for (NSDictionary *tag in self.tags) {
            NSString* tagValue = tag[@"tag"]
            if (!tagValue) continue
            
            NSRange range = [(NSValue*)tag[@"range"] rangeValue]
            [string addAttribute:@"BeatTag" value:tagValue range:range]
        }
        
        return string
    }

    ### N.B. Does NOT return a Cocoa-compatible attributed string. The attributes are used to create a string for FDX/HTML conversion.
    def void)addStyleAttr:(NSString*)name toString:(NSMutableAttributedString*)string range:(NSRange)range
    {
        if (name == nil) NSLog(@"WARNING: Null value passed to attributes")
        
        ## We are going out of range. Abort.
        if (range.location + range.length > string.length or range.length < 1 or range.location == NSNotFound) return
        
        ## Make a copy and enumerate attributes.
        ## Add style to the corresponding range while retaining the existing attributes, if applicable.
        [string.copy enumerateAttributesInRange:range options:0 usingBlock:^(NSDictionary<NSAttributedStringKey,id> * _Nonnull attrs, NSRange range, BOOL * _Nonnull stop) {
            NSMutableSet* style
            if (attrs[@"Style"] != nil) {
                ## We need to make a copy of the set, otherwise we'll add to the same set of attributes as earlier, causing issues with overlapping attributes.
                style = ((NSMutableSet*)attrs[@"Style"]).mutableCopy
                [style addObject:name]
            } else {
                style = [NSMutableSet.alloc initWithArray:@[name]]
            }
            
            [string addAttribute:@"Style" value:style range:range]
        }]
    }

    def NSAttributedString*)attributedStringWithMacros
    {
        NSMutableAttributedString* string = [NSMutableAttributedString.alloc initWithString:self.string]
        ## Add macro attributes
        for (NSValue* r in self.macros) {
            NSRange range = r.rangeValue
            NSString* resolvedMacro = self.resolvedMacros[r]
            
            [string addAttribute:@"Macro" value:(resolvedMacro) ? resolvedMacro : @"" range:range]
        }
        return string
    }

    ### Returns an attributed string without formatting markup
    def NSAttributedString*)attributedStringForOutputWith:(BeatExportSettings*)settings
    {
        ## First create a standard attributed string with the style attributes in place
        NSMutableAttributedString* attrStr = self.attributedString.mutableCopy
        
        ## Set up an index set for each index we want to include.
        NSMutableIndexSet* includedRanges = NSMutableIndexSet.new
        ## If we're printing notes, let's include those in the ranges
        if (settings.printNotes) [includedRanges addIndexes:self.noteRanges]
        
        ## Create actual content ranges
        NSMutableIndexSet* contentRanges = [self contentRangesIncluding:includedRanges].mutableCopy
        
        ## Enumerate visible ranges and build up the resulting string
        NSMutableAttributedString* result = NSMutableAttributedString.new
        [contentRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            if (range.length == 0) return
            
            NSAttributedString* content = [attrStr attributedSubstringFromRange:range]
            [result appendAttributedString:content]
            
            ## To ensure we can map the resulting attributed string *back* to the editor ranges, we'll mark the ranges they represent. This is an experimental part of the possible upcoming more WYSIWYG-like experience.
            NSRange editorRange = NSMakeRange(range.location, range.length)
            [result addAttribute:@"BeatEditorRange" value:[NSValue valueWithRange:editorRange] range:NSMakeRange(result.length-range.length, range.length)]
        }]
        
        ## Replace macro ranges. All macros should be resolved by now.
        [result.copy enumerateAttribute:@"Macro" inRange:NSMakeRange(0,result.length) options:NSAttributedStringEnumerationReverse usingBlock:^(id  _Nullable value, NSRange range, BOOL * _Nonnull stop) {
            if (value == nil) return
            NSDictionary* attrs = [result attributesAtIndex:range.location effectiveRange:nil]
            NSAttributedString* resolved = [NSAttributedString.alloc initWithString:value attributes:attrs]
            [result replaceCharactersInRange:range withAttributedString:resolved]
        }]
            
        return result
    }'''

    #pragma mark - Splitting --- BACKBURNER --- SHIFT RESPONSIBILITY



    # Splits a line at a given PRINTING index, meaning that the index was calculated from
    # the actually printing string, with all formatting removed. That's why we'll first create an attributed string,
    # and then format it back to Fountain.
    # 
    # The whole practice is silly, because we could actually just put attributed strings into the paginated
    # result — with revisions et al. I don't know why I'm just thinking about this now. Well, Beat is not
    # the result of clever thinking and design, but trial and error. Fuck you, past me, for leaving all
    # this to me.
    # 
    # We could actually send attributed strings to the PAGINATOR and make it easier to calculate the ----
    # it's 22.47 in the evening, I have to work tomorrow and I'm sitting alone in my kitchen. It's not
    # a problem for present me.
    # 
    # See you in the future.
    # 
    # __Update in 2023-12-28__: The pagination _sort of_ works like this nowadays, but because we are
    # still rendering Fountain to something else, we still need to split and format the lines.
    # This should still be fixed at some point. Maybe create line element which already has a preprocessed
    # attributed string for output.
    

    '''def NSArray<Line*>*)splitAndFormatToFountainAt:(NSInteger)index {
        NSAttributedString *string = [self attributedStringForFDX]
        NSMutableAttributedString *attrStr = NSMutableAttributedString.new
        
        [self.contentRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            if (range.length > 0) [attrStr appendAttributedString:[string attributedSubstringFromRange:range]]
        }]
        
        NSAttributedString *first  = [NSMutableAttributedString.alloc initWithString:@""]
        NSAttributedString *second = [NSMutableAttributedString.alloc initWithString:@""]
        
        ## Safeguard index (this could happen to numerous reasons, extra spaces etc.)
        if (index > attrStr.length) index = attrStr.length
        
        ## Put strings into the split strings
        first = [attrStr attributedSubstringFromRange:(NSRange){ 0, index }]
        if (index <= attrStr.length) second = [attrStr attributedSubstringFromRange:(NSRange){ index, attrStr.length - index }]
        
        ## Remove whitespace from the beginning if needed
        while (second.string.length > 0) {
            if ([second.string characterAtIndex:0] == ' ') {
                second = [second attributedSubstringFromRange:NSMakeRange(1, second.length - 1)]
                ## The index also shifts
                index += 1
            } else {
                break
            }
        }
        
        Line *retain = [Line withString:[self attributedStringToFountain:first] type:self.type pageSplit:True]
        Line *split = [Line withString:[self attributedStringToFountain:second] type:self.type pageSplit:True]
        
        if (self.changed) {
            retain.changed = True
            split.changed = True
        }
            
        ## Set flags
        
        retain.beginsNewParagraph = self.beginsNewParagraph
        retain.paragraphIn = self.paragraphIn
        retain.paragraphOut = True

        split.paragraphIn = True
        split.beginsNewParagraph = True

        ## Set identity
        
        retain.uuid = self.uuid
        retain.position = self.position
        
        split.uuid = self.uuid
        split.position = self.position + retain.string.length
        
        ## Now we'll have to go through some extra trouble to keep the revised ranges intact.
        if (self.revisedRanges.count) {
            NSRange firstRange = NSMakeRange(0, index)
            NSRange secondRange = NSMakeRange(index, split.string.length)
            split.revisedRanges = NSMutableDictionary.new
            retain.revisedRanges = NSMutableDictionary.new
            
            for (NSString *key in self.revisedRanges.allKeys) {
                retain.revisedRanges[key] = NSMutableIndexSet.indexSet
                split.revisedRanges[key] = NSMutableIndexSet.indexSet
                
                ## Iterate through revised ranges, calculate intersections and add to their respective line items
                [self.revisedRanges[key] enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
                    NSRange firstIntersct = NSIntersectionRange(range, firstRange)
                    NSRange secondIntersct = NSIntersectionRange(range, secondRange)
                    
                    if (firstIntersct.length > 0) {
                        [retain.revisedRanges[key] addIndexesInRange:firstIntersct]
                    }
                    if (secondIntersct.length > 0) {
                        ## Substract offset from the split range to get it back to zero
                        NSRange actualRange = NSMakeRange(secondIntersct.location - index, secondIntersct.length)
                        [split.revisedRanges[key] addIndexesInRange:actualRange]
                    }
                }]
            }
        }
        
        ## Let's also split our resolved macros
        if (self.resolvedMacros.count) {
            retain.resolvedMacros = NSMutableDictionary.new
            split.resolvedMacros = NSMutableDictionary.new
            
            for (NSValue* r in self.resolvedMacros.allKeys) {
                NSRange range = r.rangeValue
                if (range.length == 0) continue
                
                if (NSMaxRange(range) < index) {
                    NSValue* rKey = [NSValue valueWithRange:range]
                    retain.resolvedMacros[rKey] = self.resolvedMacros[r]
                } else {
                    NSRange newRange = NSMakeRange(range.location - index, range.length)
                    NSValue* rKey = [NSValue valueWithRange:newRange]
                    split.resolvedMacros[rKey] = self.resolvedMacros[r]
                }
            }
        }
        
        return @[ retain, split ]
    }'''

    #pragma mark - Formatting helpers --- BACKBURNER

    ### What is this? Seems like a more sensible attributed string idea.
    '''def NSAttributedString*)formattingAttributes
    {
        NSMutableAttributedString* attrStr = [NSMutableAttributedString.alloc initWithString:self.string]
        
        [self.italicRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            [attrStr addAttribute:BeatFormattingKeyItalic value:@True range:range]
        }]
        [self.boldRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            [attrStr addAttribute:BeatFormattingKeyBold value:@True range:range]
        }]
        [self.underlinedRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            [attrStr addAttribute:BeatFormattingKeyUnderline value:@True range:range]
        }]
        
        return attrStr
    }'''

    #pragma mark Formatting range lookup --- BACKBURNER

    ### Returns ranges between given strings. Used to return attributed string formatting to Fountain markup. The same method can be found in the parser, too. Why, I don't know.
    '''def rangesInChars(string:str,
                      length: int,
                      startString: str,
                      endString: str,
                      delimLength: int) -> list:
    
        indexSet: list = []
        
        lastIndex: int = length - delimLength ##Last index to look at if we are looking for start
        rangeBegin: int = -1 ##Set to -1 when no range is currently inspected, or the the index of a detected beginning
        
        # NOTE: What be this for loop
        for i in range(0, lastIndex+1):
            ## No range is currently inspected
            if (rangeBegin == -1):
                _match: bool = True
                for j in range(0, delimLength): 
                    ## Check for escape character (like \*)
                    if (i > 0 and string[j + i - 1] == '\\'):
                        _match = False
                        break
                    if (string[j+i] != startString[j]):
                        _match = False
                        break
                if (_match):
                    rangeBegin = i
                    i += delimLength - 1
                
            ## We have found a range
            else:
                _match: bool = True
                for j in range(0, delimLength):
                    if (string[j+i] != endString[j]):
                        _match = False
                        break
                    
                
                if (_match):
                    [indexSet addIndexesInRange:NSMakeRange(rangeBegin, i - rangeBegin + delimLength)]
                    rangeBegin = -1
                    i += delimLength - 1
                
            
        
            
        return indexSet'''
    

    #pragma mark Formatting checking convenience

    ### Returns TRUE when the line has no Fountain formatting (like **bold**)
    def noFormatting(self) -> bool:
        if (self.len(self.boldRanges)
            or self.len(self.italicRanges)
            or self.len(self.strikeoutRanges)
            or self.len(self.underlinedRanges)):
            return False
        else: 
            return True

    #pragma mark - Identity

    def matchesUUID(self, _uuid: uuid.uuid4) -> bool:
        if self._uuid == _uuid:
            return True
        else:
            return False
    

    def matchesUUIDString(self, _uuid: uuid.uuid4) -> bool:
        if str(self._uuid) == str(_uuid):
            return True
        else:
            return False
    

    def uuidString(self) -> str:
        return str(self._uuid)
    
    #pragma mark - Ranges --- BACKBURNER

    ### Converts a global (document-wide) range into local range inside the line
    '''def globalRangeToLocal(_range) -> range:
        ## Insert a range and get a LOCAL range in the line
        lineRange: range = (NSRange){ self.position, self.string.length }
        intersection: range = NSIntersectionRange(range, lineRange)
        
        return (NSRange){ intersection.location - self.position, intersection.length }
    

    ### Converts a global (document-wide) range into local range inside this line
    def globalRangeFromLocal(_range: range) -> range:
        return NSMakeRange(range.location + self.position, range.length)
    

    def rangeInStringRange:(NSRange)range {
        if (range.location + range.length <= self.string.length) return True
        else return False
    }

    ### Returns ranges with content ONLY (useful for reconstructing the string with no Fountain stylization)
    def NSIndexSet*)contentRanges
    {
        return [self contentRangesIncluding:nil]
    }
    ### Returns ranges with content ONLY (useful for reconstructing the string with no Fountain stylization), with given extra ranges included.
    def NSIndexSet*)contentRangesIncluding:(NSIndexSet*)includedRanges
    {
        NSMutableIndexSet *contentRanges = NSMutableIndexSet.indexSet
        [contentRanges addIndexesInRange:NSMakeRange(0, self.string.length)]
        
        ## Get formatting ranges.
        ## We can provide ranges that are excluded from formatting ranges and included in the resulting string.
        NSMutableIndexSet *formattingRanges = self.formattingRanges.mutableCopy
        [formattingRanges removeIndexes:includedRanges]
        
        ## Remove formatting indices from content indices.
        [contentRanges removeIndexes:formattingRanges]
        
        return contentRanges
    }

    ### Returns content ranges, including notes
    def NSIndexSet*)contentRangesWithNotes {
        ## Returns content ranges WITH notes included
        NSMutableIndexSet *contentRanges = [NSMutableIndexSet indexSet]
        [contentRanges addIndexesInRange:NSMakeRange(0, self.string.length)]
        
        NSIndexSet *formattingRanges = [self formattingRangesWithGlobalRange:False includeNotes:False]
        [contentRanges removeIndexes:formattingRanges]
        
        return contentRanges
    }

    def NSUInteger)numberOfPrecedingFormattingCharacters
    {
        if (self.string.length < 1) return 0
        
        LineType type = self.type
        unichar c = [self.string characterAtIndex:0]
        
        ## Check if this is a shot
        if (self.string.length > 1 and c == '!') {
            unichar c2 = [self.string characterAtIndex:1]
            if (type == shot and c2 == '!') return 2
        }
        
        ## Other types
        if ((self.type == character and c == '@') ||
            (self.type == heading and c == '.') ||
            (self.type == action and c == '!') ||
            (self.type == lyrics and c == '~') ||
            (self.type == synopse and c == '=') ||
            (self.type == centered and c == '>') ||
            (self.type == transitionLine and c == '>')) {
            return 1
        }
        ## Section
        elif (self.type == section) {
            return self.sectionDepth
        }
        
        return 0
    }

    ### Maps formatting characters into an index set, INCLUDING notes, scene numbers etc. to convert it to another style of formatting
    def NSIndexSet*)formattingRanges {
        return [self formattingRangesWithGlobalRange:False includeNotes:True]
    }

    ### Maps formatting characters into an index set, INCLUDING notes, scene numbers etc.
    ### You can use global range flag to return ranges relative to the *whole* document.
    ### Notes are included in formatting ranges by default.
    def NSIndexSet*)formattingRangesWithGlobalRange:(bool)globalRange includeNotes:(bool)includeNotes
    {
        NSMutableIndexSet *indices = NSMutableIndexSet.new
        NSInteger offset = 0
        
        if (globalRange) offset = self.position
        
        ## Add any ranges that are used to force elements. First handle the elements which don't work without markup characters.
        NSInteger precedingCharacters = self.numberOfPrecedingFormattingCharacters
        if (precedingCharacters > 0) {
            [indices addIndexesInRange:NSMakeRange(0 + offset, precedingCharacters)]
        }
        
        ## Catch dual dialogue force symbol
        if (self.type == dualDialogueCharacter and self.string.length > 0 and [self.string characterAtIndex:self.string.length - 1] == '^') {
            [indices addIndex:self.string.length - 1 +offset]
        }
        
        ## Add ranges for > and < (if needed)
        if (self.type == centered and self.string.length >= 2) {
            if ([self.string characterAtIndex:0] == '>' and [self.string characterAtIndex:self.string.length - 1] == '<') {
                [indices addIndex:0+offset]
                [indices addIndex:self.string.length - 1+offset]
            }
        }
        
        ## Title page keys will be included in formatting ranges
        if (self.isTitlePage and self.beginsTitlePageBlock and self.titlePageKey.length) {
            NSInteger i = self.titlePageKey.length+1
            [indices addIndexesInRange:NSMakeRange(0, i)]
            
            ## Also add following spaces to formatting ranges
            while (i < self.length) {
                unichar c = [self.string characterAtIndex:i]
                
                if (c == ' ') [indices addIndex:i]
                else break
                
                i += 1
            }
        }
        
        ## Escape ranges
        [indices addIndexes:[[NSIndexSet alloc] initWithIndexSet:self.escapeRanges]]
        
        ## Scene number range
        if (self.sceneNumberRange.length) {
            [indices addIndexesInRange:(NSRange){ self.sceneNumberRange.location + offset, self.sceneNumberRange.length }]
            ## Also remove the surrounding #'s
            [indices addIndex:self.sceneNumberRange.location + offset - 1]
            [indices addIndex:self.sceneNumberRange.location + self.sceneNumberRange.length + offset]
        }
        
        ## Stylization ranges
        [self.boldRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            [indices addIndexesInRange:NSMakeRange(range.location +offset, BOLD_PATTERN.length)]
            [indices addIndexesInRange:NSMakeRange(range.location + range.length - BOLD_PATTERN.length +offset, BOLD_PATTERN.length)]
        }]
        [self.italicRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            [indices addIndexesInRange:NSMakeRange(range.location +offset, ITALIC_PATTERN.length)]
            [indices addIndexesInRange:NSMakeRange(range.location + range.length - ITALIC_PATTERN.length +offset, ITALIC_PATTERN.length)]
        }]
        [self.underlinedRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            [indices addIndexesInRange:NSMakeRange(range.location +offset, UNDERLINE_PATTERN.length)]
            [indices addIndexesInRange:NSMakeRange(range.location + range.length - UNDERLINE_PATTERN.length +offset, UNDERLINE_PATTERN.length)]
        }]
        /*
        [self.strikeoutRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            [indices addIndexesInRange:NSMakeRange(range.location, STRIKEOUT_PATTERN.length +offset)]
            [indices addIndexesInRange:NSMakeRange(range.location + range.length - STRIKEOUT_PATTERN.length +offset, STRIKEOUT_PATTERN.length)]
        }]
        */
                
        ## Add note ranges
        if (includeNotes) [indices addIndexes:self.noteRanges]
        [indices addIndexes:self.omittedRanges]
        
        return indices
    }

    def NSRange)characterNameRange
    {
        NSInteger parenthesisLoc = [self.string rangeOfString:@"("].location
        
        if (parenthesisLoc == NSNotFound) {
            return (NSRange){ 0, self.string.length }
        } else {
            return (NSRange){ 0, parenthesisLoc }
        }
    }
    def hasExtension {
        ### Returns  `TRUE` if the character cue has an extension
        if (!self.isAnyCharacter) return False
        
        NSInteger parenthesisLoc = [self.string rangeOfString:@"("].location
        if (parenthesisLoc == NSNotFound) return False
        else return True
    }

    ### Ranges of emojis (o the times we live in)
    def NSArray<NSValue*>*)emojiRanges {
        return self.string.emo_emojiRanges
    }
    def hasEmojis {
        if (self.string == nil) return False
        return self.string.emo_containsEmoji
    }'''

    #pragma mark - Helper methods --- BACKBURNER
    def trimmed(self):
        return self.string.strip()
    
    '''### Joins a line into this line. Copies all stylization and offsets the formatting ranges.
    def void)joinWithLine:(Line *)line
    {
        if (!line) return
        
        NSString *string = line.string
        
        ## Remove symbols for forcing elements
        if (line.numberOfPrecedingFormattingCharacters > 0 and string.length > 0) {
            string = [string substringFromIndex:line.numberOfPrecedingFormattingCharacters]
        }
        
        NSInteger offset = self.string.length + 1 - line.numberOfPrecedingFormattingCharacters
        if (line.changed) self.changed = True
        
        ## Join strings
        self.string = [self.string stringByAppendingString:[NSString stringWithFormat:@"\n%@", string]]
        
        ## Offset and copy formatting ranges
        [line.boldRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            [self.boldRanges addIndexesInRange:(NSRange){ offset + range.location, range.length }]
        }]
        [line.italicRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            [self.italicRanges addIndexesInRange:(NSRange){ offset + range.location, range.length }]
        }]
        [line.underlinedRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            [self.underlinedRanges addIndexesInRange:(NSRange){ offset + range.location, range.length }]
        }]
        [line.strikeoutRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            [self.strikeoutRanges addIndexesInRange:(NSRange){ offset + range.location, range.length }]
        }]
        [line.escapeRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            [self.escapeRanges addIndexesInRange:(NSRange){ offset + range.location, range.length }]
        }]
        [line.noteRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            [self.noteRanges addIndexesInRange:(NSRange){ offset + range.location, range.length }]
        }]
        [line.macroRanges enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            [self.macroRanges addIndexesInRange:(NSRange){ offset + range.location, range.length }]
        }]
        
        ## Offset and copy revised ranges
        for (NSString* key in line.revisedRanges.allKeys) {
            if (!self.revisedRanges) self.revisedRanges = NSMutableDictionary.dictionary
            if (!self.revisedRanges[key]) self.revisedRanges[key] = NSMutableIndexSet.indexSet
            
            [line.revisedRanges[key] enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
                [self.revisedRanges[key] addIndexesInRange:(NSRange){ offset + range.location, range.length }]
            }]
        }
        
        ## Offset and copy resolved macros
        if (line.macroRanges.count > 0) {
            if (self.resolvedMacros == nil) self.resolvedMacros = NSMutableDictionary.new
            
            for (NSValue* r in line.resolvedMacros) {
                NSRange range = r.rangeValue
                NSRange newRange = NSMakeRange(range.location + offset, range.length)
                NSValue* rKey = [NSValue valueWithRange:newRange]
                self.resolvedMacros[rKey] = line.resolvedMacros[r]
            }
        }
    }

    def NSString*)characterName
    {
        ## This removes any extensions from character name, ie. (V.O.), (CONT'D) etc.
        ## We'll allow the method to run for lines under 4 characters, even if not parsed as character cues
        ## (update in 2022: why do we do this, past me?)
        if ((self.type != character and self.type != dualDialogueCharacter) and self.string.length > 3) return nil
        
        ## Strip formatting (such as symbols for forcing element types)
        NSString *name = self.stripFormatting
        if (name.length == 0) return @""
            
        ## Find and remove suffix
        NSRange suffixRange = [name rangeOfString:@"("]
        if (suffixRange.location != NSNotFound and suffixRange.location > 0) name = [name substringWithRange:(NSRange){0, suffixRange.location}]
        
        ## Remove dual dialogue character if needed
        if (self.type == dualDialogueCharacter and [name characterAtIndex:name.length-1] == '^') {
            name = [name substringToIndex:name.length - 1]
        }
        
        return [name stringByTrimmingCharactersInSet:NSCharacterSet.whitespaceCharacterSet]
    }
    '''
    def getTitlePageKey(self,) -> str:
        if (len(self.string) == 0):
            return ""
        if ":" in self.string:
            i: int = self.string.index(":")
            if (
                i == None 
                or i == 0 
                or [self.string[0]] == ' '
                or self.string[:i].lower().endswith(" to") # NOTE: maybe shouldn't be the responsibility of the title page key func to gatekeep transition lines
                ):
                return ""
            else:
                return self.string[:i].lower()
        else:
            return ""
    
    def getTitlePageValue(self) -> str:
        if ":" in self.string:
            i: int = self.string.index(":")
            if (i == None): 
                return self.string
            
            return self.string[i+1:].strip()
        elif self.string.strip() == "The Sequel": print("Amongus")
        else:
            return ""
    
    '''
    ### Returns `true` for lines which should effectively be considered as empty when parsing.
    def effectivelyEmpty {
        if (self.type == empty or self.length == 0 or self.opensOrClosesOmission or self.type == section or self.type == synopse ||
            (self.string.containsOnlyWhitespace and self.string.length == 1)) return True
        else return False
    }

    def opensOrClosesOmission {
        NSString *trimmed = [self.string stringByTrimmingCharactersInSet:NSCharacterSet.whitespaceCharacterSet]
        if ([trimmed isEqualToString:@"*/"] or [trimmed isEqualToString:@"/*"]) return True
        return False
    }'''

    #pragma mark - JSON serialization --- BACKBURNER

    '''-(NSDictionary*)forSerialization
    {
        NSMutableDictionary *json = [NSMutableDictionary dictionaryWithDictionary:@{
            @"string": (self.string.length) ? self.string.copy : @"",
            @"sceneNumber": (self.sceneNumber) ? self.sceneNumber.copy : @"",
            @"position": @(self.position),
            @"range": @{ @"location": @(self.range.location), @"length": @(self.range.length) },
            @"sectionDepth": @(self.sectionDepth),
            @"textRange": @{ @"location": @(self.textRange.location), @"length": @(self.textRange.length) },
            @"typeAsString": self.typeAsString,
            @"omitted": @(self.omitted),
            @"marker": (self.marker.length) ? self.marker : @"",
            @"markerDescription": (self.markerDescription.length) ? self.markerDescription : @"",
            @"uuid": (self.uuid) ? self.uuid.UUIDString : @"",
            @"notes": [self notesAsJSON],
            @"ranges": self.ranges
        }]
        
        if (self.type == synopse) {
            json[@"color"] = (self.color != nil) ? self.color : @""
            json[@"stringForDisplay"] = self.stringForDisplay
        }
        
        return json
    }

    ### Returns a dictionary of ranges for plugins
    -(NSDictionary*)ranges {
        return @{
            @"notes": [self indexSetAsArray:self.noteRanges],
            @"omitted": [self indexSetAsArray:self.omittedRanges],
            @"bold": [self indexSetAsArray:self.boldRanges],
            @"italic": [self indexSetAsArray:self.italicRanges],
            @"underlined": [self indexSetAsArray:self.underlinedRanges],
            @"revisions": @{
                @"blue": (self.revisedRanges[@"blue"]) ? [self indexSetAsArray:self.revisedRanges[@"blue"]] : @[],
                @"orange": (self.revisedRanges[@"orange"]) ? [self indexSetAsArray:self.revisedRanges[@"orange"]] : @[],
                @"purple": (self.revisedRanges[@"purple"]) ? [self indexSetAsArray:self.revisedRanges[@"purple"]] : @[],
                @"green": (self.revisedRanges[@"green"]) ? [self indexSetAsArray:self.revisedRanges[@"green"]] : @[]
            }
        }
    }

    -(NSArray*)indexSetAsArray:(NSIndexSet*)set {
        NSMutableArray *array = NSMutableArray.array
        [set enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            if (range.length > 0) {
                [array addObject:@[ @(range.location), @(range.length) ]]
            }
        }]
        
        return array
    }'''

    #pragma mark - Custom data --- BACKBURNER
    # NOTE: ?????? what is happening here
    '''def setCustomData(self, key:string, value: any) -> dict:
        if (not self.customDataDictionary):
            self.customDataDictionary: dict = {}
        
        if (not value):
            return self.customDataDictionary[key]
        else:
            self.customDataDictionary[key] = value
        return None
    
    def getCustomData(self, key: str) -> any:
        if (not self.customDataDictionary):
            self.customDataDictionary = {}
        return self.customDataDictionary[key]'''
    


    #pragma mark - Debugging --- BACKBURNER

    #def description() -> str:
    #    return "Line: %s  (%s at %s) %s", self.string, self.typeAsString, self.position, (self.nextElementIsDualDialogue) ? @"Next is dual" : @"" ]
    