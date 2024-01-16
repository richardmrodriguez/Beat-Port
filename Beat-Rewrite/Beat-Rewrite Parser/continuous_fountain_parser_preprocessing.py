##
##  ContinuousFountainParser+Preprocessing.m
##  BeatParsing
##
##  Created by Lauri-Matti Parppei on 4.1.2024.
##

 
# This category handles the line preprocessing before the document is allowed to be printed.
##  It's a subclass now

from continuous_fountain_parser import ContinuousFountainParser
from screenplay_data.beat_screenplay import BeatScreenplay
from screenplay_data.beat_export_settings import BeatExportSettings


#pragma mark - Preprocessing


## ?? syntax hurty
## was a category instead of a subclass before
class Preprocessing(ContinuousFountainParser):

    def preprocessForPrinting(self) -> list:
        return self.preprocessForPrintingWithLines(
            lines=self.safeLines,
            exportSettings=None,
            screenplayData=None
            )
    

    def preprocessForPrintingWithExportSettings(
            self, 
            exportSettings: BeatExportSettings
            ) -> list:
        return self.preprocessForPrintingWithLines(
            lines=self.safeLines,
            exportSettings=exportSettings,
            screenplayData=None
            )
    
    ## ?? syntax hurty
    # this is probably the wrong interperetation tbh
    # ! PARAMETERS are probably wrong names
    def preprocessForPrintingWithLines(
            self, 
            lines: list, 
            exportSettings:BeatExportSettings,
            screenplayData:BeatScreenplay
            ) -> list:
        
        if (lines is None) or (lines == []):
            lines = self.safeLines
        return self.preprocessForPrintingWithLines(
            lines=lines, 
            documentSettings=self.documentSettings,
            exportSettings=exportSettings,
            screenplay=screenplayData
            )
    

    def _preprocessForPrintingWithLines(lines: list, documentSettings: BeatDocumentSettings) -> list:

        return ContinuousFountainParser.preprocessForPrintingWithLines(
            lines=lines,
            documentSettings=documentSettings, 
            exportSettings=None, 
            screenplay=None
            )
    
    
    # BEEG func
    def _preprocessForPrintingWithLines(
            lines: list,
            documentSettings: BeatDocumentSettings,
            exportSettings: BeatExportSettings,
            screenplay: BeatScreenplay
            ) -> list:
        
        #### !? CODE STRUCTURE: can any of this be done with a match statement instead of a bunch of if-statements?
    
        ## The array for printable elements
        elements: list = []
        
        ## Create a copy of parsed lines
        linesForPrinting: list = []
        precedingLine: Line
        macros = BeatMacroParser()
        
        
        for line in lines:
            linesForPrinting.append(line.clone)
                    
            l: Line = linesForPrinting[-1]
            
            ## Preprocess macros
            if (l.macroRanges.count > 0):
                
                ## syntax hurty
                ## wtf is this lmao
                macroKeys: list = [l.macros.allKeys sortedArrayUsingComparator:^NSComparisonResult(NSValue*  _Nonnull obj1, NSValue*  _Nonnull obj2) {
                    return (obj1.rangeValue.location > obj2.rangeValue.location);
                }];
                
                l.resolvedMacros = {}
                for (NSValue* range in macroKeys):
                    macro: str = l.macros[range];
                    id value = [macros parseMacro:macro];
                    
                    if (value is not None):
                        l.resolvedMacros[range] = [NSString stringWithFormat:@"%@", value]
                
            
            
            ## Skip line if it's a macro and has no results
            if l.macroRanges.count == l.length and l.resolvedMacros.count == 0:
                linesForPrinting.pop
                ## ?? syntax hurty
                ## empty is a Line type, but idk where it is defined as such
                l.type = empty
                precedingLine = l
                continue
            
            
            ## Skip notes
            if l.note and not exportSettings.printNotes:
                continue
            
            ## Reset dual dialogue
            elif l.type == character:
                l.nextElementIsDualDialogue = False
            
            elif (l.type == action or l.type == lyrics or l.type == centered):
                l.beginsNewParagraph = True
                
                ## BUT in some cases, they don't.
                if (not precedingLine.effectivelyEmpty) and (precedingLine.type == l.type):
                    l.beginsNewParagraph = False
                
            
            else:
                l.beginsNewParagraph = True
            
            
            precedingLine = l;
        
        
        ## Get scene number offset from the delegate/document settings
        sceneNumber: int = 1;
        if documentSettings.getInt(DocSettingSceneNumberStart) > 1:
            sceneNumber = documentSettings.getInt(DocSettingSceneNumberStart)
            if sceneNumber < 1:
                sceneNumber = 1
        
        
        ##
        previousLine: Line
        for line in linesForPrinting:
            ## Fix a weird bug for first line
            if (
                (line.type == empty) 
                and (line.string.length )
                and (not line.string.containsOnlyWhitespace)
                ): 

                line.type = action
            
            ## Check if we should spare some non-printing objects or not.
            if (
                (line.isInvisible or line.effectivelyEmpty) 
                and 
                (
                    exportSettings.additionalTypes,containsIndex(line.type) 
                    or (line.note and exportSettings.printNotes)
                )
                 ):
                  
                
                ## Lines which are *effectively* empty have to be remembered.
                if line.effectivelyEmpty: 
                    previousLine = line;

                continue
            
            
            ## Add scene numbers
            if (line.type == heading):
                if (line.sceneNumberRange.length > 0):
                    # syntax hurty
                    # what is sceneNumberRange ?
                    # what is substringWithRange ?
                    line.sceneNumber = [line.string substringWithRange:line.sceneNumberRange];
                
            elif (not line.sceneNumber or line.sceneNumber is None):
                    line.sceneNumber = str(sceneNumber);
                    sceneNumber += 1;
                
            else:
                line.sceneNumber = ""
            
            
            ## Eliminate faux empty lines with only single space. To force whitespace you have to use two spaces.
            if ([line.string == " "]):
                line.type = empty;
                continue
            
                    
            ## Remove misinterpreted dialogue
            if (line.isAnyDialogue and line.string.length == 0): 
                line.type = empty;
                previousLine = line;
                continue;
            
                        
            ## If this is a dual dialogue character cue, we'll need to search for the previous one
            ## and make it aware of being a part of a dual dialogue block.
            if (line.type == dualDialogueCharacter):
                i: int = elements.count - 1;
                while (i >= 0):
                    precedingLine: Line = elements[i]    
                    if (precedingLine.type == character):
                        precedingLine.nextElementIsDualDialogue = True;
                        break
                    
                    
                    ## Break the loop if this is not a dialogue element OR it's another dual dialogue element.
                    if not (precedingLine.isDialogueElement or precedingLine.isDualDialogueElement):
                       break

                    i -= 1
                
            
            
            elements.append(line)
            
            previousLine = line;
        
        
        return elements;



