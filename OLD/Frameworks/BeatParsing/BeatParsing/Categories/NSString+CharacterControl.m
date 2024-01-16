//
//  NSString+Whitespace.m
//  Beat
//
//  Created by Hendrik Noeller on 01.04.16.
//  Copyright © 2016 Hendrik Noeller. All rights reserved.
//	Parts copyright © 2019-2021 Lauri-Matti Parppei. All rights reserved.
//

#import "NSString+CharacterControl.h"

@implementation NSString (CharacterControl)

- (bool)containsOnlyWhitespace
{
    NSUInteger length = [self length];
    
    NSCharacterSet* whitespaceSet = NSCharacterSet.whitespaceAndNewlineCharacterSet;
    for (int i = 0; i < length; i++) {
        unichar c = [self characterAtIndex:i];
        if (![whitespaceSet characterIsMember:c]) {
            return NO;
        }
    }
    return YES;
}

- (NSCharacterSet*)uppercaseLetters {
    // Add some symbols which are potentially not recognized out of the box.
    // List stolen from https://stackoverflow.com/questions/36897781/how-to-uppercase-lowercase-utf-8-characters-in-c
    static NSMutableCharacterSet* characters;
    if (characters == nil) {
        characters = NSCharacterSet.uppercaseLetterCharacterSet.mutableCopy;
        
        //[characters addCharactersInString:@"IÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞĀĂĄĆĈĊČĎĐĒĔĖĘĚĜĞĠĢĤĦĨĪĬĮİĲĴĶĹĻĽĿŁŃŅŇŊŌŎŐŒŔŖŘŚŜŞŠŢŤŦŨŪŬŮŰŲŴŶŸŹŻŽƁƂƄƆƇƊƋƎƏƐƑƓƔƖƗƘƜƝƠƢƤƧƩƬƮƯƱƲƳƵƷƸƼǄǅǇǈǊǋǍǏǑǓǕǗǙǛǞǠǢǤǦǨǪǬǮǱǲǴǶǷǸǺǼǾȀȂȄȆȈȊȌȎȐȒȔȖȘȚȜȞȠȢȤȦȨȪȬȮȰȲȺȻȽȾɁɃɄɅɆɈɊɌɎͰͲͶͿΆΈΉΊΌΎΏΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩΪΫϏϘϚϜϞϠϢϤϦϨϪϬϮϴϷϹϺϽϾϿЀЁЂЃЄЅІЇЈЉЊЋЌЍЎЏАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯѠѢѤѦѨѪѬѮѰѲѴѶѸѺѼѾҀҊҌҎҐҒҔҖҘҚҜҞҠҢҤҦҨҪҬҮҰҲҴҶҸҺҼҾӀӁӃӅӇӉӋӍӐӒӔӖӘӚӜӞӠӢӤӦӨӪӬӮӰӲӴӶӸӺӼӾԀԂԄԆԈԊԌԎԐԒԔԖԘԚԜԞԠԢԤԦԨԪԬԮԱԲԳԴԵԶԷԸԹԺԻԼԽԾԿՀՁՂՃՄՅՆՇՈՉՊՋՌՍՎՏՐՑՒՓՔՕՖႠႡႢႣႤႥႦႧႨႩႪႫႬႭႮႯႰႱႲႳႴႵႶႷႸႹႺႻႼႽႾႿჀჁჂჃჄჅჇჍᎠᎡᎢᎣᎤᎥᎦᎧᎨᎩᎪᎫᎬᎭᎮᎯᎰᎱᎲᎳᎴᎵᎶᎷᎸᎹᎺᎻᎼᎽᎾᎿᏀᏁᏂᏃᏄᏅᏆᏇᏈᏉᏊᏋᏌᏍᏎᏏᏐᏑᏒᏓᏔᏕᏖᏗᏘᏙᏚᏛᏜᏝᏞᏟᏠᏡᏢᏣᏤᏥᏦᏧᏨᏩᏪᏫᏬᏭᏮᏯᏰᏱᏲᏳᏴᏵᲐᲑᲒᲓᲔᲕᲖᲗᲘᲙᲚᲛᲜᲝᲞᲟᲠᲡᲢᲣᲤᲥᲦᲧᲨᲩᲪᲫᲬᲭᲮᲯᲰᲱᲲᲳᲴᲵᲶᲷᲸᲹᲺᲽᲾᲿḀḂḄḆḈḊḌḎḐḒḔḖḘḚḜḞḠḢḤḦḨḪḬḮḰḲḴḶḸḺḼḾṀṂṄṆṈṊṌṎṐṒṔṖṘṚṜṞṠṢṤṦṨṪṬṮṰṲṴṶṸṺṼṾẀẂẄẆẈẊẌẎẐẒẔẞẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼẾỀỂỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴỶỸỺỼỾἈἉἊἋἌἍἎἏἘἙἚἛἜἝἨἩἪἫἬἭἮἯἸἹἺἻἼἽἾἿὈὉὊὋὌὍὙὛὝὟὨὩὪὫὬὭὮὯᾈᾉᾊᾋᾌᾍᾎᾏᾘᾙᾚᾛᾜᾝᾞᾟᾨᾩᾪᾫᾬᾭᾮᾯᾸᾹᾺΆᾼῈΈῊΉῌῘῙῚΊῨῩῪΎῬῸΌῺΏῼⰀⰁⰂⰃⰄⰅⰆⰇⰈⰉⰊⰋⰌⰍⰎⰏⰐⰑⰒⰓⰔⰕⰖⰗⰘⰙⰚⰛⰜⰝⰞⰟⰠⰡⰢⰣⰤⰥⰦⰧⰨⰩⰪⰫⰬⰭⰮⱠⱢⱣⱤⱧⱩⱫⱭⱮⱯⱰⱲⱵⱾⱿⲀⲂⲄⲆⲈⲊⲌⲎⲐⲒⲔⲖⲘⲚⲜⲞⲠⲢⲤⲦⲨⲪⲬⲮⲰⲲⲴⲶⲸⲺⲼⲾⳀⳂⳄⳆⳈⳊⳌⳎⳐⳒⳔⳖⳘⳚⳜⳞⳠⳢⳫⳭⳲⴀⴁⴂⴃⴄⴅⴆⴇⴈⴉⴊⴋⴌⴍⴎⴏⴐⴑⴒⴓⴔⴕⴖⴗⴘⴙⴚⴛⴜⴝⴞⴟⴠⴡⴢⴣⴤⴥⴧⴭꙀꙂꙄꙆꙈꙊꙌꙎꙐꙒꙔꙖꙘꙚꙜꙞꙠꙢꙤꙦꙨꙪꙬꚀꚂꚄꚆꚈꚊꚌꚎꚐꚒꚔꚖꚘꚚꜢꜤꜦꜨꜪꜬꜮꜲꜴꜶꜸꜺꜼꜾꝀꝂꝄꝆꝈꝊꝌꝎꝐꝒꝔꝖꝘꝚꝜꝞꝠꝢꝤꝦꝨꝪꝬꝮꝹꝻꝽꝾꞀꞂꞄꞆꞋꞍꞐꞒꞖꞘꞚꞜꞞꞠꞢꞤꞦꞨꞪꞫꞬꞭꞮꞰꞱꞲꞳꞴꞶꞸꞺꞼꞾꟂꟄꟅꟆꟇꟉꟵＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ𐐀𐐁𐐂𐐃𐐄𐐅𐐆𐐇𐐈𐐉𐐊𐐋𐐌𐐍𐐎𐐏𐐐𐐑𐐒𐐓𐐔𐐕𐐖𐐗𐐘𐐙𐐚𐐛𐐜𐐝𐐞𐐟𐐠𐐡𐐢𐐣𐐤𐐥𐐦𐐧𐒰𐒱𐒲𐒳𐒴𐒵𐒶𐒷𐒸𐒹𐒺𐒻𐒼𐒽𐒾𐒿𐓀𐓁𐓂𐓃𐓄𐓅𐓆𐓇𐓈𐓉𐓊𐓋𐓌𐓍𐓎𐓏𐓐𐓑𐓒𐓓𐲀𐲁𐲂𐲃𐲄𐲅𐲆𐲇𐲈𐲉𐲊𐲋𐲌𐲍𐲎𐲏𐲐𐲑𐲒𐲓𐲔𐲕𐲖𐲗𐲘𐲙𐲚𐲛𐲜𐲝𐲞𐲟𐲠𐲡𐲢𐲣𐲤𐲥𐲦𐲧𐲨𐲩𐲪𐲫𐲬𐲭𐲮𐲯𐲰𐲱𐲲𑢠𑢡𑢢𑢣𑢤𑢥𑢦𑢧𑢨𑢩𑢪𑢫𑢬𑢭𑢮𑢯𑢰𑢱𑢲𑢳𑢴𑢵𑢶𑢷𑢸𑢹𑢺𑢻𑢼𑢽𑢾𑢿𖹀𖹁𖹂𖹃𖹄𖹅𖹆𖹇𖹈𖹉𖹊𖹋𖹌𖹍𖹎𖹏𖹐𖹑𖹒𖹓𖹔𖹕𖹖𖹗𖹘𖹙𖹚𖹛𖹜𖹝𖹞𖹟𞤀𞤁𞤂𞤃𞤄𞤅𞤆𞤇𞤈𞤉𞤊𞤋𞤌𞤍𞤎𞤏𞤐𞤑𞤒𞤓𞤔𞤕𞤖𞤗𞤘𞤙𞤚𞤛𞤜𞤝𞤞𞤟𞤠𞤡"];
    }
    return characters;
}

