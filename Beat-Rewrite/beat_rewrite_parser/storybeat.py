##
##  Storybeat.m
##  Beat
##
##  Created by Lauri-Matti Parppei on 14.2.2022.
##  Copyright © 2022 Lauri-Matti Parppei. All rights reserved.
##

#import "Storybeat.h"

# new imports
from line import Line 
from outline_scene import OutlineScene

class Storybeat:
### Creates a storyline and automatically divides storyline and beat.
    beat: str
    storyline: str
    scene: OutlineScene
    line: Line
    rangeInLine: range

    def __init__(self, line: Line, scene: OutlineScene, string:str, range: range):
        
        storyline: str = ""
        beat: str = ""
        
        if ":" in string:
            loc: int = string.find(":")
            if (loc > 0):
                storyline = string[:loc]
            else:
                storyline = string[1:]
            
            
            if (loc != string.length):
                beat = string[loc+1:]
            
            
        else: 
            storyline = string
        


    '''
    # idk what to do with this tbh
        storybeat = Storybeat()
        storybeat.line = line;
        storybeat.beat = [beat stringByTrimmingCharactersInSet:NSCharacterSet.whitespaceCharacterSet];
        storybeat.storyline = [storyline stringByTrimmingCharactersInSet:NSCharacterSet.whitespaceCharacterSet].uppercaseString;
        storybeat.scene = scene;
        storybeat.rangeInLine = range;
        return storybeat;
    '''

    @classmethod
    def stringWithStorylineNames(storylineNames: list[str]) -> str:
        
        string: str = "[[Beat "
        for name in storylineNames:
            string += name
            if name != storylineNames[-1]:
                string += ", "
        string += "]]"
        return string
    
    def stringWithBeats(self, beats: list[any]):
        string: str = "[[Beat"
        for beat in beats:
            # string = [string stringByAppendingFormat:@" %@", beat.stringified];
            string += " " + beat.stringified()
            if beat != beats[-1]:
                string += ","
        
        string += "]]"
        return string
    
    def stringified(self) -> str:
        string = self.storyline
        if (self.beat.length):
            string += ": " + self.beat
        return string
    

    def forSerialization(self) -> dict:
        return {
            "storyline": (self.storyline) if self.storyline else "",
            "beat": (self.beat) if self.beat else "",
        }
    

    #pragma mark - Debug

    def description(self) -> str: 
        return (self.storyline, 
                self.beat, 
                "(at", 
                self.rangeInLine.location, + ",", 
                self.rangeInLine.length + ")"
                )
    

