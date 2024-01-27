# Beat Rewrite

A simple, elegant screenwriting app.

This is a port of Lauri-Matti Parppei's macOS app "Beat", for Linux and Windows.

"Beat" is originally based upon "Writer" by Hendrik Noeller.

Please check [PROGESS](PROGRESS.md) to see the progress as well as plans for functionality.

Please check [OVERVIEW](OVERVIEW.md) for the current top-down look at the structure of the code.

Everything is very early and Work-in-Progress!

## Current Functionality

The `StaticFountainParser` can parse the following line types:
                       
✅ section                      
✅ synopse                       
✅ titlePageTitle                
✅ titlePageAuthor               
✅ titlePageCredit               
✅ titlePageSource               
✅ titlePageContact              
✅ titlePageDraftDate            
❌ titlePageUnknown -- for custom Title Page fields

✅ heading                        
✅ action                         
✅ character                      
✅ parenthetical                  
✅ dialogue                       
✅ dualDialogueCharacter          
✅ dualDialogueParenthetical      
✅ dualDialogue                   
✅ transitionLine                 
✅ lyrics                         
✅ pageBreak                      
✅ centered                       
✅ shot 
  