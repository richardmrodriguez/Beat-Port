#
#  BeatScreenplay.m
#  BeatParsing
#
#  Created by Lauri-Matti Parppei on 7.10.2022.
#

# import "BeatScreenplay.h"
from continuous_fountain_parser import ContinuousFountainParser
from continuous_fountain_parser_preprocessing import ContinuousFountainParser
from beat_export_settings import BeatExportSettings

#pragma mark - Screenplay meta-object

class BeatScreenplay:

# Usage: [BeatScreenplay from:parser settings:settings]
# python Usage: BeatScreenplay(from, settings)
    parser
    settings
    
    def __init__(self, parser, settings) -> None:
        self.parser = parser
        self.settings = settings

    # I have no idea whatsoever what this code is supposed to be doing

    def +(instancetype)from:(ContinuousFountainParser*)parser:
    
        return self(parser, None)
    
    def +(instancetype)from:(ContinuousFountainParser*)parser settings:(BeatExportSettings*)settings:
    
        screenplay = BeatScreenplay()
        screenplay.titlePage = [ContinuousFountainParser titlePageForString:parser.titlePageAsString]
        screenplay.titlePageContent = parser.parseTitlePage
        screenplay.lines = parser.preprocessForPrintingWithExportSettings(settings)
        
        return screenplay
    
