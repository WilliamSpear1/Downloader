import unittest
from unittest.mock import Mock, MagicMock, patch
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from src.service.scraper_service import ScarperService
from src.model.video import Video


class TestScarperService(unittest.TestCase):

    def setUp(self):
        self.url = "https://example.com/videos"
        self.number_of_pages = 2
        self.parent_directory = "TestParent"
        self.service = ScarperService(self.url, self.number_of_pages, self.parent_directory)

    def test_init(self):
        """Test ScarperService initialization."""
        self.assertEqual(self.service.url, self.url)
        self.assertEqual(self.service.number_of_pages, self.number_of_pages)
        self.assertEqual(self.service.parent_directory, self.parent_directory)

    def test_init_default_parent_directory(self):
        """Test ScarperService initialization with default parent_directory."""
        service = ScarperService(self.url, self.number_of_pages)
        self.assertEqual(service.parent_directory, "")

    @patch('src.service.scraper_service.logger')
    def test_scrape_multiple_videos_success(self, mock_logger):
        """Test scraping multiple videos successfully."""
        # Mock WebDriver and elements
        mock_driver = Mock()
        mock_element1 = Mock()
        mock_element2 = Mock()

        # Mock first video element
        mock_link1 = Mock()
        mock_link1.get_attribute.side_effect = lambda attr: (
            "https://example.com/video1" if attr == 'href' else "Video 1 Title"
        )
        mock_element1.find_element.return_value = mock_link1

        # Mock second video element
        mock_link2 = Mock()
        mock_link2.get_attribute.side_effect = lambda attr: (
            "https://example.com/video2" if attr == 'href' else "Video 2 Title"
        )
        mock_element2.find_element.return_value = mock_link2

        # Mock driver.find_elements to return the mock elements
        mock_driver.find_elements.return_value = [mock_element1, mock_element2]

        path = "/videos/TestPath"

        with patch('src.service.scraper_service.Video') as MockVideo:
            # Create mock Video instances
            mock_video1 = Mock(spec=Video)
            mock_video2 = Mock(spec=Video)
            MockVideo.side_effect = [mock_video1, mock_video2]

            result = ScarperService.scrape_multiple_videos(mock_driver, path)

            # Verify results
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], mock_video1)
            self.assertEqual(result[1], mock_video2)

            # Verify Video was instantiated correctly
            self.assertEqual(MockVideo.call_count, 2)
            MockVideo.assert_any_call(
                link="https://example.com/video1",
                title="Video 1 Title"
            )
            MockVideo.assert_any_call(
                link="https://example.com/video2",
                title="Video 2 Title"
            )

            # Verify path was set
            mock_video1.path = path
            mock_video2.path = path

            # Verify logger was called
            mock_logger.info.assert_called_with("Found 2 videos on the page.")

    @patch('src.service.scraper_service.logger')
    def test_scrape_multiple_videos_with_exception(self, mock_logger):
        """Test scraping when some elements raise NoSuchElementException."""
        mock_driver = Mock()
        mock_element1 = Mock()
        mock_element2 = Mock()

        # First element succeeds
        mock_link1 = Mock()
        mock_link1.get_attribute.side_effect = lambda attr: (
            "https://example.com/video1" if attr == 'href' else "Video 1 Title"
        )
        mock_element1.find_element.return_value = mock_link1

        # Second element raises NoSuchElementException
        mock_element2.find_element.side_effect = NoSuchElementException("Element not found")

        mock_driver.find_elements.return_value = [mock_element1, mock_element2]

        path = "/videos/TestPath"

        with patch('src.service.scraper_service.Video') as MockVideo:
            mock_video1 = Mock(spec=Video)
            MockVideo.return_value = mock_video1

            result = ScarperService.scrape_multiple_videos(mock_driver, path)

            # Only one video should be returned (second one failed)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], mock_video1)

            # Verify warning was logged
            mock_logger.warning.assert_called_once()
            self.assertIn("No Such Element Exception Has Occurred", str(mock_logger.warning.call_args))

            # Verify info log still shows 1 video found
            mock_logger.info.assert_called_with("Found 1 videos on the page.")

    @patch('src.service.scraper_service.logger')
    def test_scrape_multiple_videos_empty_page(self, mock_logger):
        """Test scraping when no videos are found on the page."""
        mock_driver = Mock()
        mock_driver.find_elements.return_value = []

        path = "/videos/TestPath"

        result = ScarperService.scrape_multiple_videos(mock_driver, path)

        self.assertEqual(len(result), 0)
        mock_logger.info.assert_called_with("Found 0 videos on the page.")

    @patch('src.service.scraper_service.logger')
    def test_scrape_multiple_videos_all_exceptions(self, mock_logger):
        """Test scraping when all elements raise exceptions."""
        mock_driver = Mock()
        mock_element1 = Mock()
        mock_element2 = Mock()

        # Both elements raise NoSuchElementException
        mock_element1.find_element.side_effect = NoSuchElementException("Element not found")
        mock_element2.find_element.side_effect = NoSuchElementException("Element not found")

        mock_driver.find_elements.return_value = [mock_element1, mock_element2]

        path = "/videos/TestPath"

        result = ScarperService.scrape_multiple_videos(mock_driver, path)

        # No videos should be returned
        self.assertEqual(len(result), 0)

        # Two warnings should be logged
        self.assertEqual(mock_logger.warning.call_count, 2)

        # Info log should show 0 videos
        mock_logger.info.assert_called_with("Found 0 videos on the page.")

    @patch('src.service.scraper_service.logger')
    def test_scrape_multiple_videos_correct_css_selectors(self, mock_logger):
        """Verify correct CSS selectors are used."""
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

            # Verify correct selectors were used
            mock_driver.find_elements.assert_called_once_with(By.CSS_SELECTOR, "div.item-info")


if __name__ == '__main__':
    unittest.main()