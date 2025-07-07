"""
Tests for XC8 Wrapper

Basic test suite for the XC8 wrapper functionality.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from xc8_wrapper.core import get_xc8_tool_path, validate_xc8_tool, SUPPORTED_XC8_TOOLS


class TestXC8ToolPath:
    """Test XC8 tool path resolution"""

    def test_get_xc8_tool_path_with_version(self):
        """Test getting tool path with version"""
        path, version_info = get_xc8_tool_path("cc", version="3.00")
        expected_path = r"C:\Program Files\Microchip\xc8\v3.00\bin\xc8-cc.exe"
        assert path == expected_path
        assert version_info == "v3.00"

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
        with pytest.raises(
            ValueError, match="Either version or custom_path must be provided"
        ):
            get_xc8_tool_path("cc")


class TestValidateXC8Tool:
    """Test XC8 tool validation"""

    @patch("os.path.exists")
    def test_validate_xc8_tool_exists(self, mock_exists):
        """Test validation when tool exists"""
        mock_exists.return_value = True
        result = validate_xc8_tool("fake_path", "cc", "v3.00")
        assert result is True

    @patch("os.path.exists")
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


if __name__ == "__main__":
    pytest.main([__file__])
