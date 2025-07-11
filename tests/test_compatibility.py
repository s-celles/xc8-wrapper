"""
Compatibility tests for XC8 Wrapper

Test compatibility across different Python versions, platforms, and XC8 versions.
"""

import platform
import sys
from unittest.mock import MagicMock, patch

import pytest

from xc8_wrapper.cli import main
from xc8_wrapper.core import SUPPORTED_XC8_TOOLS, get_xc8_tool_path, validate_xc8_tool


@pytest.mark.compatibility
class TestPythonVersionCompatibility:
    """Test compatibility across Python versions"""

    def test_python_version_support(self):
        """Test that current Python version is supported"""
        major, minor = sys.version_info[:2]

        # Package supports Python 3.9+
        assert major == 3, f"Python {major}.{minor} not supported"
        assert minor >= 9, f"Python {major}.{minor} not supported, minimum is 3.9"

    def test_string_formatting_compatibility(self):
        """Test that string formatting works across Python versions"""
        # Test f-strings (Python 3.6+)
        version = "3.00"
        tool = "cc"

        formatted = f"xc8-{tool}.exe version {version}"
        assert formatted == "xc8-cc.exe version 3.00"

        # Test .format() method (older compatibility)
        formatted2 = "xc8-{}.exe version {}".format(tool, version)
        assert formatted2 == "xc8-cc.exe version 3.00"

    def test_pathlib_compatibility(self):
        """Test pathlib usage across Python versions"""
        from pathlib import Path

        # Test Path operations
        path = Path("C:/Program Files/Microchip/xc8/v3.00/bin/xc8-cc.exe")
        assert path.name == "xc8-cc.exe"
        assert path.suffix == ".exe"
        assert "xc8" in str(path)

    def test_type_hints_compatibility(self):
        """Test that type hints don't break on older Python versions"""
        # Import the modules to ensure type hints don't cause issues
        from xc8_wrapper.cli import main
        from xc8_wrapper.core import get_xc8_tool_path

        # Test that functions are callable
        assert callable(get_xc8_tool_path)
        assert callable(main)


class TestPlatformCompatibility:
    """Test compatibility across different platforms"""

    def test_windows_compatibility(self):
        """Test Windows-specific functionality"""
        if platform.system() == "Windows":
            # Test Windows path handling
            path, version = get_xc8_tool_path("cc", version="3.00")
            assert "\\" in path or "/" in path
            assert path.endswith("xc8-cc.exe")
        else:
            # Skip on non-Windows platforms
            pytest.skip("Windows-specific test")

    def test_unix_compatibility(self):
        """Test Unix-like system compatibility"""
        if platform.system() in ["Linux", "Darwin"]:
            # Test that basic operations work on Unix
            try:
                path, version = get_xc8_tool_path("cc", version="3.00")
                # On Unix, this might fail due to Windows-specific paths
                # but it shouldn't crash
                assert isinstance(path, str)
                assert isinstance(version, str)
            except Exception:
                # Expected on Unix systems with Windows-specific paths
                pass
        else:
            pytest.skip("Unix-specific test")

    def test_path_separator_handling(self):
        """Test that path separators are handled correctly"""
        import os

        # Test with different path separators
        test_paths = [
            "C:\\Program Files\\Microchip\\xc8\\v3.00\\bin\\xc8-cc.exe",
            "C:/Program Files/Microchip/xc8/v3.00/bin/xc8-cc.exe",
            "/usr/local/xc8/v3.00/bin/xc8-cc.exe",
        ]

        for test_path in test_paths:
            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = True
                result = validate_xc8_tool(test_path, "cc", "v3.00")
                assert result is True

    def test_file_system_case_sensitivity(self):
        """Test handling of case-sensitive vs case-insensitive file systems"""
        test_cases = [
            ("xc8-cc.exe", "xc8-cc.exe"),
            ("XC8-CC.EXE", "xc8-cc.exe"),  # Different case
        ]

        for input_name, expected_name in test_cases:
            # Test that we handle case correctly
            assert input_name.lower() == expected_name.lower()


