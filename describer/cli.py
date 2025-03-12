"""Command-line interface for the describer package."""

# Standard library imports
import argparse
import os
import sys

# Local imports
from .core import describe_codebase


def main():
    """Entry point for the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate architectural overviews of codebases using Gemini AI"
    )
    parser.add_argument(
        "directory",
        help="Directory to analyze"
    )
    parser.add_argument(
        "-s", "--system-prompt",
        default="architectural overview as markdown",
        help="System prompt to use for the LLM"
    )
    parser.add_argument(
        "-m", "--model",
        default="gemini-2.0-pro-exp-02-05",
        help="LLM model to use"
    )
    parser.add_argument(
        "-o", "--output",
        help="Write output to specified markdown file instead of stdout"
    )
    parser.add_argument(
        "--ignore-gitignore",
        action="store_true",
        help="Ignore .gitignore rules when scanning files (by default, .gitignore rules are respected)"
    )
    parser.add_argument(
        "--exclude",
        help="Exclude files matching this glob pattern (e.g., '*.test.ts')"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Don't display file count information"
    )

    # Parse only the known arguments, ignoring any extras
    args, unknown = parser.parse_known_args()

    # If there's an unknown argument and no explicit system prompt provided,
    # use the first unknown argument as the system prompt
    if unknown and "-s" not in sys.argv and "--system-prompt" not in sys.argv:
        args.system_prompt = " ".join(unknown)

    # If output file is specified, ensure it has a .md extension
    if args.output and not args.output.lower().endswith('.md'):
        args.output = args.output + '.md'

    # Run the core function to describe the codebase
    output, return_code, file_count = describe_codebase(
        args.directory,
        args.system_prompt,
        args.model,
        args.output,
        ignore_gitignore=args.ignore_gitignore,
        exclude_pattern=args.exclude
    )

    # Display file count information unless quiet mode is enabled
    if not args.quiet and file_count > 0 and return_code == 0:
        print(f"Analyzed {file_count} file{'s' if file_count != 1 else ''} from {os.path.abspath(args.directory)}")
        if args.ignore_gitignore:
            print("Note: .gitignore rules were ignored")
        if args.exclude:
            print(f"Excluded files matching: {args.exclude}")
        print()  # Add empty line for better readability

    # Handle output based on return code and output file
    if not args.output:
        # No output file specified, just print to console
        print(output)
    elif return_code == 0:
        # Only show success message if there was no error
        output_path = os.path.abspath(args.output)
        print(f"Output written to: {output_path}")
    else:
        # If there was an error, just print the error message
        print(output)

    sys.exit(return_code)


if __name__ == "__main__":
    main()
