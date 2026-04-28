import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
from pathlib import Path

from src.service.directory_service import DirectoryService

class TestDirectoryService(unittest.TestCase):

    def setUp(self):
        self.service = DirectoryService()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)  # Change to temp dir for isolation

    def tearDown(self):
        os.chdir(self.original_cwd)
        self.temp_dir.cleanup()

    @patch('src.service.directory_service.logger')
    def test_create_directory_standard_url(self, mock_logger):
        url = "https://example.com/videos/my-video-series"
        result = self.service.create_directory(url)
        expected_path = Path("./videos/MY-VIDEO-SERIES")
        self.assertTrue(expected_path.exists())
        self.assertEqual(result, str(expected_path))
        mock_logger.info.assert_called()

    @patch('src.service.directory_service.logger')
    def test_create_directory_hits_url_with_ps_param(self, mock_logger):
        url = "https://hits.com/?ps=MySeries"
        result = self.service.create_directory(url)
        expected_path = Path("./videos/MYSERIES")
        self.assertTrue(expected_path.exists())
        self.assertEqual(result, str(expected_path))

    @patch('src.service.directory_service.logger')
    def test_create_directory_hits_url_with_spon_param(self, mock_logger):
        url = "https://hits.com/?spon=AnotherSeries"
        result = self.service.create_directory(url)
        expected_path = Path("./videos/ANOTHERSERIES")
        self.assertTrue(expected_path.exists())

    @patch('src.service.directory_service.logger')
    def test_create_directory_with_parent_directory(self, mock_logger):
        url = "https://example.com/videos/my-video"
        parent = "ParentDir"
        result = self.service.create_directory(url, parent)
        expected_path = Path("./videos/PARENTDIR/MY-VIDEO")
        self.assertTrue(expected_path.exists())
        self.assertEqual(result, str(expected_path))

    @patch('src.service.directory_service.logger')
    def test_create_directory_invalid_url_raises_value_error(self, mock_logger):
        url = "https://example.com/"  # No path or params
        with self.assertRaises(ValueError) as cm:
            self.service.create_directory(url)
        self.assertIn("Cannot extract directory name", str(cm.exception))

    @patch('pathlib.Path.mkdir', side_effect=OSError("Permission denied"))
    @patch('src.service.directory_service.logger')
    def test_create_directory_permission_error_raises_custom_error(self, mock_logger, mock_mkdir):
        url = "https://example.com/videos/test"
        from src.error.directory_creation_error import DirectoryCreationError
        with self.assertRaises(DirectoryCreationError):
            self.service.create_directory(url)

    def test_safe_dir_name_sanitizes_special_chars(self):
        self.assertEqual(DirectoryService.safe_dir_name("My.Video+Name"), "My_Video_Name")
        self.assertEqual(DirectoryService.safe_dir_name("___Name___"), "Name")
        self.assertEqual(DirectoryService.safe_dir_name("!@#$%"), "default")  # All invalid becomes default

    def test_safe_dir_name_empty_string(self):
        self.assertEqual(DirectoryService.safe_dir_name(""), "default")

    def test_get_end_valid_end(self):
        parts = ["videos", "most-popular"]
        self.assertEqual(self.service._get_end(parts), "my-series")

    def test_get_end_invalid_end_fallback(self):
        parts = ["most-popular", "videos"]
        self.assertEqual(self.service._get_end(parts), "videos")

    def test_is_valid_end_true_for_valid(self):
        self.assertTrue(self.service._is_valid_end("my-series"))
        self.assertTrue(self.service._is_valid_end("category"))  # Wait, this should be False? Wait, code says != "most-popular" and != "top-rated"
        # Actually, the code returns False only for "most-popular" and "top-rated"
        self.assertFalse(self.service._is_valid_end("most-popular"))
        self.assertFalse(self.service._is_valid_end("top-rated"))

if __name__ == '__main__':
    unittest.main()