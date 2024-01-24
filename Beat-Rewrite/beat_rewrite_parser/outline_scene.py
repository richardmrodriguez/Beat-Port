##
##  OutlineScene.m
##  Beat
##
##  Created by Lauri-Matti Parppei on 18.2.2019.
##  Copyright © 2019 Lauri-Matti Parppei. All rights reserved.
##

# import <Foundation/Foundation.h>
from beat_note_data import BeatNoteData
# from outline_scene import OutlineScene


class OutlineScene:

    def withLine(line: Line, delegate:(id)delegate) -> OutlineScene: # syntax hurty: what is a delegate
        return [[OutlineScene alloc] initWithLine:line delegate:delegate]

    def withLine(line: Line) -> OutlineScene:
        return [[OutlineScene alloc] initWithLine:line]
    

    def initWithLine(line: Line):
        return self.initWithLine(line, None)
    


    ## ???? syntax hurty
    def initWithLine(line: Line, delegate:(id)delegate): 
        if (self = [super init]) == None:
            return None
        
        self.line = line
        self.delegate = delegate
        self.beats = []
        self.synopsis = []
        self.lines = []
        
        return self
    

    ### Calculates the range for this scene
    def get_range(self) -> range:
        return range(self.position, self.length)

    ### Returns a very unreliable "chronometric" length for the scene
    def timeLength(self) -> int:
        ## Welllll... this is a silly implementation, but let's do it.
        ## We'll measure scene length purely by the character length, but let's substract the scene heading length
        length: int = self.length - self.line.string.length + 40
        if (length < 0): 
            length = 40
        
        return length

    #pragma mark - JSON serialization

    ### Returns JSON data for scene properties (convenience method)
    def json(self) -> dict:
        return self.forSerialization(self)
    
    ### Returns JSON data for scene properties
    def forSerialization(self) -> dict:
    
        #@synchronized (self) 
            synopsis: list[dict] = [NSMutableArray arrayWithCapacity:_synopsis.count]
            for (s in _synopsis):
                synopsis.addObject(s.forSerialization)
            
            json: dict = {
                ## String values have to be guarded so we don't try to put nil into NSDictionary
                "string": (self.string != None) if self.string.copy else "",
                "typeAsString": (self.line.typeAsString) if self.line.typeAsString else "",
                "stringForDisplay": (self.stringForDisplay.length) if self.stringForDisplay else "",
                "storylines": (self.storylines) if self.storylines.copy else [],
                "sceneNumber": (self.sceneNumber) if self.sceneNumber.copy else "",
                "color": (self.color) if self.color.copy else "",
                "sectionDepth": (self.sectionDepth),
                "markerColors": (self.markerColors.count) if self.markerColors.allObjects.copy else [],
                "range": { "location": (self.range.location), "length": (self.range.length) },
                "sceneStart": (self.position),
                "sceneLength": (self.length),
                "omitted": (self.omitted),
                "synopsis": synopsis,
                "storybeats": (self.beats.count) if self.serializedBeats() else [],
                "line": self.line.forSerialization,
                "notes": self.notesAsJSON,
                "uuid": self.line.uuidString
            }
            
            return json
        
    

    def serializedBeats(self) -> list:
        beats = []
        for beat in self.beats:
            beats.append(beat.forSerialization)
    
        return beats

    def notesAsJSON(self) -> list:

        noteData: list = self.notes
        notes = []
        for note in noteData:
            notes.append(note.json)

        return notes

    #pragma mark - Section hierarchy

    def sectionDepth(self) -> int:
        self.oldSectionDepth = self.line.sectionDepth
        return _sectionDepth
    

    #pragma mark - Forwarded properties

    def type(self) -> LineType: 
        return self.line.type 

    def stringForDisplay(self)  -> str:
        return self.line.stringForDisplay 
    def string(self)  -> str:
        return self.line.string 
    def typeAsString(self) -> str:
        return self.line.typeAsString 

    def position(self) -> int:
        return self.line.position

    def omitted(self) -> bool:
        return self.line.omitted 
    def omited(self) -> bool:
         return self.omitted ## Legacy compatibility

    def color(self) -> str:
        return self.line.color 

    def sceneNumber(self) -> str:
        return self.line.sceneNumber 
    def setSceneNumber:(NSString *)sceneNumber { self.line.sceneNumber = sceneNumber }

    ## Plugin backwards compatibility
        # ? what do you mean backwards compatibility bruh
    def sceneStart(self) -> int:
        return self.position
    def sceneLength(self) -> int:
        return self.length

    #pragma mark - Generated properties

    def length(self) -> int:
        if (not_delegate): 
            return _length
        @synchronized (self.delegate.lines) { # syntax hurty: synchronized
            NSArray <Line*> *lines = self.delegate.lines.copy
            NSInteger index = [lines indexOfObject:self.line]
            
            NSInteger length = -1
            
            for (i = index + 1, i < lines.count i += 1) {
                ## To avoid any race conditions, let's break this loop if the lines array was changed
                if (not lines[i] or i >= lines.count) break
                
                Line *line = lines[i]
                if ((line.type == heading or line.type == section) and line != self.line) {
                    return line.position - self.position
                }
            }
            
            if (length == -1) {
                return NSMaxRange(lines.lastObject.textRange) - self.position
            }
            
            return length
        }
    

    ### Fetches the lines for this scene.
    ### - note: The scene has to have a delegate set for this to work. In a normal situation, this should be the case, but if you are receiving an empty array or getting an error, check if there are issues with initialization.
    def lines(self) -> list:
        return self.delegate.linesForScene(self)
    

    ### Returns an array of characters who have dialogue in this scene
    def characters(self) -> list:
        lines: list = self.lines
        
        names: list = [] # syntax hurty: NSMutableSet
        
        for line in lines:
            if line.isOutlineElement and line.type != synopse and line != self.line:
                break
            elif line.type == character or line.type == dualDialogueCharacter:
                characterName = line.characterName
                if characterName.length: 
                    names.append(line.characterName)
        
        
        return names
    

    ### An experimental method for finding where the omission covering this scene begins at.
    def omissionStartsAt(self) -> int:
        if (not self.omitted):
            return -1
        
        lines: list = self.delegate.lines
        idx: int = [lines indexOfObject:self.line]
        
        ## Find out where the omission starts
        for (s = idx, s >= 0, s -= 1):
            Line *prevLine = lines[s]
            NSInteger omitLoc = [prevLine.string rangeOfString:@"/*"].location
            if ((omitLoc is not None) and (prevLine.omitOut)):
                return prevLine.position + omitLoc
            
        
        
        return -1
    

    ### An experimental method for finding where the omission covering this scene ends at.
    def omissionEndsAt(self) -> int:
        if (not self.omitted) return -1
        
        NSArray *lines = self.delegate.lines
        NSInteger idx = [lines indexOfObject:self.line]
        
        ## Find out where the omission ends
        for (s = idx + 1, s < len(lines), s += 1):
            nextLine: Line = lines[s]
            omitEndLoc: int = [nextLine.string rangeOfString:@"*/"].location
            
            if (omitEndLoc != NSNotFound and nextLine.omitIn) {
                return nextLine.position + omitEndLoc
                break
            }
        
        
        return -1
    

    ### Returns the storyline NAMES in this scene
    def storylines(self) -> list[str]:
        beats: list = self.beats.copy
        storylines: list = []
        
        for (beat in beats):
            storylines.append(beat.storyline)
        
        return storylines
    



    #pragma mark - Synthesized properties

    # @synthesize omited
    # syntax hurty: what does synthesize motted do ??

    #pragma mark - Debugging

    def description(self) -> str:
        return f"Scene: {self.string} (pos {self.position} / len {self.length})"
            
    

 
''' 
This place is not a place of honor.
No highly esteemed deed is commemorated here.
Nothing valued is here.

What is here was dangerous and repulsive to us.
This message is a warning about danger.

The danger is still present, in your time, as it was in ours.
The danger is to the body, and it can kill.

The form of the danger is an emanation of energy.

The danger is unleashed only if you substantially disturb this place physically.
This place is best shunned and left uninhabited.
'''
 
 