- (bool)containsUppercaseLetters
{
    NSCharacterSet* characters = [self uppercaseLetters];
    
    for (int i = 0; i < self.length; i++) {
        unichar c = [self characterAtIndex:i];
        if ([characters characterIsMember:c]) return YES;
    }
    return NO;
}

- (NSInteger)numberOfOccurencesOfCharacter:(unichar)symbol {
	NSInteger occurences = 0;
	
	for (NSInteger i=0; i<self.length; i++) {
		if ([self characterAtIndex:i] == symbol) occurences += 1;
	}
	
	return occurences;
}

- (bool)containsOnlyUppercase
{
	return [self.uppercaseString isEqualToString:self] && [self containsUppercaseLetters];
}

- (NSString *)stringByTrimmingTrailingCharactersInSet:(NSCharacterSet *)characterSet {
	NSRange rangeOfLastWantedCharacter = [self rangeOfCharacterFromSet:characterSet.invertedSet options:NSBackwardsSearch];
	if (rangeOfLastWantedCharacter.location == NSNotFound) {
		return @"";
	}
    if (rangeOfLastWantedCharacter.location + 1 <= self.length) {
        return [self substringToIndex:rangeOfLastWantedCharacter.location+1]; // non-inclusive
    } else {
        return self;
    }
}

