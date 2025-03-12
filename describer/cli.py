"""Command-line interface for the describer package."""

import argparse
import sys
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

    # Parse only the known arguments, ignoring any extras
    args, unknown = parser.parse_known_args()

    # If there's an unknown argument and no explicit system prompt provided,
    # use the first unknown argument as the system prompt
    if unknown and "-s" not in sys.argv and "--system-prompt" not in sys.argv:
        args.system_prompt = " ".join(unknown)

    output, return_code = describe_codebase(
        args.directory,
        args.system_prompt,
        args.model
    )

    print(output)
    sys.exit(return_code)


if __name__ == "__main__":
    main()
