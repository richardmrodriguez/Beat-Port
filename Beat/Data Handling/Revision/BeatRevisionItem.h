//
//  BeatReviewItem.h
//  Beat
//
//  Created by Lauri-Matti Parppei on 15.3.2021.
//  Copyright © 2021 KAPITAN!. All rights reserved.
//

#import <TargetConditionals.h>
#if !TARGET_OS_IOS
    #import <Cocoa/Cocoa.h>
#else
    #import <UIKit/UIKit.h>
#endif

#if TARGET_OS_IOS
    #define BeatColor UIColor
#else
    #define BeatColor NSColor
#endif

typedef enum : NSInteger {
	RevisionNone = 0,
	RevisionAddition,
	RevisionRemoval,
	RevisionComment
} RevisionType;

@interface BeatRevisionItem : NSObject
@property (nonatomic) RevisionType type;
@property (nonatomic) NSString *colorName;
@property (nonatomic) NSString *text; // Support for additional comments - unrealized, for now
+ (BeatRevisionItem*)type:(RevisionType)type color:(NSString*)color;
+ (BeatRevisionItem*)type:(RevisionType)type;
+ (NSArray<NSString*>*)availableColors;
- (BeatColor*)backgroundColor;
- (NSString*)key;
- (NSString*)description;
@end
