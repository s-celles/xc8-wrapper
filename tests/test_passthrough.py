"""
Tests for passthrough functionality in XC8 Wrapper

This module tests the --passthrough option that allows passing raw arguments to xc8-cc.
"""

import pytest
import shlex
from unittest.mock import Mock, patch
from typer.testing import CliRunner

from xc8_wrapper.cli import app


class TestPassthroughOption:
    """Test the --passthrough option functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()

    @patch("xc8_wrapper.core.validate_xc8_tool")
    @patch("xc8_wrapper.core.get_xc8_tool_path")
    @patch("subprocess.run")
    def test_passthrough_single_option(
        self, mock_subprocess, mock_get_path, mock_validate
    ):
        """Test passthrough with a single option"""
        # Mock setup
        mock_get_path.return_value = ("/path/to/xc8-cc", "v3.00")
        mock_validate.return_value = True
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        # Test command with passthrough
        result = self.runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "--passthrough",
                "-mplib",
                "main.c",
            ],
        )

        assert result.exit_code == 0

        # Verify subprocess was called with passthrough argument
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert "-mplib" in call_args
        assert "main.c" in call_args

    @patch("xc8_wrapper.core.validate_xc8_tool")
    @patch("xc8_wrapper.core.get_xc8_tool_path")
    @patch("subprocess.run")
    def test_passthrough_multiple_options(
        self, mock_subprocess, mock_get_path, mock_validate
    ):
        """Test passthrough with multiple options"""
        # Mock setup
        mock_get_path.return_value = ("/path/to/xc8-cc", "v3.00")
        mock_validate.return_value = True
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        # Test command with multiple passthrough options
        result = self.runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "--passthrough",
                "-mplib -gdwarf-3 -mdownload-hex",
                "main.c",
            ],
        )

        assert result.exit_code == 0

        # Verify subprocess was called with all passthrough arguments
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert "-mplib" in call_args
        assert "-gdwarf-3" in call_args
        assert "-mdownload-hex" in call_args

    @patch("xc8_wrapper.core.validate_xc8_tool")
    @patch("xc8_wrapper.core.get_xc8_tool_path")
    @patch("subprocess.run")
    def test_passthrough_with_quoted_values(
        self, mock_subprocess, mock_get_path, mock_validate
    ):
        """Test passthrough with quoted values"""
        # Mock setup
        mock_get_path.return_value = ("/path/to/xc8-cc", "v3.00")
        mock_validate.return_value = True
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        # Test command with quoted passthrough options
        result = self.runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "--passthrough",
                '-mchecksum=0x1234 --fill="0xFF" -mserial="ABC123"',
                "main.c",
            ],
        )

        assert result.exit_code == 0

        # Verify subprocess was called with properly parsed arguments
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert "-mchecksum=0x1234" in call_args
        assert "--fill=0xFF" in call_args
        assert "-mserial=ABC123" in call_args

    @patch("xc8_wrapper.core.validate_xc8_tool")
    @patch("xc8_wrapper.core.get_xc8_tool_path")
    @patch("subprocess.run")
    def test_passthrough_combined_with_regular_options(
        self, mock_subprocess, mock_get_path, mock_validate
    ):
        """Test passthrough combined with regular CLI options"""
        # Mock setup
        mock_get_path.return_value = ("/path/to/xc8-cc", "v3.00")
        mock_validate.return_value = True
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        # Test command with both regular and passthrough options
        result = self.runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "-O2",
                "-v",  # Regular options
                "-D",
                "DEBUG=1",  # Regular define
                "--passthrough",
                "-mplib -gdwarf-3",  # Passthrough options
                "main.c",
            ],
        )

        assert result.exit_code == 0

        # Verify subprocess was called with both regular and passthrough arguments
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]

        # Regular options should be present
        assert "-O2" in call_args
        assert "-v" in call_args
        assert "-DDEBUG=1" in call_args

        # Passthrough options should be present
        assert "-mplib" in call_args
        assert "-gdwarf-3" in call_args

    def test_passthrough_invalid_syntax(self):
        """Test passthrough with invalid syntax"""
        result = self.runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "--passthrough",
                'invalid "unclosed quote',
                "main.c",
            ],
        )
        # Should exit with error due to invalid quoting
        assert result.exit_code == 1
        # The error message appears in logs, so we check the logs were generated
        # or that the command failed as expected
        assert result.exception is not None or result.exit_code == 1

    def test_passthrough_help_in_cli_reference(self):
        """Test that passthrough option appears in help"""
        result = self.runner.invoke(app, ["cc", "--help"])

        assert result.exit_code == 0
        assert "--passthrough" in result.output
        assert "Pass options directly to xc8-cc" in result.output

    @patch("xc8_wrapper.core.validate_xc8_tool")
    @patch("xc8_wrapper.core.get_xc8_tool_path")
    @patch("subprocess.run")
    def test_passthrough_empty_string(
        self, mock_subprocess, mock_get_path, mock_validate
    ):
        """Test passthrough with empty string"""
        # Mock setup
        mock_get_path.return_value = ("/path/to/xc8-cc", "v3.00")
        mock_validate.return_value = True
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        # Test command with empty passthrough
        result = self.runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "--passthrough",
                "",
                "main.c",
            ],
        )

        assert result.exit_code == 0

        # Should work normally, just no extra arguments added
        mock_subprocess.assert_called_once()

    def test_passthrough_short_option(self):
        """Test passthrough short option -p"""
        result = self.runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC16F877A",
                "--xc8-version",
                "3.00",
                "-p",
                "-mplib",
                "main.c",
            ],
        )

        # Should work the same as --passthrough
        # We can't easily test the subprocess call without mocking,
        # but we can test that it doesn't immediately fail
        assert "Invalid passthrough syntax" not in result.output


class TestPassthroughParsing:
    """Test the shlex parsing used in passthrough"""

    def test_shlex_simple_options(self):
        """Test parsing simple options"""
        args = shlex.split("-mplib -gdwarf-3")
        expected = ["-mplib", "-gdwarf-3"]
        assert args == expected

    def test_shlex_options_with_values(self):
        """Test parsing options with values"""
        args = shlex.split("-mchecksum=0x1234 --fill=0xFF")
        expected = ["-mchecksum=0x1234", "--fill=0xFF"]
        assert args == expected

    def test_shlex_quoted_values(self):
        """Test parsing quoted values"""
        args = shlex.split('-mserial="ABC 123" --output="my file.hex"')
        expected = ["-mserial=ABC 123", "--output=my file.hex"]
        assert args == expected

    def test_shlex_mixed_quoting(self):
        """Test parsing with mixed quoting styles"""
        args = shlex.split("""--define='VERSION="1.0"' -DNAME='"MyProject"'""")
        expected = ['--define=VERSION="1.0"', '-DNAME="MyProject"']
        assert args == expected

    def test_shlex_invalid_syntax(self):
        """Test that invalid syntax raises ValueError"""
        with pytest.raises(ValueError):
            shlex.split('unclosed "quote string')


class TestPassthroughIntegration:
    """Integration tests for passthrough functionality"""

    def test_passthrough_common_xc8_options(self):
        """Test passthrough with common XC8 options that aren't in the CLI"""
        runner = CliRunner()

        common_options = [
            "-mplib",
            "-gdwarf-3",
            "-mdownload-hex",
            "-mresetbits",
            "-mconfig",
            "--memorysummary=memory.xml",
            "--fill=0xFF",
        ]

        for option in common_options:
            result = runner.invoke(
                app,
                [
                    "cc",
                    "--cpu",
                    "PIC16F877A",
                    "--xc8-version",
                    "3.00",
                    "--passthrough",
                    option,
                    "main.c",
                ],
            )

            # Should not fail with syntax errors
            assert "Invalid passthrough syntax" not in result.output

    def test_passthrough_complex_real_world_example(self):
        """Test a complex real-world passthrough example"""
        runner = CliRunner()

        # Complex command that might be used in production
        passthrough_opts = (
            "-mplib -gdwarf-3 -mdownload-hex "
            "-mchecksum=0x1234 --fill=0xFF "
            "--memorysummary=memory.xml "
            "-mserial=ABC123"
        )

        result = runner.invoke(
            app,
            [
                "cc",
                "--cpu",
                "PIC18F4550",
                "--xc8-version",
                "3.00",
                "-O2",
                "-v",  # Regular options
                "-I",
                "./include",
                "-I",
                "./lib",  # Include paths
                "-D",
                "DEBUG=1",
                "-D",
                "VERSION=100",  # Defines
                "--passthrough",
                passthrough_opts,  # Passthrough
                "src/main.c",
                "src/uart.c",
                "src/spi.c",  # Multiple files
            ],
        )

        # Should not fail with syntax errors
        assert "Invalid passthrough syntax" not in result.output


