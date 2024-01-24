# 2024 - 01 - 23

## Current Functionality

The parser is mostly working:
- Title Page Elements are working completely
- Action, Character, Parenthetical, Dialogue, Heading (sluglines) and Transition Line elements are working

Some things are not working just yet:
- Emphasis (Bold, italic, underline)

## Multilanguage considerations
Other things need to be re-worked or reconsidered going forward:
- I made the logic for detecting a transition line depend on if the line ends in "TO:", as per the fountain.io docs. However, this is English-language centric, and so this should not be the only method for parsing transition lines.

    - The original Beat code did not have this logic, and appeared to be language-agnostic. However, I also didn't understand how it worked exactly, nor could I make it work. I will have to try again to understand how to accomodate multiple languages for transition lines.

## Structural considerations

Currently the parser is `StaticFountainParser`, which is derived and modified from several functions in the old `ContinuousFountainParser`. I plan to use / implement the rest of the functionality of `ContinuousFountainParser` in another class, probably something like `DynamicFountainParser`.

I am doing this in the hopes of separating out these responsibilities:

1. Fountain parsing
2. Getting changes from the editor to update `Line` objects in memory
3. Writing changes back to the text file

I am imagining a `DynamicFountainParser` will call functions from the `StaticFountainParser`, but be itself responsible for handling the continuous editing changes.

### Separating Read and Write responsibility

The `StaticFountainParser` will *only* be responsible for *reading* from the text and spitting out arrays of `Line`. 

`DynamicFountainParser` will be primarily responsible for *handling continuous changes* from the editor, i.e. updating the contents of `Line` objects in memory. It will also call upon the `StaticFountainParser` to re-parse individual lines or blocks of lines in-place, rather than re-parse the entire document for every keystroke.

I am hoping dividing the responsibilities into discrete modules will enable a very usable API, such that potentially anyone wanting to make a fountain text editor can pick this up and get going. Also, so that anyone wanting to read this code and contribute to this particular port may do so more easily.


# 2024 - 01 - 17

## The Immediate Plan

The most immediate plan is to brute-force a functioning parser, by editing the existing code to be compliant to Python syntax.

There is a significant disparity of the syntactical functionality between Python and Objective-C. This has some obvious disadvantages -- there are some specific types and syntax in Objective-C which do not necessarily have a direct analogue in Python:

* `Blocks`
    * From what I understand, blocks in Objective-C are a way to write callbacks in a manner that keeps the code together in one section.

* `NSMutableIndexSet`
    * There are a myriad of "sets" and "arrays" in Objective-C, but I am choosing to largely ignore the nuances of these and just try and cram most things into `list` or `dict`

* Memory Management
    * Python is a garbage collecting language. Also, it passes variables by assignment by default, rather than by copy or reference. I am going to ignore or omit the nuances in the original code's memory management, cloning, copying, mutability, etc. so I can focus on the program logic. I have to cross my fingers that this won't hurt me. (It probably will, but whatever!)

Additionally, I am commenting out any functions that I feel are either not immediately relevant, or that should be reviewed for extraction into a different class.

To be specific, the `Line` and `ContinuousFountainParser` classes, contain logic for both reading and writing. 


## Read / Write responsibilities

I am trying to section off these responsibilities. I believe that the parser should generally only be responsible for *reading* the file and then categorizing each line into a specific element. A separate class should be created which either inherits from or uses the parser to then write new changes back into the document. Something like `LineWrite` or `LineModify`.

## Long-term goals

Rewriting the code in Python is incredibly useful as a way for me to simply understand the code, despite my complete lack of experience with Objective-C. It is very messy, and things will break, but just doing it will get at least something functional.

In the long term however, I have some concerns about thw whole thing being written in Python, specifically regarding performance and portability.

I worry that in practive, a wholly Python app would become unusuably slow, especially on lower end hardware or mobile (Android) devices. 

The sample Big Fish .fountain file is over 4600 lines long. With python's garbage collection system, trying to manage 4600 `Line` objects in memory... oof.

There are definitely some techniques that can and should be employed even in pure python to keep it manageable, but I am also considering if rewriting the backend specifically in a more performant language like Rust would be better for scalability.

Having the backend being written in Rust, compiled into libraries would also make it flexible -- Lots of languages have Foreign Function Interfaces (FFI) which can interop with library files, including Python and Dart.

The GUI could then be written in one of those more friendly languages, while the backend is very fast, memory-safe, and performant.

Of course, we shouldn't try to cross this bridge until we get something *functioning* in Python.

## Medium - term Goal

Once I get a functioning parser working in Python, I want to create a simple TUI (Terminal User Interface) app which can display .fountain files. This will be a quick and dirty proof-of-concept, and will not support the javascript plugins.

It will be able to simply demonstrate the Beat parser working, and it should be able to work on Linux and Windows. And, because it isn't a GUI, I don't have to worry about Wayland vs X11 madness. (Wayland still can't do multi-window apps LMAO)