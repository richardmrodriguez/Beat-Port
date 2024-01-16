##
##  BeatParsing.h
##  BeatParsing
##
##  Created by Lauri-Matti Parppei on 29.10.2022.
##

# ifndef BeatParsing_h
# define BeatParsing_h
# pragma clang system_header

from continuous_fountain_parser import ContinuousFountainParser
from continuous_fountain_parser_preprocessing import ContinuousFountainParser

from line import Line

from outline_scene import OutlineScene
import fountain_regexes as fr
from screenplay_data.beat_document_settings import BeatDocumentSettings

# import <BeatParsing/RegExCategories.h>
# import <BeatParsing/NSString+CharacterControl.h>
# import <BeatParsing/NSString+Regex.h>
# import <BeatParsing/NSMutableString+Regex.h>

# import <BeatParsing/NSCharacterSet+BadControlCharacters.h>
# import <BeatParsing/NSString+EMOEmoji.h>

# endif #/* BeatParsing_h */

# print(fr.UNIVERSAL_LINE_BREAKS_PATTERN)