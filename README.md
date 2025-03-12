# Describer

Analyze codebases using AI - generate architectural overviews, documentation, explanations, bug reports and more.

## What It Does

Describer scans all files in a directory and uses Google's Gemini AI to generate an architectural overview or any other analysis of the codebase.

For example, you can:

- Generate markdown architectural overviews
- Get a summary of the codebase
- Analyze code patterns
- Document the codebase structure
- Find potential bugs or issues
- Generate test ideas

## Prerequisites

- Python 3.6+
- A Google AI Studio API key for Gemini

## Installation

> **Note:** This package is currently in early development and not yet published to PyPI.

Install directly from GitHub:

```bash
pip install git+https://github.com/apideck-libraries/describer.git
```

Then set up your Gemini API key:

```bash
llm keys set gemini
```

When prompted, enter your API key from Google AI Studio (https://makersuite.google.com/app/apikey).

## Usage

```bash
# Generate an architectural overview of a directory
describer path/to/directory

# Generate a specific type of analysis
describer path/to/directory "summarize this codebase in 3 bullet points"
describer path/to/directory "identify potential bugs in this code"
describer path/to/directory "document this codebase as if for a new developer"

# Use a specific model
describer -m gemini-1.5-pro-latest path/to/directory
```

## How It Works

This project combines these tools:

1. [files-to-prompt](https://github.com/simonw/files-to-prompt): Collects all files in a directory and formats them for processing by an LLM.
2. [llm](https://llm.datasette.io/en/stable/): A command-line tool for interacting with various LLMs.
3. [llm-gemini](https://github.com/simonw/llm-gemini): A plugin for the `llm` tool to use Google's Gemini models.

## Development

If you want to contribute to this project, follow these steps to set up your development environment:

1. Clone the repository:

   ```bash
   git clone https://github.com/apideck-libraries/describer.git
   cd describer
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. Install the package in development mode:

   ```bash
   pip install -e .
   ```

5. Install development dependencies:

   ```bash
   pip install build twine pytest
   ```

6. Set up your Gemini API key:

   ```bash
   llm keys set gemini
   ```

7. Run tests:
   ```bash
   python -m unittest discover tests
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
