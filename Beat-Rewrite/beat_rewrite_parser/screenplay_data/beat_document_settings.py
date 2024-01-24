#
#  BeatDocumentSettings.m
#  Beat
#
#  Created by Lauri-Matti Parppei on 30.10.2020.
#  Copyright © 2020 Lauri-Matti Parppei. All rights reserved.
#

 
#This creates a settings string that can be saved at the end of a Fountain file.
#I recommend using typed setters & getters when possible.

JSON_MARKER = "\n\n/* If you're seeing this, you can remove the following stuff - BEAT:"
JSON_MARKER_END = "END_BEAT */"

class BeatDocumentSettings:

    DocSettingRevisions: str =          "Revision"
    DocSettingHiddenRevisions: str =    "Hidden Revisions"
    DocSettingRevisionColor: str =      "Revision Color"
    DocSettingSceneNumberStart: str =   "Scene Numbering Starts From"
    DocSettingTagDefinitions: str =     "TagDefinitions"
    DocSettingTags: str =               "Tags"
    DocSettingLocked: str =             "Locked"
    DocSettingRevisedPageColor: str =   "Revised Page Color"
    DocSettingRevisionMode: str =       "Revision Mode"
    DocSettingColorCodePages: str =     "Color-code Pages"
    DocSettingCaretPosition: str =      "Caret Position"
    DocSettingChangedIndices: str =     "Changed Indices"
    DocSettingReviews: str =            "Review Ranges"
    DocSettingSidebarVisible: str =     "Sidebar Visible"
    DocSettingSidebarWidth: str =       "Sidebar Width"

    DocSettingHeadingUUIDs: str =       "Heading UUIDs"

    DocSettingWindowWidth: str =        "Window Width"
    DocSettingWindowHeight: str =       "Window Height"

    DocSettingActivePlugins: str =      "Active Plugins"

    DocSettingPageSize: str =           "Page Size"

    DocSettingCharacterGenders: str =   "CharacterGenders"

    DocSettingPrintSynopsis: str =      "Print Synopsis"
    DocSettingPrintSections: str =      "Print Sections"
    DocSettingPrintNotes   : str =      "Print Notes"

    DocSettingStylesheet   : str =      "Stylesheet"

    DocSettingCharacterData: str =      "CharacterData"

    _settings: dict = {}

    # omitted original init, it feels unnecessary in python
    def __init__(self):
        pass
    
    # typed getters and setters
    def setBool(self, key: str, value: bool):
        self._settings[key] = value
    
    def setInt(self, key: str, value: int):
        self._settings[key] = value
    
    def setFloat(self, key: str, value: float):
        self._settings[key] = value

    def setString(self, key: str, value: str):
        self._settings[key] = value
    
    def set(self, key: str, value: id):
        self._settings[key] = value
    
    def has(self, key: str) -> bool:
        if key in self._settings: 
            return True
        else:
            return False
    
    def getInt(self, key: str) -> int:
        return self._settings[key]
    
    def getFloat(self, key: str) -> float:
        return self._settings[key]
    
    def getBool(self, key: int | float) -> bool: 
        return self._settings[key]
    
    def getString(self, key: str):
    
        value: str = self._settings[key]

        if not isinstance(value, str): 
            value = ""

        return value
    
    def get(self, key) -> id:
        return self._settings[key]
    
    def remove(self, key: str):
        self._settings.removeObjectForKey(key)

    # important functions
    def getSettingsString(self) -> str:
        return self.getSettingsStringWithAdditionalSettings()
    
    # syntax hurty
    def getSettingsStringWithAdditionalSettings(self, additionalSettings: dict) -> str:
    
        settings: dict = self._settings
        if additionalSettings is not None: 
            merged = settings | additionalSettings
            settings = merged
        
        # Needs to be an exception ?
            
        NSError *error
        jsonData = NSJSONSerialization(dataWithJSONObject=settings, options=0 error=&error) # Do NOT pretty print this to make the block more compact

        if jsonData is None: 
            print("%s: error: ", __func__, error.localizedDescription)
            return ""
        else:
            json = jsonData
            return JSON_MARKER + json + JSON_MARKER_END
    
    # syntax hurty
    def readSettingsAndReturnRange(self, string: str) -> range:
        # RANGE -- OBJ C range is INCLUSIVE, python range is NOT INCLUSIVE
        r1: range = len(JSON_MARKER)
        r2: range = len(JSON_MARKER_END)
        # way more needs to be added to calculate this range properly
        # syntax hurty
        rSub: range = NSMakeRange(r1.location + r1.length, r2.location - r1.location - r1.length)
        
        if (r1.location != NSNotFound and r2.location != NSNotFound):
            settingsString: str = [string substringWithRange:rSub]
            NSData *settingsData = [settingsString dataUsingEncoding:NSUTF8StringEncoding]
            NSError *error
            
            settings: dict = [NSJSONSerialization JSONObjectWithData:settingsData options:kNilOptions error:&error]
            
            if (not error):
                self._settings = settings #???
            
                # Return the index where settings start
                return NSMakeRange(r1.location, r1.length + rSub.length + r2.length)
            else:
                # Something went wrong in reading the settings. Just carry on but log a message.
                # NSLog(@"ERROR: Document settings could not be read. %@", error)
                print('ERROR: Document settings could not be read. ', error)
                self._settings = {}
                return range(0, 0)
            
        
        
        return range(0) # why return a range of 0?
    

 
''' 
olen nimennyt nämä seinät
kodikseni
sä et pääse enää sisään
sä et pääse enää sisään ikinä

mun kasvit kasvaa
osaan pitää mullan kosteena
mun kasvit kasvaa ilman sua

sä et pääse enää sisään
en tarvii sua mihinkään
sä et pääse enää sisään
ikinä.
'''