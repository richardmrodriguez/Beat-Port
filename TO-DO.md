# Immediate Tasks

## The Backend

The backend consists of three core parts. Each part builds upon the functionality of the last:

### Reading

* Parsing
* Pagination
* PDF Rendering

### Writing / Editing

Once read-only fuctionality is implemented, the Backend needs to also provide editing functions.

### Additional Backend Responsibilities
In addition, the backend is also responsible for other functions, which will become clearer as I get closer to implementing the frontend GUI.

* Javascript Plugin System

### Parser
The backend includes the Parser, which provides functions for parsing a `fountain` formatted text file, and returning the `Line Type` for each line.

The parser provides context for the following:

Beat's parser is responsible for identifying the `Line Type` of each and every line in a `Fountain` formatted plaintext screenplay file.

Here are some key points:

* Line Types are inherently contextual to the previous and following line.
    * For example, a Dialogue line is identified as such if the `Line Type` before it is a `Character`.
* In addition to continuous-contextual parsing, the Beat Parser also supports forced-formatting.
    * a bang `!` at the beginning of a line forces that line to be `Action`.

### Paginator

The app must generate a properly formatted document. The app uses the `Line Type` in addition to the raw text to visually arrange the text in the GUI text editor.

The pagination is also obviously useful for rendering a properly formatted PDF document.

### PDF Renderer

### Graphical Text Editor