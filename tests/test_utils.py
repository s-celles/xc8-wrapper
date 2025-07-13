"""
Tests for utility functions and edge cases

Test edge cases, error conditions, and utility functions.
"""

from unittest.mock import patch

import pytest

from xc8_wrapper.core import SUPPORTED_XC8_TOOLS, get_xc8_tool_path, validate_xc8_tool


@pytest.mark.unit
@pytest.mark.core
class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_get_xc8_tool_path_empty_version(self):
        """Test auto-detection with empty version string"""
        # Empty version should trigger auto-detection
        result = get_xc8_tool_path("cc", version="")
        assert result is not None
        assert len(result) == 2
        path, version = result
        assert isinstance(path, str)
        assert isinstance(version, str)

    def test_get_xc8_tool_path_none_values(self):
        """Test auto-detection with None values"""
        # None values should trigger auto-detection
        result = get_xc8_tool_path("cc", version=None, custom_path=None)
        assert result is not None
        assert len(result) == 2
        path, version = result
        assert isinstance(path, str)
        assert isinstance(version, str)

    def test_get_xc8_tool_path_both_provided(self):
        """Test behavior when both version and custom_path are provided"""
        custom_path = r"C:\custom\path\xc8-cc.exe"
        path, version_info = get_xc8_tool_path(
            "cc", version="3.00", custom_path=custom_path
        )

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

    @patch("sys.platform", "win32")
    def test_windows_path_handling(self):
        """Test Windows-specific path handling"""
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False  # Force default path selection
            path, version_info = get_xc8_tool_path("cc", version="3.00")

            # Should use Windows path format
            assert "Program Files" in path
            assert path.endswith("xc8-cc.exe")
            assert version_info == "v3.00"

    @patch("sys.platform", "linux")
    def test_posix_path_handling(self):
        """Test POSIX-specific path handling"""
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False  # Force default path selection
            path, version_info = get_xc8_tool_path("cc", version="3.00")

            # Should use Linux path format (normalize path separators for cross-platform testing)
            normalized_path = path.replace("\\", "/")
            # Under Linux, the primary path is /opt/microchip/bin (non-versioned)
            # The versioned paths are fallback options
            assert (
                "/opt/microchip/bin" in normalized_path
                or "/usr/local/microchip/bin" in normalized_path
                or "/opt/microchip/xc8" in normalized_path
                or "/usr/local/microchip/xc8" in normalized_path
            )
            assert path.endswith("xc8-cc")  # No .exe on Linux
            assert version_info == "v3.00"


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

            # Executable should be a non-empty string (platform-agnostic)
            assert isinstance(tool_info["executable"], str)
            assert len(tool_info["executable"]) > 0

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
            # Version info should always match
            assert version_info == f"v{version}"
            # Path should be a valid XC8 compiler path
            assert path.endswith("xc8-cc") or path.endswith("xc8-cc.exe")
            assert "xc8" in path.lower()


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

        # Version info should always contain the version
        assert version_info == "v3.00-beta"

        # Path should be a valid XC8 compiler path
        assert path.endswith("xc8-cc") or path.endswith("xc8-cc.exe")
        assert "xc8" in path.lower()

    def test_validate_xc8_tool_with_none_path(self):
        """Test validation with None path"""
        # No need to mock since we handle None before calling Path.exists()
        result = validate_xc8_tool(None, "cc", "v3.00")
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