class TestPassthroughSecurity:
    """Test security measures for passthrough arguments"""

    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()

    @patch("xc8_wrapper.core.validate_xc8_tool")
    @patch("xc8_wrapper.core.get_xc8_tool_path")
    def test_passthrough_blocks_file_traversal(self, mock_get_path, mock_validate):
        """Test that file traversal attempts are blocked"""
        # Mock setup
        mock_get_path.return_value = ("/path/to/xc8-cc", "v3.00")
        mock_validate.return_value = True

        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "/etc/shadow",
        ]

        for dangerous_path in dangerous_paths:
            result = self.runner.invoke(
                app,
                [
                    "cc",
                    "--cpu",
                    "PIC16F876A",
                    "--passthrough",
                    f"-I {dangerous_path}",
                    "test.c",
                ],
            )
            # Should exit with error due to security validation
            assert result.exit_code != 0, (
                f"File traversal should be blocked: {dangerous_path}"
            )

    @patch("xc8_wrapper.core.validate_xc8_tool")
    @patch("xc8_wrapper.core.get_xc8_tool_path")
    @patch("subprocess.run")
    def test_passthrough_allows_legitimate_compiler_options(
        self, mock_subprocess, mock_get_path, mock_validate
    ):
        """Test that legitimate compiler options are still allowed"""
        # Mock setup
        mock_get_path.return_value = ("/path/to/xc8-cc", "v3.00")
        mock_validate.return_value = True
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

        safe_args = [
            "-mplib",
            "-gdwarf-3",
            "--fill=0xFF",
            "-mchecksum=0x1234",
            "-Wl,--gc-sections",
            "-fdata-sections",
        ]

        for safe_arg in safe_args:
            result = self.runner.invoke(
                app,
                [
                    "cc",
                    "--cpu",
                    "PIC16F876A",
                    "--passthrough",
                    safe_arg,
                    "-###",  # Dry run mode
                    "test.c",
                ],
            )
            # Should succeed without security errors
            assert result.exit_code == 0, f"Safe argument should be allowed: {safe_arg}"
            assert "Security warning" not in result.stdout


if __name__ == "__main__":
    pytest.main([__file__])
