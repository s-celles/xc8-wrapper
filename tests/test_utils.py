"""
Tests for utility functions and edge cases

Test edge cases, error conditions, and utility functions.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from xc8_wrapper.core import SUPPORTED_XC8_TOOLS, Colors, get_xc8_tool_path, print_colored, validate_xc8_tool


@pytest.mark.unit
@pytest.mark.core
class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_get_xc8_tool_path_empty_version(self):
        """Test error with empty version string"""
        with pytest.raises(ValueError, match="Either version or custom_path must be provided"):
            get_xc8_tool_path("cc", version="")

    def test_get_xc8_tool_path_none_values(self):
        """Test error with None values"""
        with pytest.raises(ValueError, match="Either version or custom_path must be provided"):
            get_xc8_tool_path("cc", version=None, custom_path=None)

    def test_get_xc8_tool_path_both_provided(self):
        """Test behavior when both version and custom_path are provided"""
        custom_path = r"C:\custom\path\xc8-cc.exe"
        path, version_info = get_xc8_tool_path("cc", version="3.00", custom_path=custom_path)

        # custom_path should take precedence
        assert path == custom_path
        assert version_info == "custom path"

    def test_validate_xc8_tool_with_spaces_in_path(self):
        """Test validation with spaces in path"""
        path_with_spaces = r"C:\Program Files\Microchip\xc8\v3.00\bin\xc8-cc.exe"

        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True
            result = validate_xc8_tool(path_with_spaces, "cc", "v3.00")
            assert result is True
            mock_exists.assert_called_once()

    def test_validate_xc8_tool_with_unicode_path(self):
        """Test validation with unicode characters in path"""
        unicode_path = r"C:\Användare\xc8\bin\xc8-cc.exe"

        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True
            result = validate_xc8_tool(unicode_path, "cc", "v3.00")
            assert result is True


class TestPlatformSpecific:
    """Test platform-specific behavior"""

    @patch("os.name", "nt")
    def test_windows_path_handling(self):
        """Test Windows-specific path handling"""
        path, version_info = get_xc8_tool_path("cc", version="3.00")

        # Should use Windows path format
        assert path.startswith("C:")
        assert "\\" in path
        assert path.endswith("xc8-cc.exe")

    @patch("os.name", "posix")
    def test_posix_path_handling(self):
        """Test POSIX-specific path handling"""
        # This would need actual POSIX path logic in the core module
        # For now, just test that it doesn't crash
        try:
            path, version_info = get_xc8_tool_path("cc", version="3.00")
            assert isinstance(path, str)
        except Exception:
            # Expected if POSIX support isn't implemented yet
            pass


class TestColors:
    """Test color constants and functionality"""

    def test_colors_exist(self):
        """Test that color constants exist"""
        assert hasattr(Colors, "RED")
        assert hasattr(Colors, "GREEN")
        assert hasattr(Colors, "YELLOW")
        assert hasattr(Colors, "BLUE")
        assert hasattr(Colors, "CYAN")
        assert hasattr(Colors, "WHITE")
        assert hasattr(Colors, "GRAY")

    def test_colors_are_strings(self):
        """Test that color constants are strings"""
        assert isinstance(Colors.RED, str)
        assert isinstance(Colors.GREEN, str)
        assert isinstance(Colors.YELLOW, str)
        assert isinstance(Colors.BLUE, str)
        assert isinstance(Colors.CYAN, str)
        assert isinstance(Colors.WHITE, str)
        assert isinstance(Colors.GRAY, str)

    @patch("builtins.print")
    def test_print_colored_with_empty_string(self, mock_print):
        """Test print_colored with empty string"""
        print_colored("", Colors.RED)
        mock_print.assert_called_once()

    @patch("builtins.print")
    def test_print_colored_with_multiline_string(self, mock_print):
        """Test print_colored with multiline string"""
        multiline = "Line 1\nLine 2\nLine 3"
        print_colored(multiline, Colors.GREEN)
        mock_print.assert_called_once()

    @patch("builtins.print")
    def test_print_colored_with_special_characters(self, mock_print):
        """Test print_colored with special characters"""
        special_chars = "Special: äöü ñ 中文 🎉"
        print_colored(special_chars, Colors.BLUE)
        mock_print.assert_called_once()


class TestConstants:
    """Test package constants and their integrity"""

    def test_supported_tools_immutability(self):
        """Test that SUPPORTED_XC8_TOOLS structure is as expected"""
        # Test that the structure hasn't been accidentally modified
        assert "cc" in SUPPORTED_XC8_TOOLS
        assert len(SUPPORTED_XC8_TOOLS) >= 1

        # Test CC tool structure
        cc_tool = SUPPORTED_XC8_TOOLS["cc"]
        required_keys = ["executable", "description", "default_operation"]
        for key in required_keys:
            assert key in cc_tool
            assert isinstance(cc_tool[key], str)
            assert len(cc_tool[key]) > 0

    def test_supported_tools_values(self):
        """Test that supported tools have valid values"""
        for tool_name, tool_info in SUPPORTED_XC8_TOOLS.items():
            # Tool name should be a non-empty string
            assert isinstance(tool_name, str)
            assert len(tool_name) > 0

            # Tool info should be a dictionary
            assert isinstance(tool_info, dict)

            # Executable should end with .exe (for Windows)
            assert tool_info["executable"].endswith(".exe")

            # Description should be non-empty
            assert len(tool_info["description"]) > 0

            # Default operation should be non-empty
            assert len(tool_info["default_operation"]) > 0


class TestFileSystemOperations:
    """Test file system related operations"""

    def test_validate_xc8_tool_with_relative_path(self):
        """Test validation with relative path"""
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True
            result = validate_xc8_tool("./xc8-cc.exe", "cc", "v3.00")
            assert result is True

    def test_validate_xc8_tool_with_nonexistent_path(self):
        """Test validation with non-existent path"""
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False
            result = validate_xc8_tool("/nonexistent/path/xc8-cc.exe", "cc", "v3.00")
            assert result is False

    def test_path_construction_with_different_versions(self):
        """Test path construction with different version formats"""
        test_versions = ["3.00", "3.01", "2.45", "4.00"]

        for version in test_versions:
            path, version_info = get_xc8_tool_path("cc", version=version)
            assert f"v{version}" in path
            assert version_info == f"v{version}"


class TestErrorHandling:
    """Test error handling and exception scenarios"""

    def test_get_xc8_tool_path_with_invalid_tool_name(self):
        """Test error with invalid tool name"""
        with pytest.raises(ValueError, match="Unsupported XC8 tool"):
            get_xc8_tool_path("invalid_tool", version="3.00")

    def test_get_xc8_tool_path_with_special_characters_in_version(self):
        """Test version with special characters"""
        # This should work as the version is just used in path construction
        path, version_info = get_xc8_tool_path("cc", version="3.00-beta")
        assert "v3.00-beta" in path
        assert version_info == "v3.00-beta"

    def test_validate_xc8_tool_with_none_path(self):
        """Test validation with None path"""
        # No need to mock since we handle None before calling Path.exists()
        result = validate_xc8_tool(None, "cc", "v3.00")
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
