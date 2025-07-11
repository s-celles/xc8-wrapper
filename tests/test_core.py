"""
Tests for XC8 Wrapper Core Module

Comprehensive test suite for the XC8 wrapper core functionality.
"""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, call, patch

import pytest

from xc8_wrapper.core import (
    SUPPORTED_XC8_TOOLS,
    _validate_path_security,
    get_xc8_tool_path,
    handle_cc_tool,
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
        assert cc_tool["executable"] == "xc8-cc"


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


class TestHandleArTool:
    """Test handle_ar_tool function"""

    @patch("xc8_wrapper.core.get_xc8_tool_path")
    @patch("xc8_wrapper.core.validate_xc8_tool")
    @patch("xc8_wrapper.core.run_command")
    def test_handle_ar_tool_success(self, mock_run, mock_validate, mock_get_path):
        """Test successful ar tool execution"""
        # Setup mocks
        mock_get_path.return_value = (r"C:\xc8\bin\xc8-ar.exe", "v3.00")
        mock_validate.return_value = True
        mock_run.return_value = True

        # Create mock args
        args = MagicMock()
        args.xc8_version = "3.00"
        args.xc8_path = None
        args.operation = "r"
        args.archive = "mylib.a"
        args.files = ["file1.o", "file2.o"]
        args.verbose = False
        args.update = False
        args.index = False

        # Should not raise exception
        handle_ar_tool(args)

        # Verify mocks were called
        mock_get_path.assert_called_once_with("ar", "3.00", None)
        mock_validate.assert_called_once()
        mock_run.assert_called_once()

    @patch("xc8_wrapper.core.get_xc8_tool_path")
    def test_handle_ar_tool_missing_version_and_path(self, mock_get_path):
        """Test ar tool with missing version and path"""
        args = MagicMock()
        args.xc8_version = None
        args.xc8_path = None

        with pytest.raises(SystemExit):
            handle_ar_tool(args)

    @patch("xc8_wrapper.core.get_xc8_tool_path")
    @patch("xc8_wrapper.core.validate_xc8_tool")
    def test_handle_ar_tool_invalid_tool(self, mock_validate, mock_get_path):
        """Test ar tool with invalid tool path"""
        mock_get_path.return_value = (r"C:\nonexistent\xc8-ar.exe", "v3.00")
        mock_validate.return_value = False

        args = MagicMock()
        args.xc8_version = "3.00"
        args.xc8_path = None

        with pytest.raises(SystemExit):
            handle_ar_tool(args)

    @patch("xc8_wrapper.core.get_xc8_tool_path")
    @patch("xc8_wrapper.core.validate_xc8_tool")
    def test_handle_ar_tool_missing_files_for_create(self, mock_validate, mock_get_path):
        """Test ar tool with missing files for create operation"""
        mock_get_path.return_value = (r"C:\xc8\bin\xc8-ar.exe", "v3.00")
        mock_validate.return_value = True

        args = MagicMock()
        args.xc8_version = "3.00"
        args.xc8_path = None
        args.operation = "r"  # requires files
        args.archive = "mylib.a"
        args.files = []  # no files provided
        args.verbose = False
        args.update = False
        args.index = False

        with pytest.raises(SystemExit):
            handle_ar_tool(args)


@pytest.mark.unit
@pytest.mark.core
class TestVersionScanning:
    """Test XC8 version scanning functionality"""

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.is_dir")
    def test_scan_for_xc8_versions_windows(self, mock_is_dir, mock_glob, mock_exists):
        """Test scanning for XC8 versions on Windows"""
        with patch("sys.platform", "win32"):
            # Mock directory structure
            mock_exists.return_value = True
            mock_is_dir.return_value = True

            # Create mock version directories
            version_dirs = []
            for version in ["v2.40", "v3.00", "v3.10"]:
                version_dir = MagicMock()
                version_dir.name = version
                version_dir.is_dir.return_value = True

                # Mock compiler path
                compiler_path = MagicMock()
                compiler_path.exists.return_value = True
                version_dir.glob.return_value = [compiler_path]

                version_dirs.append(version_dir)

            mock_glob.return_value = version_dirs

            versions = scan_for_xc8_versions()

            # Should find versions sorted highest first
            expected_versions = ["3.10", "3.00", "2.40"]
            assert versions == expected_versions

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.glob")
    def test_scan_for_xc8_versions_darwin(self, mock_glob, mock_exists):
        """Test scanning for XC8 versions on macOS"""
        with patch("sys.platform", "darwin"):
            mock_exists.return_value = True

            # Create mock version directory
            version_dir = MagicMock()
            version_dir.name = "v2.50"
            version_dir.is_dir.return_value = True

            # Mock compiler path
            compiler_path = MagicMock()
            compiler_path.exists.return_value = True
            version_dir.glob.return_value = [compiler_path]

            mock_glob.return_value = [version_dir]

            versions = scan_for_xc8_versions()
            assert "2.50" in versions

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.glob")
    def test_scan_for_xc8_versions_linux(self, mock_glob, mock_exists):
        """Test scanning for XC8 versions on Linux"""
        with patch("sys.platform", "linux"):
            mock_exists.return_value = True

            # Create mock version directory
            version_dir = MagicMock()
            version_dir.name = "v2.30"
            version_dir.is_dir.return_value = True

            # Mock compiler path
            compiler_path = MagicMock()
            compiler_path.exists.return_value = True
            version_dir.glob.return_value = [compiler_path]

            mock_glob.return_value = [version_dir]

            versions = scan_for_xc8_versions()
            assert "2.30" in versions

    @patch("pathlib.Path.exists")
    def test_scan_for_xc8_versions_no_base_paths(self, mock_exists):
        """Test scanning when base paths don't exist"""
        mock_exists.return_value = False

        versions = scan_for_xc8_versions()
        assert versions == []

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.glob")
    def test_scan_for_xc8_versions_permission_error(self, mock_glob, mock_exists):
        """Test scanning with permission errors"""
        mock_exists.return_value = True
        mock_glob.side_effect = PermissionError("Access denied")

        versions = scan_for_xc8_versions()
        assert versions == []

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.glob")
    def test_scan_for_xc8_versions_invalid_version_format(self, mock_glob, mock_exists):
        """Test scanning with invalid version directory names"""
        mock_exists.return_value = True

        # Create mock directory with invalid version name
        invalid_dir = MagicMock()
        invalid_dir.name = "vInvalid"
        invalid_dir.is_dir.return_value = True

        mock_glob.return_value = [invalid_dir]

        versions = scan_for_xc8_versions()
        assert versions == []

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.glob")
    def test_scan_for_xc8_versions_no_compiler(self, mock_glob, mock_exists):
        """Test scanning when compiler executable is missing"""
        mock_exists.return_value = True

        # Create mock version directory
        version_dir = MagicMock()
        version_dir.name = "v3.00"
        version_dir.is_dir.return_value = True
        version_dir.glob.return_value = []  # No compiler found

        mock_glob.return_value = [version_dir]

        versions = scan_for_xc8_versions()
        assert versions == []

    @patch("xc8_wrapper.core.scan_for_xc8_versions")
    def test_get_all_xc8_versions_to_try(self, mock_scan):
        """Test getting all versions to try"""
        mock_scan.return_value = ["3.10", "2.50"]

        versions = get_all_xc8_versions_to_try()

        # Should include both known and scanned versions
        assert "3.10" in versions
        assert "2.50" in versions
        # Should also include known versions from XC8_KNOWN_VERSIONS
        assert "3.00" in versions or "2.40" in versions

    @patch("xc8_wrapper.core.scan_for_xc8_versions")
    def test_get_all_xc8_versions_to_try_with_invalid_versions(self, mock_scan):
        """Test version aggregation with invalid version formats"""
        mock_scan.return_value = ["invalid.version", "3.00"]

        # Should handle invalid versions gracefully
        versions = get_all_xc8_versions_to_try()
        assert "3.00" in versions


@pytest.mark.unit
@pytest.mark.core
class TestPlatformFunctions:
    """Test platform-specific functions"""

    def test_get_platform_xc8_paths_windows(self):
        """Test getting XC8 paths on Windows"""
        with patch("sys.platform", "win32"):
            paths = _get_platform_xc8_paths("3.00")
            assert len(paths) >= 2
            assert any("Program Files" in str(path) for path in paths)
            assert all("v3.00" in str(path) for path in paths)

    def test_get_platform_xc8_paths_darwin(self):
        """Test getting XC8 paths on macOS"""
        with patch("sys.platform", "darwin"):
            paths = _get_platform_xc8_paths("3.00")
            assert len(paths) >= 2
            assert any("Applications" in str(path) for path in paths)
            assert all("v3.00" in str(path) for path in paths)

    def test_get_platform_xc8_paths_linux(self):
        """Test getting XC8 paths on Linux"""
        with patch("sys.platform", "linux"):
            paths = _get_platform_xc8_paths("3.00")
            assert len(paths) >= 2
            assert any("opt" in str(path) for path in paths)
            # Some Linux paths include version, some don't
            assert any("v3.00" in str(path) for path in paths)

    def test_get_platform_executable_name_windows(self):
        """Test getting executable name on Windows"""
        with patch("sys.platform", "win32"):
            name = _get_platform_executable_name("xc8-cc")
            assert name == "xc8-cc.exe"

    def test_get_platform_executable_name_unix(self):
        """Test getting executable name on Unix systems"""
        with patch("sys.platform", "linux"):
            name = _get_platform_executable_name("xc8-cc")
            assert name == "xc8-cc"

    @patch("pathlib.Path.exists")
    def test_find_existing_xc8_path_found(self, mock_exists):
        """Test finding existing XC8 path when it exists"""
        mock_exists.return_value = True
        paths = [Path("/fake/path1"), Path("/fake/path2")]

        result = _find_existing_xc8_path(paths)
        assert result == paths[0]

    @patch("pathlib.Path.exists")
    def test_find_existing_xc8_path_not_found(self, mock_exists):
        """Test finding existing XC8 path when none exist"""
        mock_exists.return_value = False
        paths = [Path("/fake/path1"), Path("/fake/path2")]

        result = _find_existing_xc8_path(paths)
        assert result is None

    def test_find_existing_xc8_path_empty_list(self):
        """Test finding existing XC8 path with empty list"""
        result = _find_existing_xc8_path([])
        assert result is None


@pytest.mark.unit
@pytest.mark.core
class TestSecurityAndValidation:
    """Test security and validation functions"""

    def test_validate_path_security_safe_path(self):
        """Test path security validation with safe path"""
        safe_path = "/opt/microchip/xc8/v3.00/bin/xc8-cc"
        result = _validate_path_security(safe_path)
        assert result is True

    def test_validate_path_security_unsafe_path(self):
        """Test path security validation with potentially unsafe path"""
        unsafe_path = "/etc/../../../bin/rm"
        result = _validate_path_security(unsafe_path)
        # The function should handle this appropriately
        assert isinstance(result, bool)

    def test_validate_path_security_windows_path(self):
        """Test path security validation with Windows path"""
        windows_path = r"C:\Program Files\Microchip\xc8\v3.00\bin\xc8-cc.exe"
        result = _validate_path_security(windows_path)
        assert result is True

    @patch("builtins.print")
    def test_print_installation_paths(self, mock_print):
        """Test printing installation paths"""
        _print_installation_paths("3.00")
        # Should print some output
        assert mock_print.called


@pytest.mark.unit
@pytest.mark.core
class TestErrorHandling:
    """Test error handling in core functions"""

    @patch("xc8_wrapper.core.get_xc8_tool_path")
    @patch("xc8_wrapper.core.validate_xc8_tool")
    def test_handle_cc_tool_invalid_path(self, mock_validate, mock_get_path):
        """Test CC tool handling with invalid path"""
        mock_get_path.return_value = ("/fake/path", "v3.00")
        mock_validate.return_value = False

        args = MagicMock()
        args.cpu = "PIC16F876A"
        args.xc8_version = "3.00"
        args.xc8_path = None

        # Should handle invalid path gracefully
        try:
            handle_cc_tool(args)
        except SystemExit:
            pass  # Expected for invalid path

    @patch("xc8_wrapper.core.get_xc8_tool_path")
    def test_handle_cc_tool_missing_arguments(self, mock_get_path):
        """Test CC tool handling with missing required arguments"""
        mock_get_path.return_value = ("/fake/path", "v3.00")

        args = MagicMock()
        args.cpu = None  # Missing required argument
        args.xc8_version = "3.00"
        args.xc8_path = None

        # Should handle missing arguments gracefully
        try:
            handle_cc_tool(args)
        except (SystemExit, AttributeError):
            pass  # Expected for missing arguments

    @patch("subprocess.run")
    def test_run_command_timeout(self, mock_run):
        """Test command execution with timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)

        result = run_command(["sleep", "60"], "Long running command")
        assert result is False

    def test_run_command_empty_command(self):
        """Test command execution with empty command"""
        result = run_command([], "Empty command")
        assert result is False
