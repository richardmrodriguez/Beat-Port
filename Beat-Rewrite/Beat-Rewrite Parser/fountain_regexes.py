#
#  RegexConstants.m
#
#  Copyright (c) 2012-2013 Nima Yousefi & John August
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy 
#  of this software and associated documentation files (the "Software"), to 
#  deal in the Software without restriction, including without limitation the 
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or 
#  sell copies of the Software, and to permit persons to whom the Software is 
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in 
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
#  IN THE SOFTWARE.
#

# could probably make this a json or yaml or something else language-agnostic

UNIVERSAL_LINE_BREAKS_PATTERN  = "\\r\\n|\\r|\\n"
UNIVERSAL_LINE_BREAKS_TEMPLATE = "\n"

#pragma mark - Patterns

SCENE_HEADER_PATTERN       = "(?<=\\n)(([iI][nN][tT]|[eE][xX][tT]|[^\\w][eE][sS][tT]|\\.|[iI]\\.?\\/[eE]\\.?)([^\\n]+))\\n"
ACTION_PATTERN             = "([^<>]*?)(\\n{2}|\\n<)"
MULTI_LINE_ACTION_PATTERN  = "\n{2}(([^a-z\\n:]+?[\\.\\?,\\s!\\*_]*?)\n{2}){1,2}"
CHARACTER_CUE_PATTERN      = "(?<=\\n)([ \\t]*[^<>a-z\\s\\/\\n][^<>a-z:!\\?\\n]*[^<>a-z\\(!\\?:,\\n\\.][ \\t]?)\\n{1}(?!\\n)"
DIALOGUE_PATTERN           = "(<(Character|Parenthetical)>[^<>\\n]+<\\/(Character|Parenthetical)>)([^<>]*?)(?=\\n{2}|\\n{1}<Parenthetical>)"
PARENTHETICAL_PATTERN      = "(\\([^<>]*?\\)[\\s]?)\n"
TRANSITION_PATTERN         = "\\n([\\*_]*([^<>\\na-z]*TO:|FADE TO BLACK\\.|FADE OUT\\.|CUT TO BLACK\\.)[\\*_]*)\\n"
FORCED_TRANSITION_PATTERN  = "\\n((&gt;|>)\\s*[^<>\\n]+)\\n"    # need to look for &gt; pattern because we run this regex against marked up content
FALSE_TRANSITION_PATTERN  = "\\n((&gt;|>)\\s*[^<>\\n]+(&lt;\\s*))\\n";     # need to look for &gt; pattern because we run this regex against marked up content
PAGE_BREAK_PATTERN         = "(?<=\\n)(\\s*[\\=\\-\\_]{3,8}\\s*)\\n{1}"
CLEANUP_PATTERN            = "<Action>\\s*<\\/Action>"
FIRST_LINE_ACTION_PATTERN  = "^\\n\\n([^<>\\n#]*?)\\n"
SCENE_NUMBER_PATTERN       = "(\\#([0-9A-Za-z\\.\\)-]+)\\#)"
SECTION_HEADER_PATTERN     = "((#+)(\\s*[^\\n]*))\\n?"

#pragma mark - Templates

SCENE_HEADER_TEMPLATE      = "\n<Scene Heading>$1</Scene Heading>"
ACTION_TEMPLATE            = "<Action>$1</Action>$2"
MULTI_LINE_ACTION_TEMPLATE = "\n<Action>$2</Action>"
CHARACTER_CUE_TEMPLATE     = "<Character>$1</Character>"
DIALOGUE_TEMPLATE          = "$1<Dialogue>$4</Dialogue>"
PARENTHETICAL_TEMPLATE     = "<Parenthetical>$1</Parenthetical>"
TRANSITION_TEMPLATE        = "\n<Transition>$1</Transition>"
FORCED_TRANSITION_TEMPLATE = "\n<Transition>$1</Transition>"
FALSE_TRANSITION_TEMPLATE  = "\n<Action>$1</Action>"
PAGE_BREAK_TEMPLATE        = "\n<Page Break></Page Break>\n"
CLEANUP_TEMPLATE           = ""
FIRST_LINE_ACTION_TEMPLATE = "<Action>$1</Action>\n"
SECTION_HEADER_TEMPLATE    = "<Section Heading>$1</Section Heading>"

#pragma mark - Block Comments
BLOCK_COMMENT_PATTERN      = "\\n\\/\\*([^<>]+?)\\*\\/\\n"
BRACKET_COMMENT_PATTERN    = "\\n\\[{2}([^<>]+?)\\]{2}\\n"
SYNOPSIS_PATTERN           = "\\n={1}([^<>=][^<>]+?)\\n";    # we need to make sure we don't catch ==== as a synopsis
BLOCK_COMMENT_TEMPLATE     = "\n<Boneyard>$1</Boneyard>\n"
BRACKET_COMMENT_TEMPLATE   = "\n<Comment>$1</Comment>\n"
SYNOPSIS_TEMPLATE          = "\n<Synopsis>$1</Synopsis>\n"
NEWLINE_REPLACEMENT        = "@@@@@"; # NOTE: fuuuuuuck what even is this lmao
NEWLINE_RESTORE            = "\n"
#pragma mark - Title Page

TITLE_PAGE_PATTERN             = "^([^\\n]+:(([ \\t]*|\\n)[^\\n]+\\n)+)+\\n"
INLINE_DIRECTIVE_PATTERN       = "^([\\w\\s&]+):\\s*([^\\s][\\w&,\\.\\?!:\\(\\)\\/\\s-©\\*\\_]+)$"
MULTI_LINE_DIRECTIVE_PATTERN   = "^([\\w\\s&]+):\\s*$"
MULTI_LINE_DATA_PATTERN        = "^([ ]{2,8}|\\t)([^<>]+)$"

#pragma mark - Misc

DUAL_DIALOGUE_PATTERN          = "\\^\\s*$"
CENTERED_TEXT_PATTERN          = "^>[^<>\\n]+<"


#pragma mark - Formatting regexes

BOLD_ITALIC_UNDERLINE_FORMATTING_PATTERN  = "(?<!\\\\)(_\\*{3}|\\*{3}_)([^<>]+)(_\\*{3}|\\*{3}_)"
BOLD_ITALIC_FORMATTING_PATTERN            = "(?<!\\\\)(\\*{3})([^<>]+)(\\*{3})"
BOLD_UNDERLINE_FORMATTING_PATTERN         = "(?<!\\\\)(_\\*{2}|\\*{2}_)([^<>]+)(_\\*{2}|\\*{2}_)"
ITALIC_UNDERLINE_FORMATTING_PATTERN       = "(?<!\\\\)(_\\*{1}|\\*{1}_)([^<>]+)(_\\*{1}|\\*{1}_)"
BOLD_FORMATTING_PATTERN                   = "(?<!\\\\)(\\*{2})(.+?)(\\*{2})"
ITALIC_FORMATTING_PATTERN                 = "(?<!\\\\)(\\*)(.+?)(\\*)"
UNDERLINE_FORMATTING_PATTERN              = "(?<!\\\\)(_)(.+?)(_)"

#pragma mark - Styling templates

BOLD_ITALIC_UNDERLINE_TEMPLATE = "Bold+Italic+Underline"
BOLD_ITALIC_TEMPLATE           = "Bold+Italic"
BOLD_UNDERLINE_TEMPLATE        = "Bold+Underline"
ITALIC_UNDERLINE_TEMPLATE      = "Italic+Underline"
BOLD_TEMPLATE                  = "Bold"
ITALIC_TEMPLATE                = "Italic"
UNDERLINE_TEMPLATE             = "Underline"
