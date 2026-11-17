import unittest
from unittest.mock import Mock, MagicMock, patch
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from src.service.scraper_service import ScarperService
from src.model.video import Video


class TestScarperService(unittest.TestCase):
    """Tests for ScarperService covering initialization and video element extraction from web pages."""

    def setUp(self) -> None:
        """Set up a ScarperService instance with test URL, page count, and parent directory."""
        self.url = "https://example.com/videos"
        self.number_of_pages = 2
        self.parent_directory = "TestParent"
        self.service = ScarperService(self.url, self.number_of_pages, self.parent_directory)

    def test_init(self):
        """
        Test that ScarperService stores the provided URL, page count, and parent directory.

        Asserts all three attributes match the constructor arguments.
        """
        self.assertEqual(self.service.url, self.url)
        self.assertEqual(self.service.number_of_pages, self.number_of_pages)
        self.assertEqual(self.service.parent_directory, self.parent_directory)

    def test_init_default_parent_directory(self):
        """
        Test that ScarperService defaults parent_directory to an empty string.

        Creates a service without specifying parent_directory and verifies the default.

        Asserts parent_directory is an empty string.
        """
        service = ScarperService(self.url, self.number_of_pages)
        self.assertEqual(service.parent_directory, "")

    @patch('src.service.scraper_service.logger')
    def test_scrape_multiple_videos_success(self, mock_logger):
        """
        Test that scrape_multiple_videos extracts video titles and links correctly.

        Mocks a WebDriver returning two video elements with href and title attributes.
        Verifies Video objects are created with the correct link and title, and the
        path is set on each video.

        Asserts 2 videos are returned with correct attributes and logger is called.
        """
        mock_driver = Mock()
        mock_element1 = Mock()
        mock_element2 = Mock()

        mock_link1 = Mock()
        mock_link1.get_attribute.side_effect = lambda attr: (
            "https://example.com/video1" if attr == 'href' else "Video 1 Title"
        )
        mock_element1.find_element.return_value = mock_link1

        mock_link2 = Mock()
        mock_link2.get_attribute.side_effect = lambda attr: (
            "https://example.com/video2" if attr == 'href' else "Video 2 Title"
        )
        mock_element2.find_element.return_value = mock_link2

        mock_driver.find_elements.return_value = [mock_element1, mock_element2]

        path = "/videos/TestPath"

        with patch('src.service.scraper_service.Video') as MockVideo:
            mock_video1 = Mock(spec=Video)
            mock_video2 = Mock(spec=Video)
            MockVideo.side_effect = [mock_video1, mock_video2]

            result = ScarperService.scrape_multiple_videos(mock_driver, path)

            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], mock_video1)
            self.assertEqual(result[1], mock_video2)

            self.assertEqual(MockVideo.call_count, 2)
            MockVideo.assert_any_call(
                link="https://example.com/video1",
                title="Video 1 Title"
            )
            MockVideo.assert_any_call(
                link="https://example.com/video2",
                title="Video 2 Title"
            )

            mock_video1.path = path
            mock_video2.path = path

            mock_logger.info.assert_called_with("Found 2 videos on the page.")

    @patch('src.service.scraper_service.logger')
    def test_scrape_multiple_videos_with_exception(
            self,
            mock_logger
    ):
        """
        Test that scrape_multiple_videos handles partial failures gracefully.

        Mocks two video elements where the second raises NoSuchElementException.
        Verifies only the successful video is returned and a warning is logged.

        Asserts 1 video is returned, warning is logged, and info log shows 1 video.
        """
        mock_driver = Mock()
        mock_element1 = Mock()
        mock_element2 = Mock()

        mock_link1 = Mock()
        mock_link1.get_attribute.side_effect = lambda attr: (
            "https://example.com/video1" if attr == 'href' else "Video 1 Title"
        )
        mock_element1.find_element.return_value = mock_link1

        mock_element2.find_element.side_effect = NoSuchElementException("Element not found")

        mock_driver.find_elements.return_value = [mock_element1, mock_element2]

        path = "/videos/TestPath"

        with patch('src.service.scraper_service.Video') as MockVideo:
            mock_video1 = Mock(spec=Video)
            MockVideo.return_value = mock_video1

            result = ScarperService.scrape_multiple_videos(mock_driver, path)

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], mock_video1)

            mock_logger.warning.assert_called_once()
            self.assertIn("No Such Element Exception Has Occurred", str(mock_logger.warning.call_args))

            mock_logger.info.assert_called_with("Found 1 videos on the page.")

    @patch('src.service.scraper_service.logger')
    def test_scrape_multiple_videos_empty_page(self, mock_logger):
        """
        Test that scrape_multiple_videos returns an empty list when no videos exist.

        Mocks a WebDriver that returns no video elements.
        Verifies an empty list is returned and the logger reports 0 videos.

        Asserts result is empty and info log shows 0 videos.
        """
        mock_driver = Mock()
        mock_driver.find_elements.return_value = []

        path = "/videos/TestPath"

        result = ScarperService.scrape_multiple_videos(mock_driver, path)

        self.assertEqual(len(result), 0)
        mock_logger.info.assert_called_with("Found 0 videos on the page.")

    @patch('src.service.scraper_service.logger')
    def test_scrape_multiple_videos_all_exceptions(
            self,
            mock_logger
    ):
        """
        Test that scrape_multiple_videos handles all elements failing gracefully.

        Mocks two video elements that both raise NoSuchElementException.
        Verifies an empty list is returned and warnings are logged for each failure.

        Asserts 0 videos are returned and 2 warnings are logged.
        """
        mock_driver = Mock()
        mock_element1 = Mock()
        mock_element2 = Mock()

        mock_element1.find_element.side_effect = NoSuchElementException("Element not found")
        mock_element2.find_element.side_effect = NoSuchElementException("Element not found")

        mock_driver.find_elements.return_value = [mock_element1, mock_element2]

        path = "/videos/TestPath"

        result = ScarperService.scrape_multiple_videos(mock_driver, path)

        self.assertEqual(len(result), 0)

        self.assertEqual(mock_logger.warning.call_count, 2)

        mock_logger.info.assert_called_with("Found 0 videos on the page.")

    @patch('src.service.scraper_service.logger')
    def test_scrape_multiple_videos_correct_css_selectors(
            self,
            mock_logger
    ):
        """
        Test that scrape_multiple_videos uses the correct CSS selectors.

        Mocks a WebDriver and verifies the correct CSS selectors are used:
        'div.item-info' for finding video elements and 'a.thumb_title' for links.

        Asserts find_elements is called with the expected CSS selector.
        """
        mock_driver = Mock()
        mock_element = Mock()
        mock_link = Mock()
        mock_link.get_attribute.side_effect = lambda attr: (
            "https://example.com/video" if attr == 'href' else "Video Title"
        )
        mock_element.find_element.return_value = mock_link

        mock_driver.find_elements.return_value = [mock_element]

        with patch('src.service.scraper_service.Video'):
            ScarperService.scrape_multiple_videos(mock_driver, "/path")

            mock_driver.find_elements.assert_called_once_with(By.CSS_SELECTOR, "div.item-info")

if __name__ == '__main__':
    unittest.main()