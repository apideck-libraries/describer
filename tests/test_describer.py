"""Tests for the describer package."""

import unittest
from unittest.mock import patch, MagicMock
from describer.core import describe_codebase


class TestDescriber(unittest.TestCase):
    """Test cases for the describer package."""

    @patch('subprocess.Popen')
    def test_describe_codebase_success(self, mock_popen):
        """Test that describe_codebase works correctly when processes succeed."""
        # Set up the mock to simulate successful execution
        mock_process = MagicMock()
        mock_process.stdout = MagicMock()
        mock_process.communicate.return_value = ("Test output", None)
        mock_process.wait.return_value = 0

        mock_popen.return_value = mock_process

        # Call the function
        output, return_code = describe_codebase("test_dir")

        # Assertions
        self.assertEqual(output, "Test output")
        self.assertEqual(return_code, 0)

        # Verify the correct commands were called
        calls = mock_popen.call_args_list
        self.assertEqual(len(calls), 2)  # Two processes should be created

        # First call should be to files-to-prompt
        self.assertEqual(calls[0][0][0][0], "files-to-prompt")

        # Second call should be to llm
        self.assertEqual(calls[1][0][0][0], "llm")

    @patch('subprocess.Popen')
    def test_describe_codebase_error(self, mock_popen):
        """Test that describe_codebase handles errors gracefully."""
        # Set up the mock to simulate an exception
        mock_popen.side_effect = Exception("Test error")

        # Call the function
        output, return_code = describe_codebase("test_dir")

        # Assertions
        self.assertEqual(output, "Test error")
        self.assertEqual(return_code, 1)


if __name__ == '__main__':
    unittest.main()
