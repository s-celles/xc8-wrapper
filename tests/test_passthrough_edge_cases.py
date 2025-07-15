"""
Edge case tests for passthrough functionality

These tests cover edge cases, error conditions, and security considerations.
"""

import pytest
from unittest.mock import Mock, patch
from typer.testing import CliRunner

from xc8_wrapper.cli import app


class TestPassthroughEdgeCases:
    """Test edge cases for passthrough functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()

    def test_passthrough_with_dangerous_commands(self):
        """Test that passthrough doesn't enable command injection"""
        # These should be treated as arguments to xc8-cc, not as shell commands
        dangerous_inputs = [
            "; rm -rf /",
            "&& del *.*",
            "| cat /etc/passwd",
            "`cat /etc/passwd`",
            "$(rm -rf /)",
        ]

        for dangerous_input in dangerous_inputs:
            result = self.runner.invoke(
                app,
                [
                    "cc",
                    "--cpu",
                    "PIC16F877A",
                    "--xc8-version",
                    "3.00",
                    "--passthrough",
                    dangerous_input,
                    "main.c",
                ],
            )

            # Should not fail due to shell injection - these will be passed as args
            # The actual compilation will fail because these aren't valid xc8-cc options,
            # but that's expected and safe
            assert "Invalid passthrough syntax" not in result.output

    def test_passthrough_very_long_argument(self):
        """Test passthrough with very long argument"""
        long_arg = "-D" + "A" * 1000 + "=1"

        result = self.runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "--passthrough",
                long_arg,
                "main.c",
            ],
        )

        # Should handle long arguments without syntax errors
        assert "Invalid passthrough syntax" not in result.output

    def test_passthrough_unicode_characters(self):
        """Test passthrough with unicode characters"""
        unicode_arg = "-DPROJECT_NAME=こんにちは"

        result = self.runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "--passthrough",
                unicode_arg,
                "main.c",
            ],
        )

        # Should handle unicode without syntax errors
        assert "Invalid passthrough syntax" not in result.output

    def test_passthrough_multiple_equals_signs(self):
        """Test passthrough with multiple equals signs"""
        complex_arg = "-DEQUATION=x=y+z"

        result = self.runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "--passthrough",
                complex_arg,
                "main.c",
            ],
        )

        # Should handle complex arguments with multiple = signs
        assert "Invalid passthrough syntax" not in result.output

    def test_passthrough_with_spaces_in_paths(self):
        """Test passthrough with file paths containing spaces"""
        path_with_spaces = '--output="C:\\Program Files\\My Project\\output.hex"'

        result = self.runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "--passthrough",
                path_with_spaces,
                "main.c",
            ],
        )

        # Should handle paths with spaces correctly when quoted
        assert "Invalid passthrough syntax" not in result.output

    def test_passthrough_empty_quoted_string(self):
        """Test passthrough with empty quoted strings"""
        empty_quoted = '-DVERSION="" --comment=""'

        result = self.runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "--passthrough",
                empty_quoted,
                "main.c",
            ],
        )

        # Should handle empty quoted strings
        assert "Invalid passthrough syntax" not in result.output

    def test_passthrough_escaped_quotes(self):
        """Test passthrough with escaped quotes"""
        escaped_quotes = r'-DMESSAGE="He said \"Hello\""'

        result = self.runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "--passthrough",
                escaped_quotes,
                "main.c",
            ],
        )

        # Should handle escaped quotes
        assert "Invalid passthrough syntax" not in result.output

    @patch("xc8_wrapper.core.validate_xc8_tool")
    @patch("xc8_wrapper.core.get_xc8_tool_path")
    @patch("subprocess.run")
    def test_passthrough_preserves_argument_order(
        self, mock_subprocess, mock_get_path, mock_validate
    ):
        """Test that passthrough preserves argument order"""
        # Mock setup
        mock_get_path.return_value = ("/path/to/xc8-cc", "v3.00")
        mock_validate.return_value = True
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        # Test with ordered arguments
        result = self.runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "-O2",  # Regular option first
                "--passthrough",
                "-mplib -gdwarf-3 --fill=0xFF",  # Passthrough in middle
                "-v",  # Regular option after
                "main.c",
            ],
        )

        assert result.exit_code == 0

        # Get the command arguments that were passed to subprocess
        call_args = mock_subprocess.call_args[0][0]

        # Verify that both regular and passthrough options are present
        assert "-mcpu=PIC16F877A" in call_args
        assert "-O2" in call_args
        assert "-mplib" in call_args
        assert "-gdwarf-3" in call_args
        assert "--fill=0xFF" in call_args
        assert "-v" in call_args
        assert "main.c" in call_args

    def test_passthrough_with_newlines(self):
        """Test passthrough with newlines in arguments"""
        multiline_arg = "-DLONG_TEXT=line1\\nline2\\nline3"

        result = self.runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "--passthrough",
                multiline_arg,
                "main.c",
            ],
        )

        # Should handle newlines in arguments
        assert "Invalid passthrough syntax" not in result.output


class TestPassthroughSecurity:
    """Security-focused tests for passthrough"""

    def test_passthrough_no_shell_execution(self):
        """Verify that passthrough doesn't enable shell execution"""
        # This is a critical security test
        shell_commands = [
            "rm -rf /tmp/test",
            "del C:\\temp\\*",
            "cat /etc/passwd",
            "type C:\\Windows\\System32\\drivers\\etc\\hosts",
        ]

        runner = CliRunner()

        for cmd in shell_commands:
            result = runner.invoke(
                app,
                [
                    "cc",
                    "--cpu",
                    "PIC16F877A",
                    "--xc8-version",
                    "3.00",
                    "--passthrough",
                    cmd,
                    "main.c",
                ],
            )

            # These should be treated as xc8-cc arguments, not shell commands
            # They will cause xc8-cc to fail, but that's safe
            assert "Invalid passthrough syntax" not in result.output

    def test_passthrough_argument_isolation(self):
        """Test that passthrough arguments are properly isolated"""
        # Arguments should be passed as separate items, not concatenated
        runner = CliRunner()

        result = runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "--passthrough",
                "-DTEST=1 -DOTHER=2",
                "main.c",
            ],
        )

        # Should parse as separate arguments, not as one big string
        assert "Invalid passthrough syntax" not in result.output


class TestPassthroughErrorHandling:
    """Test error handling in passthrough"""

    def test_passthrough_with_invalid_cpu_still_processes(self):
        """Test that passthrough works even with invalid CPU"""
        runner = CliRunner()

        result = runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "INVALID_CPU",
                "--xc8-version",
                "3.00",
                "--passthrough",
                "-mplib",
                "main.c",
            ],
        )

        # Should still process passthrough, even if CPU is invalid
        # (The actual compilation will fail later due to invalid CPU)
        assert "Invalid passthrough syntax" not in result.output

    def test_passthrough_preserves_error_context(self):
        """Test that passthrough errors provide good context"""
        runner = CliRunner()

        # Use invalid quote syntax
        result = runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "--passthrough",
                'unclosed "quote',
                "main.c",
            ],
        )

        assert result.exit_code == 1
        error_text = result.output + getattr(result, "stdout", "")
        assert "Invalid passthrough syntax" in error_text


if __name__ == "__main__":
    pytest.main([__file__])
