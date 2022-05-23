//
//  BeatPaperSizing.m
//  Beat
//
//  Created by Lauri-Matti Parppei on 25.11.2020.
//  Copyright © 2020 Lauri-Matti Parppei. All rights reserved.
//

#import "BeatPaperSizing.h"

#define PAPER_A4 595.0, 842.0
#define PAPER_USLETTER 612.0, 792.0

@implementation BeatMargins

+ (BeatMargins*)margins {
	static BeatMargins* margins;
	if (!margins) margins = BeatMargins.new;
	
	NSDictionary *contents = [NSDictionary dictionaryWithContentsOfURL:[NSBundle.mainBundle URLForResource:@"Page Sizing" withExtension:@"plist"]];
	margins.top = [(NSNumber*)contents[@"Margin Top"] floatValue];
	margins.bottom = [(NSNumber*)contents[@"Margin Bottom"] floatValue];
	margins.left = [(NSNumber*)contents[@"Margin Left"] floatValue];
	margins.right = [(NSNumber*)contents[@"Margin Right"] floatValue];
	
	return margins;
}

@end

@implementation BeatPaperSizing

+ (NSPrintInfo*)printInfoFor:(BeatPaperSize)size {
	NSPrintInfo *printInfo = NSPrintInfo.sharedPrintInfo;
	return [BeatPaperSizing setSize:size printInfo:printInfo];
}

+ (NSPrintInfo*)setMargins:(NSPrintInfo*)printInfo {
	BeatMargins *margins = BeatMargins.margins;
	
	CGSize offset = CGSizeMake(0, 0);
	CGFloat reference = 12.5;
	CGSize imageableSize = CGSizeMake(printInfo.imageablePageBounds.origin.x, printInfo.imageablePageBounds.origin.y);
	
	// The user's system has less visible space on paper than it should (???), so let's fix that in margins.
	if (imageableSize.width - reference > 0 || imageableSize.height - reference > 0) {
		offset.width = imageableSize.width - reference;
		offset.width = imageableSize.height - reference;
	}
	
	printInfo.topMargin = margins.top - offset.height;
	printInfo.bottomMargin = margins.bottom;
	printInfo.leftMargin = margins.left - offset.width;
	printInfo.rightMargin = margins.right;
	
	
	return printInfo;
}
+ (NSPrintInfo*)setPaperSize:(NSPrintInfo*)printInfo size:(BeatPaperSize)size {
	
	if (size == BeatA4) [printInfo setPaperName:@"A4"];
	else [printInfo setPaperName:@"Letter"];
	
	return printInfo;
}

+ (NSPrintInfo*)setSize:(BeatPaperSize)size printInfo:(NSPrintInfo*)printInfo {
	printInfo = [BeatPaperSizing setPaperSize:printInfo size:size];
	printInfo = [BeatPaperSizing setMargins:printInfo];
	
	return printInfo;
}

+ (void)setPageSize:(BeatPaperSize)size printInfo:(NSPrintInfo*)printInfo {
	if (size == BeatA4) printInfo.paperSize = NSMakeSize(PAPER_A4);
	else printInfo.paperSize = NSMakeSize(PAPER_USLETTER);
	
	printInfo = [self setMargins:printInfo];
	/*
	BeatMargins *margins = BeatMargins.margins;
	printInfo.topMargin = margins.top;
	printInfo.bottomMargin = margins.bottom;
	printInfo.leftMargin = margins.left;
	printInfo.rightMargin = margins.right;
	*/
}

@end
/*
 
 mä puen villapaidan päälle
 me tehdään kierros järven jäälle
 ja nähdään läheltä saari
 jossa muutama talo on tyhjillään
 
 se ei oo mitenkään ihmeellistä
 se ei oo mitään tyypillistä
 josta joku vois tehdä kivan biisin
 ja kerätä miljoonan
 
 */