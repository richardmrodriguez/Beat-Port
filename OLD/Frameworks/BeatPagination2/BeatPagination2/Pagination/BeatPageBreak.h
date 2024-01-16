//
//  BeatPageBreak.h
//  Beat
//
//  Created by Lauri-Matti Parppei on 18.12.2022.
//  Copyright © 2022 Lauri-Matti Parppei. All rights reserved.
//

#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN
@class Line;

@interface BeatPageBreak : NSObject
@property (nonatomic) CGFloat y;
@property (nonatomic) CGFloat lineHeight;
@property (nonatomic) Line* element;
@property (nonatomic) NSString* reason;

-(instancetype)initWithY:(CGFloat)y element:(Line*)line lineHeight:(CGFloat)lineHeight reason:(NSString*)reason;
-(instancetype)initWithY:(CGFloat)y element:(Line*)line lineHeight:(CGFloat)lineHeight;


-(instancetype)initWithVisibleIndex:(NSInteger)index element:(Line*)line attributedString:(NSAttributedString* _Nullable)attrStr reason:(NSString*)reason;

// For the WYSIWYG-variant
@property (nonatomic) NSInteger index;

@end

NS_ASSUME_NONNULL_END
