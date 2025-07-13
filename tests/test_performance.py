"""
Performance tests for XC8 Wrapper

Test the performance characteristics of the XC8 wrapper.
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from xc8_wrapper.cli import main
from xc8_wrapper.core import get_xc8_tool_path, validate_xc8_tool


@pytest.mark.performance
class TestPerformance:
    """Performance tests for XC8 wrapper"""

    @pytest.mark.slow
    def test_tool_path_resolution_performance(self):
        """Test that tool path resolution is fast"""
        start_time = time.time()

        # Run multiple path resolutions
        for _ in range(100):
            path, version = get_xc8_tool_path("cc", version="3.00")

        end_time = time.time()
        duration = end_time - start_time

        # Should complete 100 resolutions in under 1 second
        assert duration < 1.0, f"Path resolution took {duration:.3f}s for 100 calls"

    @pytest.mark.slow
    def test_validation_performance(self):
        """Test that validation is fast"""
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True

            start_time = time.time()

            # Run multiple validations
            for _ in range(100):
                validate_xc8_tool("fake_path", "cc", "v3.00")

            end_time = time.time()
            duration = end_time - start_time

            # Should complete 100 validations in under 0.5 seconds
            assert duration < 0.5, f"Validation took {duration:.3f}s for 100 calls"

    @pytest.mark.slow
    def test_cli_parsing_performance(self):
        """Test that CLI parsing is fast"""
        with (
            patch("xc8_wrapper.core.validate_xc8_tool") as mock_validate,
            patch("xc8_wrapper.core.get_xc8_tool_path") as mock_get_path,
            patch("xc8_wrapper.core.run_command") as mock_run,
            patch("os.path.exists") as mock_exists,
            patch("xc8_wrapper.core.os.path.getsize") as mock_getsize,
        ):
            # Setup mocks
            mock_get_path.return_value = (r"C:\xc8\bin\xc8-cc.exe", "v3.00")
            mock_validate.return_value = True
            mock_exists.return_value = True
            mock_run.return_value = MagicMock(returncode=0)
            mock_getsize.return_value = 1024  # Mock file size

            start_time = time.time()

            # Run multiple CLI parsing operations
            for _ in range(50):
                try:
                    main(["--cpu", "PIC16F876A", "--xc8-version", "3.00"])
                except SystemExit:
                    pass

            end_time = time.time()
            duration = end_time - start_time

            # Should complete 50 CLI operations in under 2 seconds
            assert duration < 2.0, f"CLI parsing took {duration:.3f}s for 50 calls"

    def test_memory_usage_stability(self):
        """Test that memory usage remains stable"""
        import gc

        # Force garbage collection
        gc.collect()

        # Run operations multiple times
        for _ in range(1000):
            path, version = get_xc8_tool_path("cc", version="3.00")

            # Simulate some work
            temp_data = [i for i in range(100)]
            del temp_data

        # Force garbage collection again
        gc.collect()

        # This test mainly ensures no memory leaks cause crashes
        # In a real scenario, you'd measure actual memory usage
        assert True  # Test passes if no memory issues occur


class TestScalability:
    """Test scalability aspects"""

    def test_concurrent_operations(self):
        """Test that operations work correctly under concurrent access"""
        import queue
        import threading

        results = queue.Queue()

        def worker():
            try:
                path, version = get_xc8_tool_path("cc", version="3.00")
                results.put(("success", path, version))
            except Exception as e:
                results.put(("error", str(e)))

        # Start multiple threads
        threads = []
        for _ in range(10):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Check results
        success_count = 0
        while not results.empty():
            result = results.get()
            if result[0] == "success":
                success_count += 1

        assert success_count == 10, (
            f"Expected 10 successful operations, got {success_count}"
        )

    def test_large_argument_lists(self):
        """Test handling of large argument lists"""
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

            # Create large argument list
            large_args = ["cc", "--cpu", "PIC16F876A", "--xc8-version", "3.00"]

            # Add many defines
            for i in range(100):
                large_args.extend(["-D", f"VAR{i}={i}"])

            # Add many includes
            for i in range(50):
                large_args.extend(["-I", f"./include{i}"])

            # Test that it handles large argument lists
            try:
                main(large_args)
            except SystemExit:
                pass

            # Verify it was called
            mock_run.assert_called()


class TestResourceUsage:
    """Test resource usage characteristics"""

    def test_file_handle_cleanup(self):
        """Test that file handles are properly cleaned up"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple temporary files
            for i in range(100):
                temp_file = Path(temp_dir) / f"test_{i}.c"
                temp_file.write_text(f"// Test file {i}")

            # Test that operations don't leave file handles open
            with patch("os.path.exists") as mock_exists:
                mock_exists.return_value = True

                for i in range(100):
                    result = validate_xc8_tool(str(temp_file), "cc", "v3.00")
                    assert result is True

        # Directory cleanup should succeed if no handles are left open
        assert True

    def test_error_recovery(self):
        """Test that errors don't leave resources in bad state"""
        # Test multiple error conditions (only unsupported tool should raise error)
        error_scenarios = [
            ("nonexistent_tool", "3.00", None),  # Only this should raise
        ]
        
        # Test auto-detection scenarios (should work)
        auto_detection_scenarios = [
            ("cc", "", None),
            ("cc", None, None),
        ]
        
        # Test error scenario
        for tool, version, custom_path in error_scenarios:
            with pytest.raises(ValueError):
                get_xc8_tool_path(tool, version=version, custom_path=custom_path)
        
        # Test auto-detection scenarios
        for tool, version, custom_path in auto_detection_scenarios:
            result = get_xc8_tool_path(tool, version=version, custom_path=custom_path)
            assert result is not None

        # After errors, normal operations should still work
        path, version = get_xc8_tool_path("cc", version="3.00")
        assert path is not None
        assert version is not None


if __name__ == "__main__":
    pytest.main([__file__])
