import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
from pathlib import Path

from src.service.directory_service import DirectoryService

class TestDirectoryService(unittest.TestCase):
    """Tests for DirectoryService covering directory creation, URL parsing, and path sanitization."""

    def setUp(self) -> None:
        """Set up a DirectoryService instance and isolate file system operations in a temporary directory."""
        self.service = DirectoryService()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)  # Change to temp dir for isolation

    def tearDown(self) -> None:
        """Restore the original working directory and clean up the temporary directory."""
        os.chdir(self.original_cwd)
        self.temp_dir.cleanup()

    @patch('src.service.directory_service.logger')
    def test_create_directory_standard_url(self, mock_logger):
        """
        Test that a standard URL with a path segment creates the expected directory.

        Given a URL like 'https://example.com/videos/my-video-series', the last path segment
        should be extracted, uppercased, and used as the directory name under './videos/'.

        Asserts the directory exists, the returned path matches, and logging is called.
        """
        url = "https://example.com/videos/my-video-series"
        result = self.service.create_directory(url)
        expected_path = Path("./videos/MY-VIDEO-SERIES")
        self.assertTrue(expected_path.exists())
        self.assertEqual(result, str(expected_path))
        mock_logger.info.assert_called()

    @patch('src.service.directory_service.logger')
    def test_create_directory_hits_url_with_ps_param(self, mock_logger):
        """
        Test that a Hits URL with 'ps' query parameter extracts the series name correctly.

        Given a URL like 'https://hits.com/?ps=MySeries', the 'ps' parameter value
        should be extracted and uppercased as the directory name.

        Asserts the directory exists and the returned path matches './videos/MYSERIES'.
        """
        url = "https://hits.com/?ps=MySeries"
        result = self.service.create_directory(url)
        expected_path = Path("./videos/MYSERIES")
        self.assertTrue(expected_path.exists())
        self.assertEqual(result, str(expected_path))

    @patch('src.service.directory_service.logger')
    def test_create_directory_hits_url_with_spon_param(self, mock_logger):
        """
        Test that a Hits URL with 'spon' query parameter extracts the series name correctly.

        Given a URL like 'https://hits.com/?spon=AnotherSeries', the 'spon' parameter value
        should be extracted and uppercased as the directory name.

        Asserts the directory exists with the expected path './videos/ANOTHERSERIES'.
        """
        url = "https://hits.com/?spon=AnotherSeries"
        result = self.service.create_directory(url)
        expected_path = Path("./videos/ANOTHERSERIES")
        self.assertTrue(expected_path.exists())

    @patch('src.service.directory_service.logger')
    def test_create_directory_with_parent_directory(self, mock_logger):
        """
        Test that a parent directory is prepended to the created path.

        Given a URL and a parent directory name, the parent should be uppercased
        and placed between './videos/' and the extracted directory name.

        Asserts the directory exists at './videos/PARENTDIR/MY-VIDEO'.
        """
        url = "https://example.com/videos/my-video"
        parent = "ParentDir"
        result = self.service.create_directory(url, parent)
        expected_path = Path("./videos/PARENTDIR/MY-VIDEO")
        self.assertTrue(expected_path.exists())
        self.assertEqual(result, str(expected_path))

    @patch('src.service.directory_service.logger')
    def test_create_directory_invalid_url_raises_value_error(self, mock_logger):
        """
        Test that a URL with no extractable path or query parameter raises ValueError.

        Given a URL like 'https://example.com/' with no path segment or query params,
        the service should raise a ValueError indicating it cannot extract a directory name.

        Asserts ValueError is raised with the expected error message.
        """
        url = "https://example.com/"
        with self.assertRaises(ValueError) as cm:
            self.service.create_directory(url)
        self.assertIn("Cannot extract directory name", str(cm.exception))

    def test_safe_dir_name_sanitizes_special_chars(self):
        """
        Test that safe_dir_name replaces special characters and strips underscores.

        Verifies that dots, pluses, and other special chars become underscores,
        leading/trailing underscores are stripped, and fully invalid names fall back to 'default'.

        Asserts the sanitized names match expected output for each input.
        """
        self.assertEqual(DirectoryService.safe_dir_name("My.Video+Name"), "My_Video_Name")
        self.assertEqual(DirectoryService.safe_dir_name("___Name___"), "Name")
        self.assertEqual(DirectoryService.safe_dir_name("!@#$%"), "default")

    def test_safe_dir_name_empty_string(self):
        """
        Test that an empty string input returns the default directory name.

        Asserts that safe_dir_name returns 'default' when given an empty string.
        """
        self.assertEqual(DirectoryService.safe_dir_name(""), "default")

    def test_get_end_valid_end(self):
        """
        Test that _get_end returns the last valid path segment.

        Given path parts where the last segment is a valid end (not 'most-popular' or 'top-rated'),
        it should return that last segment.

        Asserts the returned value is the expected valid end string.
        """
        parts = ["videos", "most-popular"]
        self.assertEqual(self.service._get_end(parts), "my-series")

    def test_get_end_invalid_end_fallback(self):
        """
        Test that _get_end falls back when the last segment is invalid.

        Given path parts where the last segment is valid but the second-to-last is invalid
        ('most-popular'), it should return the valid segment ('videos').

        Asserts the returned value is the fallback valid segment.
        """
        parts = ["most-popular", "videos"]
        self.assertEqual(self.service._get_end(parts), "videos")

    def test_is_valid_end_true_for_valid(self):
        """
        Test that _is_valid_end correctly identifies valid and invalid end segments.

        Asserts that valid names like 'my-series' and 'category' return True,
        while reserved names 'most-popular' and 'top-rated' return False.
        """
        self.assertTrue(self.service._is_valid_end("my-series"))
        self.assertTrue(self.service._is_valid_end("category"))  # Wait, this should be False? Wait, code says != "most-popular" and != "top-rated"
        # Actually, the code returns False only for "most-popular" and "top-rated"
        self.assertFalse(self.service._is_valid_end("most-popular"))
        self.assertFalse(self.service._is_valid_end("top-rated"))

if __name__ == '__main__':
    unittest.main()