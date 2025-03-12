"""Tests for the output file feature."""

import unittest
from unittest.mock import patch, MagicMock, mock_open
from describer.core import describe_codebase, format_markdown


class TestOutputFile(unittest.TestCase):
    """Test cases for the output file feature."""

    @patch('subprocess.Popen')
    @patch('subprocess.check_output')
    @patch('builtins.open', new_callable=mock_open)
    @patch('describer.core.format_markdown')
    def test_describe_codebase_output_file(self, mock_format, mock_file, mock_check_output, mock_popen):
        """Test that describe_codebase writes to file when output_file is specified."""
        # Set up the mock to simulate successful execution
        mock_process = MagicMock()
        mock_process.stdout = MagicMock()
        mock_process.communicate.return_value = ("Test output", None)
        mock_process.wait.return_value = 0

        mock_popen.return_value = mock_process

        # Mock the check_output call to return a simple file structure
        mock_check_output.return_value = "file.txt\n---\nContent"

        # Set up the format_markdown mock
        mock_format.return_value = "Formatted test output"

        # Call the function with output file
        output, return_code, file_count = describe_codebase("test_dir", output_file="test_output.md")

        # Assertions
        self.assertEqual(output, "Formatted test output")
        self.assertEqual(return_code, 0)
        self.assertEqual(file_count, 1)

        # Verify the format_markdown function was called with the correct input
        mock_format.assert_called_once_with("Test output")

        # Verify file was written to with the formatted output
        mock_file.assert_called_once_with("test_output.md", "w")
        mock_file().write.assert_called_once_with("Formatted test output")

    def test_format_markdown_function(self):
        """Test the format_markdown function's basic functionality."""
        # Test with multiple blank lines
        test_input = "# Title\n\n\n\nContent\n\n\nMore content"
        expected_output = "# Title\n\nContent\n\nMore content"

        result = format_markdown(test_input)
        self.assertEqual(result, expected_output)


if __name__ == '__main__':
    unittest.main()
