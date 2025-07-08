"""
Tests for XC8 Wrapper Core Module

Comprehensive test suite for the XC8 wrapper core functionality.
"""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from xc8_wrapper.core import (
    SUPPORTED_XC8_TOOLS,
    Colors,
    get_xc8_tool_path,
    handle_cc_tool,
    print_colored,
    run_command,
    validate_xc8_tool,
)


@pytest.mark.unit
@pytest.mark.core
class TestXC8ToolPath:
    """Test XC8 tool path resolution"""

    def test_get_xc8_tool_path_with_version(self):
        """Test getting tool path with version"""
        path, version_info = get_xc8_tool_path("cc", version="3.00")

        # Verify the version info is correct
        assert version_info == "v3.00"

        # Verify the path contains the expected components
        assert "xc8" in path.lower()
        assert "bin" in path

        # Verify platform-specific executable name
        if sys.platform.startswith("win"):
            assert path.endswith("xc8-cc.exe")
            # Should be one of the Windows paths
            assert ("Program Files" in path and "Microchip" in path) or ("Program Files (x86)" in path and "Microchip" in path)
        else:
            assert path.endswith("xc8-cc")
            # Should be one of the Unix paths
            assert ("opt/microchip" in path) or ("Applications/microchip" in path) or ("usr/local/microchip" in path)

    def test_get_xc8_tool_path_with_custom_path(self):
        """Test getting tool path with custom path"""
        custom_path = r"C:\custom\path\xc8-cc.exe"
        path, version_info = get_xc8_tool_path("cc", custom_path=custom_path)
        assert path == custom_path
        assert version_info == "custom path"

    def test_get_xc8_tool_path_unsupported_tool(self):
        """Test error with unsupported tool"""
        with pytest.raises(ValueError, match="Unsupported XC8 tool"):
            get_xc8_tool_path("unsupported", version="3.00")

    def test_get_xc8_tool_path_no_version_or_path(self):
        """Test error when neither version nor path is provided"""
        with pytest.raises(ValueError, match="Either version or custom_path must be provided"):
            get_xc8_tool_path("cc")


class TestValidateXC8Tool:
    """Test XC8 tool validation"""

    @patch("pathlib.Path.exists")
    def test_validate_xc8_tool_exists(self, mock_exists):
        """Test validation when tool exists"""
        mock_exists.return_value = True
        result = validate_xc8_tool("fake_path", "cc", "v3.00")
        assert result is True

    @patch("pathlib.Path.exists")
    def test_validate_xc8_tool_not_exists(self, mock_exists):
        """Test validation when tool doesn't exist"""
        mock_exists.return_value = False
        result = validate_xc8_tool("fake_path", "cc", "v3.00")
        assert result is False


class TestConstants:
    """Test package constants"""

    def test_supported_tools_structure(self):
        """Test that SUPPORTED_XC8_TOOLS has correct structure"""
        assert isinstance(SUPPORTED_XC8_TOOLS, dict)
        assert "cc" in SUPPORTED_XC8_TOOLS

        cc_tool = SUPPORTED_XC8_TOOLS["cc"]
        assert "executable" in cc_tool
        assert "description" in cc_tool
        assert "default_operation" in cc_tool
        assert cc_tool["executable"] == "xc8-cc.exe"


class TestPrintColored:
    """Test colored output functionality"""

    @patch("builtins.print")
    def test_print_colored_basic(self, mock_print):
        """Test basic colored printing"""
        print_colored("Test message", Colors.RED)
        mock_print.assert_called_once()

    @patch("builtins.print")
    def test_print_colored_with_different_colors(self, mock_print):
        """Test colored printing with different colors"""
        colors = [Colors.RED, Colors.GREEN, Colors.YELLOW, Colors.BLUE, Colors.CYAN]
        for color in colors:
            print_colored("Test", color)
        assert mock_print.call_count == len(colors)


