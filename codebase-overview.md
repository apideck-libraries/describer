```markdown
# Describer: Architectural Overview

## Overview

Describer is a command-line tool built in Python that leverages Google's Gemini AI to analyze and document codebases.  It takes a directory as input, gathers all the files within that directory (respecting `.gitignore` rules by default, with an option to override), and then uses the `llm` tool, along with the `llm-gemini` plugin, to interact with a specified Gemini model. The AI generates output based on a user-defined prompt, such as requesting an architectural overview, a summary of the codebase, identification of potential bugs, or general documentation.  The output can be directed to standard output or saved to a Markdown file.

## Core Components

The project is structured into the following key components:

1.  **`describer.cli` (Command-Line Interface):**
    *   Provides the command-line interface for users.
    *   Handles argument parsing (using `argparse`).
    *   Accepts the directory to analyze, system prompt, Gemini model, output file path, `.gitignore` handling, and quiet mode as arguments.
    *   Calls the core logic in `describer.core`.
    *   Handles the output (printing to console or writing to a file) and error reporting.
    *  Adds .md extension if missing from output file.
    * Informs the user about the amount of analyzed files and if `.gitignore` was used.

2.  **`describer.core` (Core Logic):**
    *   Contains the main function `describe_codebase` which orchestrates the analysis.
    *   Uses `files-to-prompt` to collect files from the specified directory. Supports ignoring `.gitignore` via a flag.
    *   Uses `llm` (with the `llm-gemini` plugin) to interact with the Gemini AI model, passing the collected code and the user's prompt.
    *   Handles subprocess execution and error checking for both `files-to-prompt` and `llm`.
    *   Provides a utility function `count_files_in_prompt` to determine the number of files processed.
    *   Includes a `format_markdown` function for basic Markdown cleanup (removes excessive blank lines).
    *   Returns the generated output, a return code (0 for success, 1 for error), and the number of files analyzed.

3.  **`tests` (Test Suite):**
    *   Contains unit tests for the `describer.core` module.
    *   Uses `unittest` and `unittest.mock` (specifically `patch`, `MagicMock`, and `mock_open`) to mock external dependencies (like `subprocess.Popen`, `subprocess.check_output`, and file operations).
    *   Tests various scenarios, including successful execution, error handling, output file writing, and `.gitignore` handling.
    *   Includes specific tests (`test_output_file.py`) focusing on the output file functionality and markdown formatting.

## Data Flow

1.  **Input:** The user provides a directory path and optionally a system prompt, model, output file, and flags for ignoring `.gitignore` or quiet mode via the command line.
2.  **File Collection:** `files-to-prompt` is called to gather all files within the specified directory, respecting `.gitignore` rules unless overridden.
3.  **Prompt Construction:** The collected files are formatted into a single prompt string suitable for the LLM.
4.  **AI Processing:** The prompt is sent to the specified Gemini model via the `llm` tool.
5.  **Output Generation:** The Gemini model generates text based on the prompt and the provided codebase.
6.  **Output Handling:**
    *   If an output file is specified, the generated text is formatted (using `format_markdown`) and written to the file.
    *   If no output file is specified, the generated text is printed to the console.
7.  **Error Handling:** Errors during file collection, LLM execution, or file writing are caught and reported to the user.
8. **File Count:** Displays file count and gitignore usage info.

## External Dependencies

*   **`files-to-prompt`:**  Collects files in a directory and prepares them for processing by an LLM.
*   **`llm`:** A command-line utility for interacting with various LLMs.
*   **`llm-gemini`:** An `llm` plugin that enables interaction with Google's Gemini models.
*   **`markdown`:** Used for basic markdown validation.
* **hatchling:** Used for building the package.
* **twine:** Used to upload to PyPi (inferred from development dependencies).
* **pytest:** Used to run tests (inferred from development dependencies).

## Build and Deployment

*   The project uses `hatchling` as the build backend (specified in `pyproject.toml`).
*   The `pyproject.toml` file defines project metadata, dependencies, and entry points.
*   The `README.md` file provides instructions for installation, usage, and development.
*   The `LICENSE` file specifies the project's license (MIT).
*   The package can be installed directly from GitHub using `pip`.

## Development Setup

The `README.md` provides instructions for setting up a development environment, including:

1.  Cloning the repository.
2.  Creating and activating a virtual environment.
3.  Installing the package in editable mode (`pip install -e .`).
4.  Installing development dependencies (`pip install build twine pytest`).
5.  Setting up the Gemini API key using `llm keys set gemini`.
6.  Running tests with:  `python -m unittest discover tests`
