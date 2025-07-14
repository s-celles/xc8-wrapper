"""
Simple tests for XC8 Installation Module

This module provides basic tests for the installation functionality using mocks
to avoid actual downloads and installations.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from xc8_wrapper.install import (
    get_platform_name,
    get_xc8_download_url,
    get_all_xc8_versions_to_try,
    is_xc8_installed,
    get_installed_xc8_version,
    install_xc8_if_needed,
)


class TestPlatformDetection:
    """Test platform detection functions"""

    def test_get_platform_name_windows(self):
        """Test Windows platform detection"""
        with patch("platform.system", return_value="Windows"):
            assert get_platform_name() == "windows"

    def test_get_platform_name_linux(self):
        """Test Linux platform detection"""
        with patch("platform.system", return_value="Linux"):
            assert get_platform_name() == "linux"

    def test_get_platform_name_macos(self):
        """Test macOS platform detection"""
        with patch("platform.system", return_value="Darwin"):
            assert get_platform_name() == "darwin"

    def test_get_platform_name_unsupported(self):
        """Test unsupported platform detection"""
        with patch("platform.system", return_value="FreeBSD"):
            with pytest.raises(ValueError, match="Unsupported platform"):
                get_platform_name()


class TestDownloadUrls:
    """Test download URL generation"""

    def test_get_xc8_download_url_windows(self):
        """Test Windows download URL generation"""
        url = get_xc8_download_url("3.00", "windows")
        assert "windows-x64-installer.exe" in url
        assert "xc8-v3.00" in url

    def test_get_xc8_download_url_linux(self):
        """Test Linux download URL generation"""
        url = get_xc8_download_url("3.00", "linux")
        assert "linux-x64-installer.run" in url
        assert "xc8-v3.00" in url

    def test_get_xc8_download_url_macos(self):
        """Test macOS download URL generation"""
        url = get_xc8_download_url("3.00", "darwin")
        assert "macos-x64-installer.dmg" in url
        assert "xc8-v3.00" in url


class TestVersionList:
    """Test version list functionality"""

    def test_get_all_xc8_versions_to_try(self):
        """Test that version list is returned"""
        versions = get_all_xc8_versions_to_try()
        assert isinstance(versions, list)
        assert len(versions) > 0
        # Should contain some common versions
        assert any("3." in version for version in versions)


class TestInstallationStatus:
    """Test XC8 installation status functions"""

    def test_is_xc8_installed_true(self):
        """Test XC8 installed detection when installed"""
        with patch(
            "xc8_wrapper.core.get_xc8_tool_path", return_value=("path", "version")
        ):
            assert is_xc8_installed() is True

    def test_is_xc8_installed_false(self):
        """Test XC8 installed detection when not installed"""
        with patch(
            "xc8_wrapper.core.get_xc8_tool_path", side_effect=Exception("Not found")
        ):
            assert is_xc8_installed() is False

    def test_get_installed_xc8_version_success(self):
        """Test getting installed XC8 version successfully"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Microchip MPLAB XC8 C Compiler V3.00\n"

        with patch(
            "xc8_wrapper.core.get_xc8_tool_path", return_value=("xc8-cc", "v3.00")
        ):
            with patch("subprocess.run", return_value=mock_result):
                version = get_installed_xc8_version()
                assert version == "3.00"

    def test_get_installed_xc8_version_failure(self):
        """Test getting version when detection fails"""
        with patch(
            "xc8_wrapper.core.get_xc8_tool_path", side_effect=Exception("Error")
        ):
            version = get_installed_xc8_version()
            assert version == "unknown"


class TestInstallIfNeeded:
    """Test the main install_xc8_if_needed function"""

    def test_install_xc8_if_needed_already_installed(self):
        """Test when XC8 is already installed"""
        with patch("xc8_wrapper.install.is_xc8_installed", return_value=True):
            result = install_xc8_if_needed()
            assert result is True

    def test_install_xc8_if_needed_skip_env_var(self):
        """Test installation skipped via environment variable"""
        with patch("xc8_wrapper.install.is_xc8_installed", return_value=False):
            with patch("os.environ.get", return_value="true"):
                result = install_xc8_if_needed()
                assert result is False

    def test_install_xc8_if_needed_force_reinstall(self):
        """Test force reinstall when XC8 is already installed"""
        with patch("xc8_wrapper.install.is_xc8_installed", return_value=True):
            with patch("xc8_wrapper.install.get_platform_name", return_value="linux"):
                with patch("xc8_wrapper.install.download_file", return_value=False):
                    # Should try to install even though XC8 is installed
                    result = install_xc8_if_needed(force=True)
                    assert result is False  # Fails because download fails


class TestDownloadAndInstall:
    """Test download and installation functions"""

    def test_download_file_failure(self):
        """Test failed file download"""
        from xc8_wrapper.install import download_file

        with patch("urllib.request.urlopen", side_effect=Exception("Network error")):
            result = download_file("http://fake.url", Path("/tmp/installer"))
            assert result is False

    def test_install_xc8_linux_failure(self):
        """Test failed Linux installation"""
        from xc8_wrapper.install import install_xc8_linux

        installer_path = Path("/tmp/installer.run")
        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch("pathlib.Path.exists", return_value=True):
            with patch("subprocess.run", return_value=mock_result):
                result = install_xc8_linux(installer_path)
                assert result is False

    def test_install_xc8_windows_success(self):
        """Test successful Windows installation"""
        from xc8_wrapper.install import install_xc8_windows

        installer_path = Path("C:\\temp\\installer.exe")
        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("pathlib.Path.exists", return_value=True):
            with patch("subprocess.run", return_value=mock_result):
                result = install_xc8_windows(installer_path)
                assert result is True


class TestInstallationOrchestration:
    """Test the main installation orchestration"""

    def test_install_xc8_if_needed_download_failure(self):
        """Test installation failure due to download issues"""
        with patch("xc8_wrapper.install.is_xc8_installed", return_value=False):
            with patch("xc8_wrapper.install.get_platform_name", return_value="linux"):
                with patch("xc8_wrapper.install.download_file", return_value=False):
                    result = install_xc8_if_needed(version="3.00")
                    assert result is False

    def test_install_xc8_if_needed_installation_success(self):
        """Test successful installation workflow"""
        with patch(
            "xc8_wrapper.install.is_xc8_installed", side_effect=[False, True]
        ):  # Not installed, then installed
            with patch("xc8_wrapper.install.get_platform_name", return_value="linux"):
                with patch("xc8_wrapper.install.download_file", return_value=True):
                    with patch(
                        "xc8_wrapper.install.install_xc8_linux", return_value=True
                    ):
                        with patch(
                            "xc8_wrapper.install.get_installed_xc8_version",
                            return_value="3.00",
                        ):
                            result = install_xc8_if_needed(version="3.00")
                            assert result is True


class TestUtilityFunctions:
    """Test utility and helper functions"""

    def test_check_xc8_installation(self):
        """Test installation check function"""
        from xc8_wrapper.install import check_xc8_installation

        with patch("xc8_wrapper.install.is_xc8_installed", return_value=True):
            with patch(
                "xc8_wrapper.install.get_installed_xc8_version", return_value="3.00"
            ):
                result = check_xc8_installation()
                assert result["installed"] is True
                assert result["version"] == "3.00"
