from dataclasses import dataclass

@dataclass
class FormattingCharacters:
    #pragma mark - Formatting characters

    FORMATTING_CHARACTERS = ["/*", "*/", "*", "_", "[[", "]]", "<<", ">>"]

    ITALIC_PATTERN = "*"
    ITALIC_CHAR = "*"
    BOLD_PATTERN = "**"
    BOLD_CHAR = "**"
    UNDERLINE_PATTERN = "_"
    UNDERLINE_CHAR = "_"
    OMIT_PATTERN = "/*"
    NOTE_PATTERN = "[["

    NOTE_OPEN_CHAR = "[["
    NOTE_CLOSE_CHAR = "]]"

    MACRO_OPEN_CHAR = r"{{"
    MACRO_CLOSE_CHAR = r"}}"

    NOTE_OPEN_PATTERN = "[["
    NOTE_CLOSE_PATTERN = "]]"
    OMIT_OPEN_PATTERN = "/*"
    OMIT_CLOSE_PATTERN = "*/"

    BOLD_PATTERN_LENGTH = 2
    ITALIC_PATTERN_LENGTH = 1
    UNDERLINE_PATTERN_LENGTH = 1
    NOTE_PATTERN_LENGTH = 2
    OMIT_PATTERN_LENGTH = 2
    HIGHLIGHT_PATTERN_LENGTH = 2
    STRIKEOUT_PATTERN_LENGTH = 2

    COLOR_PATTERN = "color"
    STORYLINE_PATTERN = "storyline"

    # FDX style names
    ## For FDX compatibility & attribution

    BOLD_STYLE = "Bold"
    ITALIC_STYLE = "Italic"
    BOLDITALIC_STYLE = "BoldItalic"
    UNDERLINE_STYLE = "Underline"
    STRIKEOUT_STYLE = "Strikeout"
    OMIT_STYLE = "Omit"
    NOTE_STYLE = "Note"
    MACRO_STYLE = "Macro"

# print(FormattingCharacters().MACRO_STYLE)