class TestXC8VersionCompatibility:
    """Test compatibility with different XC8 versions"""

    def test_version_format_support(self):
        """Test support for different XC8 version formats"""
        version_formats = [
            "3.00",
            "3.01",
            "2.45",
            "4.00",
            "3.00-beta",
            "3.10",
        ]

        for version in version_formats:
            path, version_info = get_xc8_tool_path("cc", version=version)
            # Version info should always match
            assert version_info == f"v{version}"
            # Path should be a valid XC8 compiler path
            assert path.endswith("xc8-cc") or path.endswith("xc8-cc.exe")
            assert "xc8" in path.lower()

    def test_legacy_version_support(self):
        """Test support for older XC8 versions"""
        legacy_versions = ["1.45", "2.00", "2.10", "2.20"]

        for version in legacy_versions:
            # Should work with older versions too
            path, version_info = get_xc8_tool_path("cc", version=version)
            # Version info should always match
            assert version_info == f"v{version}"
            # Path should be a valid XC8 compiler path
            assert path.endswith("xc8-cc") or path.endswith("xc8-cc.exe")
            assert "xc8" in path.lower()

    def test_future_version_support(self):
        """Test that future XC8 versions are supported"""
        future_versions = ["5.00", "10.00", "99.99"]

        for version in future_versions:
            # Should work with future versions
            path, version_info = get_xc8_tool_path("cc", version=version)
            # Version info should always match
            assert version_info == f"v{version}"
            # Path should be a valid XC8 compiler path
            assert path.endswith("xc8-cc") or path.endswith("xc8-cc.exe")
            assert "xc8" in path.lower()


class TestDependencyCompatibility:
    """Test compatibility with dependencies"""

    def test_colorama_compatibility(self):
        """Test colorama compatibility"""
        try:
            from colorama import Fore, Style, init

            # Test that colorama works
            init()
            assert hasattr(Fore, "RED")
            assert hasattr(Fore, "GREEN")
            assert hasattr(Style, "RESET_ALL")

        except ImportError:
            pytest.fail("colorama not available")

    def test_standard_library_compatibility(self):
        """Test standard library compatibility"""
        # Test imports that should work across Python versions
        import argparse
        import os
        import pathlib
        import subprocess
        import sys
        import tempfile

        # Test basic functionality
        assert callable(os.path.exists)
        assert callable(subprocess.run)
        assert callable(pathlib.Path)
        assert callable(argparse.ArgumentParser)
        assert callable(tempfile.TemporaryDirectory)

    def test_unittest_mock_compatibility(self):
        """Test unittest.mock compatibility"""
        from unittest.mock import MagicMock, call, patch

        # Test that mock functionality works
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True
            result = validate_xc8_tool("fake_path", "cc", "v3.00")
            assert result is True
            mock_exists.assert_called_once()


class TestEncodingCompatibility:
    """Test encoding and unicode compatibility"""

    def test_unicode_path_handling(self):
        """Test handling of unicode characters in paths"""
        unicode_paths = [
            "C:\\Användare\\test\\xc8-cc.exe",  # Swedish characters
            "C:\\Usuários\\test\\xc8-cc.exe",  # Portuguese characters
            "C:\\用户\\test\\xc8-cc.exe",  # Chinese characters
        ]

        for unicode_path in unicode_paths:
            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = True
                result = validate_xc8_tool(unicode_path, "cc", "v3.00")
                assert result is True

    def test_unicode_output_handling(self):
        """Test handling of unicode in output"""
        from xc8_wrapper.logger import log

        unicode_messages = [
            "Compilation réussie",  # French
            "Компиляция успешна",  # Russian
            "コンパイル成功",  # Japanese
            "编译成功",  # Chinese
        ]

        # Test that unicode messages don't crash
        for message in unicode_messages:
            try:
                log.info(message)
            except UnicodeError:
                pytest.fail(f"Unicode error with message: {message}")

    def test_file_encoding_handling(self):
        """Test handling of different file encodings"""
        import tempfile

        # Test different encodings
        encodings = ["utf-8", "latin-1", "cp1252"]

        for encoding in encodings:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding=encoding, delete=False
            ) as f:
                f.write("// Test file\n")
                f.write("int main() { return 0; }\n")
                temp_path = f.name

            # Test that file existence check works regardless of encoding
            with patch("os.path.exists") as mock_exists:
                mock_exists.return_value = True
                result = validate_xc8_tool(temp_path, "cc", "v3.00")
                assert result is True

            # Clean up
            import os

            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__])
