"""
Integration tests for XC8 Wrapper

Test the integration between different components of the XC8 wrapper.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from xc8_wrapper.cli import main


@pytest.mark.integration
class TestIntegration:
    """Integration tests for XC8 wrapper components"""

    def test_cli_to_core_integration(self):
        """Test integration between CLI and core modules"""
        with (
            patch("xc8_wrapper.core.validate_xc8_tool") as mock_validate,
            patch("xc8_wrapper.core.get_xc8_tool_path") as mock_get_path,
            patch("xc8_wrapper.core.run_command") as mock_run,
            patch("os.path.exists") as mock_exists,
            patch("os.path.getsize") as mock_getsize,
            patch("os.makedirs"),
        ):
            # Setup mocks
            mock_get_path.return_value = (r"C:\xc8\bin\xc8-cc.exe", "v3.00")
            mock_validate.return_value = True
            mock_exists.return_value = True
            mock_run.return_value = True
            mock_getsize.return_value = 1024

            # Test CLI calling core functionality
            try:
                main(["cc", "--cpu", "PIC16F876A", "--xc8-version", "3.00"])
            except SystemExit:
                # Expected when tool execution completes
                pass

            # Verify the integration chain
            mock_get_path.assert_called()
            mock_validate.assert_called()

    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test source directory and file
            src_dir = Path(temp_dir) / "src"
            src_dir.mkdir()

            main_c = src_dir / "main.c"
            main_c.write_text(
                """
#include <xc.h>

int main() {
    return 0;
}
"""
            )

            build_dir = Path(temp_dir) / "build"

            with (
                patch("xc8_wrapper.core.validate_xc8_tool") as mock_validate,
                patch("xc8_wrapper.core.get_xc8_tool_path") as mock_get_path,
                patch("xc8_wrapper.core.run_command") as mock_run,
            ):
                # Setup mocks
                mock_get_path.return_value = (r"C:\xc8\bin\xc8-cc.exe", "v3.00")
                mock_validate.return_value = True
                mock_run.return_value = MagicMock(returncode=0)

                # Test complete workflow
                try:
                    main(
                        [
                            "cc",
                            "--cpu",
                            "PIC16F876A",
                            "--xc8-version",
                            "3.00",
                            "--source-dir",
                            str(src_dir),
                            "--build-dir",
                            str(build_dir),
                        ]
                    )
                except SystemExit:
                    pass

                # Verify workflow executed
                mock_get_path.assert_called()
                mock_validate.assert_called()
                mock_run.assert_called()

    def test_error_handling_integration(self):
        """Test error handling across components"""
        with patch("xc8_wrapper.core.get_xc8_tool_path") as mock_get_path:
            # Test error propagation from core to CLI
            mock_get_path.side_effect = ValueError("Test error")

            with pytest.raises(SystemExit):
                main(["--cpu", "PIC16F876A", "--xc8-version", "3.00"])

    def test_configuration_integration(self):
        """Test configuration handling across components"""
        with (
            patch("xc8_wrapper.core.validate_xc8_tool") as mock_validate,
            patch("xc8_wrapper.core.get_xc8_tool_path") as mock_get_path,
            patch("xc8_wrapper.core.run_command") as mock_run,
            patch("pathlib.Path.exists") as mock_exists,
            patch("pathlib.Path.mkdir") as mock_mkdir,
            patch("pathlib.Path.stat") as mock_stat,
        ):
            # Setup mocks
            mock_get_path.return_value = (r"C:\xc8\bin\xc8-cc.exe", "v3.00")
            mock_validate.return_value = True
            mock_exists.return_value = True
            mock_mkdir.return_value = None
            mock_stat.return_value = MagicMock(st_size=1024)
            mock_run.return_value = MagicMock(returncode=0)

            # Test with various configuration options
            try:
                main(
                    [
                        "cc",
                        "--cpu",
                        "PIC18F4550",
                        "--xc8-version",
                        "3.00",
                        "-O2",
                        "-D",
                        "DEBUG=1",
                        "-D",
                        "VERSION=100",
                        "-I",
                        "./include",
                        "--verbose",
                    ]
                )
            except SystemExit:
                pass

            # Verify configuration was passed through
            mock_run.assert_called()

            # Check all calls to run_command
            all_calls = mock_run.call_args_list

            # Check that defines were included in compilation step (first call)
            if len(all_calls) > 0:
                compile_args = all_calls[0][0][0]  # First call args
                assert any("-O2" in str(arg) for arg in compile_args)
                assert any("-DDEBUG=1" in str(arg) for arg in compile_args)


class TestPackageIntegration:
    """Test package-level integration"""

    def test_package_imports(self):
        """Test that package imports work correctly"""
        import xc8_wrapper

        # Test that main exports are available
        assert hasattr(xc8_wrapper, "get_xc8_tool_path")
        assert hasattr(xc8_wrapper, "validate_xc8_tool")
        assert hasattr(xc8_wrapper, "SUPPORTED_XC8_TOOLS")

        # Test version information
        assert hasattr(xc8_wrapper, "__version__")
        assert hasattr(xc8_wrapper, "__author__")
        assert hasattr(xc8_wrapper, "__email__")

    def test_cli_entry_point(self):
        """Test that CLI entry point works"""
        from xc8_wrapper.cli import main

        # Test that main function exists and is callable
        assert callable(main)

    def test_demo_script_integration(self):
        """Test that demo script can import and use the package"""
        # This would normally import and run the demo script
        # For now, we'll just test the imports it uses
        from xc8_wrapper import SUPPORTED_XC8_TOOLS, get_xc8_tool_path

        # Test that demo script dependencies are available
        assert callable(get_xc8_tool_path)
        assert isinstance(SUPPORTED_XC8_TOOLS, dict)


if __name__ == "__main__":
    pytest.main([__file__])
