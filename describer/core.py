"""Core functionality for the describer package."""

import subprocess
import os
from typing import Optional, Tuple


def describe_codebase(
    directory_path: str,
    system_prompt: str = "architectural overview as markdown",
    model: str = "gemini-2.0-pro-exp-02-05"
) -> Tuple[str, int]:
    """
    Generate a description of a codebase using files-to-prompt and llm.

    Args:
        directory_path: Path to the directory to analyze
        system_prompt: System prompt to use for the LLM
        model: LLM model to use

    Returns:
        Tuple of (output, return_code)
    """
    try:
        # Run files-to-prompt
        files_process = subprocess.Popen(
            ["files-to-prompt", directory_path, "-c"],
            stdout=subprocess.PIPE,
            text=True
        )

        # Pipe output to llm
        llm_process = subprocess.Popen(
            ["llm", "-m", model, "-s", system_prompt],
            stdin=files_process.stdout,
            stdout=subprocess.PIPE,
            text=True
        )

        # Close the files-to-prompt stdout (we've already piped it to llm)
        if files_process.stdout:
            files_process.stdout.close()

        # Get the output from llm
        output, _ = llm_process.communicate()

        # Wait for all processes to complete
        return_code = llm_process.wait()
        files_process.wait()

        return output, return_code
    except Exception as e:
        return str(e), 1
