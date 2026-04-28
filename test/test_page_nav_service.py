import unittest
from unittest.mock import Mock, patch, MagicMock, call
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from src.service.page_nav_service import run_browser


class TestPageNavService(unittest.TestCase):

    @patch('src.service.page_nav_service.logger')
    @patch('src.service.page_nav_service.ScarperService')
    @patch('src.service.page_nav_service.DownloaderService')
    @patch('src.service.page_nav_service.DirectoryService')
    @patch('src.service.page_nav_service.ChromeDriver')
    def test_run_browser_single_page_success(self, mock_chrome_driver, mock_dir_service,
                                            mock_downloader, mock_scraper, mock_logger):
        """Test run_browser successfully processes a single page."""
        # Setup mocks
        mock_driver_instance = Mock()
        mock_chrome = Mock()
        mock_chrome.get_driver.return_value = mock_driver_instance
        mock_chrome_driver.return_value = mock_chrome

        mock_dir_instance = Mock()
        mock_dir_instance.create_directory.return_value = "/videos/TEST"
        mock_dir_service.return_value = mock_dir_instance

        mock_downloader_instance = Mock()
        mock_downloader.return_value = mock_downloader_instance

        mock_scraper_instance = Mock()
        mock_video1 = Mock()
        mock_video2 = Mock()
        mock_scraper_instance.scrape_multiple_videos.return_value = [mock_video1, mock_video2]
        mock_scraper.return_value = mock_scraper_instance

        # Mock no next page
        mock_driver_instance.find_element.side_effect = NoSuchElementException("No next page")

        url = "https://example.com/videos"
        number_of_pages = 1
        parent_dir = "TestParent"

        # Execute
        run_browser(url, number_of_pages, parent_dir)

        # Verify ChromeDriver setup
        mock_chrome_driver.assert_called_once_with(url)
        mock_chrome.get_driver.assert_called_once()

        # Verify directory creation
        mock_dir_instance.create_directory.assert_called_once_with(url, parent_dir)

        # Verify scraper setup
        mock_scraper.assert_called_once_with(url, number_of_pages, parent_dir)
        mock_scraper_instance.scrape_multiple_videos.assert_called_once_with(mock_driver_instance, "/videos/TEST")

        # Verify downloads
        mock_downloader_instance.download_videos.assert_called_once_with([mock_video1, mock_video2])

        # Verify browser closed
        mock_chrome.close_browser.assert_called_once()

    @patch('src.service.page_nav_service.logger')
    @patch('src.service.page_nav_service.ScarperService')
    @patch('src.service.page_nav_service.DownloaderService')
    @patch('src.service.page_nav_service.DirectoryService')
    @patch('src.service.page_nav_service.ChromeDriver')
    def test_run_browser_multiple_pages(self, mock_chrome_driver, mock_dir_service,
                                       mock_downloader, mock_scraper, mock_logger):
        """Test run_browser processes multiple pages."""
        # Setup mocks
        mock_driver_instance = Mock()
        mock_chrome = Mock()
        mock_chrome.get_driver.return_value = mock_driver_instance
        mock_chrome_driver.return_value = mock_chrome

        mock_dir_instance = Mock()
        mock_dir_instance.create_directory.return_value = "/videos/TEST"
        mock_dir_service.return_value = mock_dir_instance

        mock_downloader_instance = Mock()
        mock_downloader.return_value = mock_downloader_instance

        mock_scraper_instance = Mock()
        mock_videos_page1 = [Mock(), Mock()]
        mock_videos_page2 = [Mock(), Mock()]
        mock_scraper_instance.scrape_multiple_videos.side_effect = [mock_videos_page1, mock_videos_page2]
        mock_scraper.return_value = mock_scraper_instance

        # Mock next page link for page 1, no next page for page 2
        mock_next_link = Mock()
        mock_driver_instance.find_element.side_effect = [
            mock_next_link,  # Page 1: next link found
            NoSuchElementException("No next page")  # Page 2: no next link
        ]

        url = "https://example.com/videos"
        number_of_pages = 2

        # Execute
        run_browser(url, number_of_pages)

        # Verify scraper was called twice
        self.assertEqual(mock_scraper_instance.scrape_multiple_videos.call_count, 2)

        # Verify download was called twice
        self.assertEqual(mock_downloader_instance.download_videos.call_count, 2)
        mock_downloader_instance.download_videos.assert_any_call(mock_videos_page1)
        mock_downloader_instance.download_videos.assert_any_call(mock_videos_page2)

        # Verify next page link was clicked
        mock_driver_instance.execute_script.assert_called_once()
        script_call = mock_driver_instance.execute_script.call_args[0]
        self.assertIn("click", script_call[0])

        # Verify browser closed
        mock_chrome.close_browser.assert_called_once()

    @patch('src.service.page_nav_service.logger')
    @patch('src.service.page_nav_service.ScarperService')
    @patch('src.service.page_nav_service.DownloaderService')
    @patch('src.service.page_nav_service.DirectoryService')
    @patch('src.service.page_nav_service.ChromeDriver')
    def test_run_browser_no_videos_found(self, mock_chrome_driver, mock_dir_service,
                                        mock_downloader, mock_scraper, mock_logger):
        """Test run_browser handles pages with no videos."""
        # Setup mocks
        mock_driver_instance = Mock()
        mock_chrome = Mock()
        mock_chrome.get_driver.return_value = mock_driver_instance
        mock_chrome_driver.return_value = mock_chrome

        mock_dir_instance = Mock()
        mock_dir_instance.create_directory.return_value = "/videos/TEST"
        mock_dir_service.return_value = mock_dir_instance

        mock_downloader_instance = Mock()
        mock_downloader.return_value = mock_downloader_instance

        mock_scraper_instance = Mock()
        mock_scraper_instance.scrape_multiple_videos.return_value = []  # No videos
        mock_scraper.return_value = mock_scraper_instance

        mock_driver_instance.find_element.side_effect = NoSuchElementException("No next page")

        url = "https://example.com/videos"

        # Execute
        run_browser(url, 1)

        # Verify download was not called
        mock_downloader_instance.download_videos.assert_not_called()

        # Verify warning was logged
        mock_logger.warning.assert_called_with("No videos found on this page.")

        # Verify browser closed
        mock_chrome.close_browser.assert_called_once()

    @patch('src.service.page_nav_service.logger')
    @patch('src.service.page_nav_service.ScarperService')
    @patch('src.service.page_nav_service.DownloaderService')
    @patch('src.service.page_nav_service.DirectoryService')
    @patch('src.service.page_nav_service.ChromeDriver')
    def test_run_browser_exception_during_scraping(self, mock_chrome_driver, mock_dir_service,
                                                   mock_downloader, mock_scraper, mock_logger):
        """Test run_browser handles exceptions gracefully and closes browser."""
        # Setup mocks
        mock_driver_instance = Mock()
        mock_chrome = Mock()
        mock_chrome.get_driver.return_value = mock_driver_instance
        mock_chrome_driver.return_value = mock_chrome

        mock_dir_instance = Mock()
        mock_dir_instance.create_directory.return_value = "/videos/TEST"
        mock_dir_service.return_value = mock_dir_instance

        mock_downloader_instance = Mock()
        mock_downloader.return_value = mock_downloader_instance

        mock_scraper_instance = Mock()
        mock_scraper_instance.scrape_multiple_videos.side_effect = RuntimeError("Scraping failed")
        mock_scraper.return_value = mock_scraper_instance

        url = "https://example.com/videos"

        # Execute
        run_browser(url, 1)

        # Verify error was logged
        self.assertTrue(mock_logger.error.called)
        error_call = mock_logger.error.call_args_list[0]
        self.assertIn("Unexpected error", error_call[0][0])

        # Verify browser was closed even with exception
        mock_chrome.close_browser.assert_called_once()

        # Verify finish log
        finish_logs = [call[0][0] for call in mock_logger.info.call_args_list]
        self.assertTrue(any("finished" in log.lower() for log in finish_logs))

    @patch('src.service.page_nav_service.logger')
    @patch('src.service.page_nav_service.WebDriverWait')
    @patch('src.service.page_nav_service.ScarperService')
    @patch('src.service.page_nav_service.DownloaderService')
    @patch('src.service.page_nav_service.DirectoryService')
    @patch('src.service.page_nav_service.ChromeDriver')
    def test_run_browser_wait_for_next_page(self, mock_chrome_driver, mock_dir_service,
                                           mock_downloader, mock_scraper, mock_wait, mock_logger):
        """Test run_browser waits for next page link to be clickable."""
        # Setup mocks
        mock_driver_instance = Mock()
        mock_chrome = Mock()
        mock_chrome.get_driver.return_value = mock_driver_instance
        mock_chrome_driver.return_value = mock_chrome

        mock_dir_instance = Mock()
        mock_dir_instance.create_directory.return_value = "/videos/TEST"
        mock_dir_service.return_value = mock_dir_instance

        mock_downloader_instance = Mock()
        mock_downloader.return_value = mock_downloader_instance

        mock_scraper_instance = Mock()
        mock_scraper_instance.scrape_multiple_videos.side_effect = [
            [Mock()],  # Page 1
            NoSuchElementException("No more pages")  # Page 2 scraper call won't happen
        ]
        mock_scraper.return_value = mock_scraper_instance

        # First call: next link found, second call: no next link
        mock_next_link = Mock()
        mock_driver_instance.find_element.side_effect = [
            mock_next_link,
            NoSuchElementException("No next page")
        ]

        # Mock WebDriverWait
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance

        url = "https://example.com/videos"

        # Execute
        run_browser(url, 2)

        # Verify WebDriverWait was used
        mock_wait.assert_called_once_with(mock_driver_instance, 40)
        mock_wait_instance.until.assert_called_once()

        # Verify correct locator was passed to until()
        locator_args = mock_wait_instance.until.call_args[0][0]
        # The locator should handle elements by CSS_SELECTOR "li.next a"

        # Verify browser was closed
        mock_chrome.close_browser.assert_called_once()

    @patch('src.service.page_nav_service.logger')
    @patch('src.service.page_nav_service.ScarperService')
    @patch('src.service.page_nav_service.DownloaderService')
    @patch('src.service.page_nav_service.DirectoryService')
    @patch('src.service.page_nav_service.ChromeDriver')
    def test_run_browser_default_parent_directory(self, mock_chrome_driver, mock_dir_service,
                                                  mock_downloader, mock_scraper, mock_logger):
        """Test run_browser with default (empty) parent_directory."""
        # Setup mocks
        mock_driver_instance = Mock()
        mock_chrome = Mock()
        mock_chrome.get_driver.return_value = mock_driver_instance
        mock_chrome_driver.return_value = mock_chrome

        mock_dir_instance = Mock()
        mock_dir_instance.create_directory.return_value = "/videos/TEST"
        mock_dir_service.return_value = mock_dir_instance

        mock_downloader_instance = Mock()
        mock_downloader.return_value = mock_downloader_instance

        mock_scraper_instance = Mock()
        mock_scraper_instance.scrape_multiple_videos.return_value = []
        mock_scraper.return_value = mock_scraper_instance

        mock_driver_instance.find_element.side_effect = NoSuchElementException("No next page")

        url = "https://example.com/videos"

        # Execute with default parent_directory
        run_browser(url, 1)

        # Verify directory creation with empty parent_directory
        mock_dir_instance.create_directory.assert_called_once_with(url, "")

        # Verify scraper initialized with empty parent_directory
        mock_scraper.assert_called_once_with(url, 1, "")

    @patch('src.service.page_nav_service.logger')
    @patch('src.service.page_nav_service.ScarperService')
    @patch('src.service.page_nav_service.DownloaderService')
    @patch('src.service.page_nav_service.DirectoryService')
    @patch('src.service.page_nav_service.ChromeDriver')
    def test_run_browser_stops_on_no_next_page(self, mock_chrome_driver, mock_dir_service,
                                              mock_downloader, mock_scraper, mock_logger):
        """Test run_browser stops pagination when next page link is not found."""
        # Setup mocks
        mock_driver_instance = Mock()
        mock_chrome = Mock()
        mock_chrome.get_driver.return_value = mock_driver_instance
        mock_chrome_driver.return_value = mock_chrome

        mock_dir_instance = Mock()
        mock_dir_instance.create_directory.return_value = "/videos/TEST"
        mock_dir_service.return_value = mock_dir_instance

        mock_downloader_instance = Mock()
        mock_downloader.return_value = mock_downloader_instance

        mock_scraper_instance = Mock()
        mock_scraper_instance.scrape_multiple_videos.return_value = [Mock()]
        mock_scraper.return_value = mock_scraper_instance

        # No next page link found
        mock_driver_instance.find_element.side_effect = NoSuchElementException("No next page")

        url = "https://example.com/videos"

        # Execute with number_of_pages=5 but only 1 page available
        run_browser(url, 5)

        # Verify scraper was only called once (pagination stopped)
        mock_scraper_instance.scrape_multiple_videos.assert_called_once()

        # Verify error was logged
        mock_logger.error.assert_called_once()

        # Verify browser was closed
        mock_chrome.close_browser.assert_called_once()


if __name__ == '__main__':
    unittest.main()