class TestRunCommand:
    """Test command execution functionality"""

    @patch("subprocess.run")
    def test_run_command_success(self, mock_run):
        """Test successful command execution"""
        mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

        result = run_command(["echo", "test"], "Test command")
        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_run):
        """Test failed command execution"""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Error")

        result = run_command(["false"], "Test command")
        assert result is False

    @patch("subprocess.run")
    def test_run_command_with_exception(self, mock_run):
        """Test command execution with exception"""
        mock_run.side_effect = FileNotFoundError("Command not found")

        result = run_command(["nonexistent"], "Test command")
        assert result is False


class TestHandleCCTool:
    """Test CC tool handling functionality"""

    @patch("xc8_wrapper.core.validate_xc8_tool")
    @patch("xc8_wrapper.core.get_xc8_tool_path")
    @patch("xc8_wrapper.core.run_command")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.iterdir")
    def test_handle_cc_tool_success(
        self, mock_iterdir, mock_mkdir, mock_stat, mock_exists, mock_run, mock_get_path, mock_validate
    ):
        """Test successful CC tool handling"""
        # Setup mocks
        mock_get_path.return_value = (r"C:\xc8\bin\xc8-cc.exe", "v3.00")
        mock_validate.return_value = True
        mock_exists.return_value = True
        mock_run.return_value = True

        # Mock stat result for file size
        stat_result = MagicMock()
        stat_result.st_size = 1024
        mock_stat.return_value = stat_result

        # Mock directory listing
        mock_file = MagicMock()
        mock_file.name = "main.hex"
        mock_file.is_file.return_value = True
        mock_file.is_dir.return_value = False
        mock_file.stat.return_value = stat_result
        mock_iterdir.return_value = [mock_file]

        # Create test args
        args = MagicMock()
        args.cpu = "PIC16F876A"
        args.xc8_version = "3.00"
        args.xc8_path = None
        args.source_dir = "src"
        args.build_dir = "build"
        args.main_c_file = "main.c"
        args.output_hex = "main.hex"
        args.output_elf = "main.elf"
        args.output_p1 = "main.p1"
        args.output_map = "main.map"
        args.memory_file = "memoryfile.xml"
        args.optimize = None
        args.define = []
        args.undefine = []
        args.include = []
        args.keep_comments = False
        args.preprocess_only = False
        args.list_headers = False
        args.list_macros = False
        args.compile_only = False
        args.assembly_only = False
        args.verbose = False
        args.suppress_warnings = False
        args.save_temps = False
        args.std = None
        args.compile_flag = []
        args.link_flag = []

        # Test
        handle_cc_tool(args)

        # Verify calls
        mock_get_path.assert_called_once()
        mock_validate.assert_called_once()
        mock_run.assert_called()

    @patch("xc8_wrapper.core.get_xc8_tool_path")
    @patch("xc8_wrapper.core.validate_xc8_tool")
    def test_handle_cc_tool_invalid_tool(self, mock_validate, mock_get_path):
        """Test CC tool handling with invalid tool"""
        mock_get_path.return_value = (r"C:\xc8\bin\xc8-cc.exe", "v3.00")
        mock_validate.return_value = False

        args = MagicMock()
        args.cpu = "PIC16F876A"
        args.xc8_version = "3.00"
        args.xc8_path = None

        with pytest.raises(SystemExit):
            handle_cc_tool(args)

    @patch("os.path.exists")
    def test_handle_cc_tool_missing_source_dir(self, mock_exists):
        """Test CC tool handling with missing source directory"""

        def exists_side_effect(path):
            # Return False only for source directory, True for other paths
            if "src" in path and "main.c" in path:
                return False
            return True

        mock_exists.side_effect = exists_side_effect

        args = MagicMock()
        args.cpu = "PIC16F876A"
        args.xc8_version = "3.00"
        args.xc8_path = None
        args.source_dir = "nonexistent"
        args.main_c_file = "main.c"

        with pytest.raises(SystemExit):
            handle_cc_tool(args)


if __name__ == "__main__":
    pytest.main([__file__])