- (bool)onlyUppercaseUntilParenthesis
{
	NSInteger parenthesisLoc = [self rangeOfString:@"("].location;
	NSInteger noteLoc = [self rangeOfString:@"[["].location;
	
	if (noteLoc == 0 || parenthesisLoc == 0) return NO;

	if (parenthesisLoc == NSNotFound) {
		// No parenthesis
		return self.containsOnlyUppercase;
	}
	else {
        // We need to check past parentheses, too, in case the user started the line with something like:
        // MIA (30) does something...
        bool parenthesisOpen = false;
        NSMutableIndexSet *indexSet = NSMutableIndexSet.new;
        
        for (NSInteger i=0; i<self.length; i++) {
            unichar c = [self characterAtIndex:i];
            if (c == ')') {
                parenthesisOpen = false;
                continue;
            }
            else if (c == '(') {
                parenthesisOpen = true;
                continue;
            }
            else if (!parenthesisOpen) {
                [indexSet addIndex:i];
            }
        }
        
        __block bool containsLowerCase = false;
        [indexSet enumerateRangesUsingBlock:^(NSRange range, BOOL * _Nonnull stop) {
            NSString *substr = [self substringWithRange:range];
            if ([substr containsOnlyWhitespace]) return;
            else if (![substr containsOnlyUppercase]) {
                containsLowerCase = true;
                *stop = true;
            }
        }];
        
        if (containsLowerCase) return false;
        else return true;
	}
	
	return NO;
}

- (NSRange)rangeBetweenFirstAndLastOccurrenceOf:(unichar)chr {
    NSInteger first = NSNotFound;
    NSInteger last = 0;
    
    for (NSInteger i=0; i<self.length; i++) {
        unichar c = [self characterAtIndex:i];
        if (c == chr && first == NSNotFound) {
            first = i;
        }
        else if (c == chr) {
            last = i;
        }
    }
    
    if (first == NSNotFound) return NSMakeRange(first, 0);
    else return NSMakeRange(first, last - first);
}

- (NSString*)stringByRemovingRange:(NSRange)range {
    NSString* head = [self substringToIndex:range.location];
    NSString* tail = (NSMaxRange(range) < self.length) ? [self substringFromIndex:NSMaxRange(range)] : @"";
    
    return [NSString stringWithFormat:@"%@%@", head, tail];
}

- (NSString*)trim
{
    return [self stringByTrimmingCharactersInSet:NSCharacterSet.whitespaceCharacterSet];
}

- (NSInteger)locationOfLastOccurenceOf:(unichar)chr
{
    for (NSInteger i=self.length-1; i>=0; i--) {
        unichar c = [self characterAtIndex:i];
        if (c == chr) return i;
    }
    
    return NSNotFound;
}

@end
