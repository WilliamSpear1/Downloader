import unittest
from unittest.mock import Mock, patch, MagicMock, call
from selenium.common import NoSuchElementException

from src.service.page_nav_service import run_browser


class TestPageNavService(unittest.TestCase):
    """Tests for the run_browser Celery task covering browser lifecycle, page scraping, and video downloading."""

    @patch('src.service.page_nav_service.logger')
    @patch('src.service.page_nav_service.ScarperService')
    @patch('src.service.page_nav_service.DownloaderService')
    @patch('src.service.page_nav_service.DirectoryService')
    @patch('src.service.page_nav_service.ChromeDriver')
    def test_run_browser_single_page_success(
            self,
            mock_chrome_driver,
            mock_dir_service,
            mock_downloader,
            mock_scraper,
            mock_logger
    ):
        """
        Test that run_browser successfully processes a single page with videos found.

        Mocks ChromeDriver, DirectoryService, ScarperService, and DownloaderService to verify
        the full pipeline: browser launch, directory creation, video scraping, downloading,
        and browser closure when no next page exists.

        Asserts all services are called with correct arguments and browser is closed.
        """
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

        mock_driver_instance.find_element.side_effect = NoSuchElementException("No next page")

        run_browser("https://example.com/videos", 1, "TestParent")

        mock_chrome_driver.assert_called_once_with("https://example.com/videos")
        mock_chrome.get_driver.assert_called_once()
        mock_dir_instance.create_directory.assert_called_once_with("https://example.com/videos", "TestParent")
        mock_scraper.assert_called_once_with("https://example.com/videos", 1, "TestParent")
        mock_scraper_instance.scrape_multiple_videos.assert_called_once_with(mock_driver_instance, "/videos/TEST")
        mock_downloader_instance.download_videos.assert_called_once_with([mock_video1, mock_video2])
        mock_chrome.close_browser.assert_called_once()

    @patch('src.service.page_nav_service.logger')
    @patch('src.service.page_nav_service.ScarperService')
    @patch('src.service.page_nav_service.DownloaderService')
    @patch('src.service.page_nav_service.DirectoryService')
    @patch('src.service.page_nav_service.ChromeDriver')
    def test_run_browser_multiple_pages(
            self,
            mock_chrome_driver,
            mock_dir_service,
            mock_downloader,
            mock_scraper,
            mock_logger
    ):
        """
        Test that run_browser processes multiple pages sequentially with next-page navigation.

        Mocks two pages of videos where the first page has a next-page link and the second does not.
        Verifies the scraper and downloader are called once per page, and the next-page link
        is clicked via JavaScript execution.

        Asserts scraper and downloader are called twice with the correct video lists per page.
        """
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

        mock_next_link = Mock()
        mock_driver_instance.find_element.side_effect = [
            mock_next_link,
            NoSuchElementException("No next page")
        ]

        run_browser("https://example.com/videos", 2)

        self.assertEqual(mock_scraper_instance.scrape_multiple_videos.call_count, 2)
        self.assertEqual(mock_downloader_instance.download_videos.call_count, 2)
        mock_downloader_instance.download_videos.assert_any_call(mock_videos_page1)
        mock_downloader_instance.download_videos.assert_any_call(mock_videos_page2)

        mock_driver_instance.execute_script.assert_called_once()
        script_call = mock_driver_instance.execute_script.call_args[0]
        self.assertIn("click", script_call[0])
        mock_chrome.close_browser.assert_called_once()

    @patch('src.service.page_nav_service.logger')
    @patch('src.service.page_nav_service.ScarperService')
    @patch('src.service.page_nav_service.DownloaderService')
    @patch('src.service.page_nav_service.DirectoryService')
    @patch('src.service.page_nav_service.ChromeDriver')
    def test_run_browser_no_videos_found(
            self,
            mock_chrome_driver,
            mock_dir_service,
            mock_downloader,
            mock_scraper,
            mock_logger
    ):
        """
        Test that run_browser skips downloading when no videos are found on a page.

        Mocks an empty video list from the scraper. Verifies the downloader is never called
        and a warning is logged.

        Asserts download_videos is not called and the warning message is logged.
        """
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

        run_browser("https://example.com/videos", 1)

        mock_downloader_instance.download_videos.assert_not_called()
        mock_logger.warning.assert_called_with("No videos found on this page.")
        mock_chrome.close_browser.assert_called_once()

    @patch('src.service.page_nav_service.logger')
    @patch('src.service.page_nav_service.ScarperService')
    @patch('src.service.page_nav_service.DownloaderService')
    @patch('src.service.page_nav_service.DirectoryService')
    @patch('src.service.page_nav_service.ChromeDriver')
    def test_run_browser_exception_during_scraping(
            self,
            mock_chrome_driver,
            mock_dir_service,
            mock_downloader,
            mock_scraper,
            mock_logger
    ):
        """
        Test that run_browser handles exceptions gracefully and always closes the browser.

        Mocks a RuntimeError during scraping. Verifies the error is logged, the browser
        is closed in the finally block, and a finish message is logged.

        Asserts error is logged, browser is closed, and finish log is present.
        """
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

        run_browser("https://example.com/videos", 1)

        self.assertTrue(mock_logger.error.called)
        error_call = mock_logger.error.call_args_list[0]
        self.assertIn("Unexpected error", error_call[0][0])
        mock_chrome.close_browser.assert_called_once()

        finish_logs = [call[0][0] for call in mock_logger.info.call_args_list]
        self.assertTrue(any("finished" in log.lower() for log in finish_logs))

    @patch('src.service.page_nav_service.logger')
    @patch('src.service.page_nav_service.WebDriverWait')
    @patch('src.service.page_nav_service.ScarperService')
    @patch('src.service.page_nav_service.DownloaderService')
    @patch('src.service.page_nav_service.DirectoryService')
    @patch('src.service.page_nav_service.ChromeDriver')
    def test_run_browser_wait_for_next_page(
            self,
            mock_chrome_driver,
            mock_dir_service,
            mock_downloader,
            mock_scraper,
            mock_wait,
            mock_logger
    ):
        """
        Test that run_browser uses WebDriverWait to wait for the next-page link to be clickable.

        Mocks WebDriverWait and verifies it's called with a 40-second timeout before clicking
        the next-page link.

        Asserts WebDriverWait is initialized correctly and the until() method is called.
        """
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
            [Mock()],
            NoSuchElementException("No more pages")
        ]
        mock_scraper.return_value = mock_scraper_instance

        mock_next_link = Mock()
        mock_driver_instance.find_element.side_effect = [
            mock_next_link,
            NoSuchElementException("No next page")
        ]

        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance

        run_browser("https://example.com/videos", 2)

        mock_wait.assert_called_once_with(mock_driver_instance, 40)
        mock_wait_instance.until.assert_called_once()
        mock_chrome.close_browser.assert_called_once()

    @patch('src.service.page_nav_service.logger')
    @patch('src.service.page_nav_service.ScarperService')
    @patch('src.service.page_nav_service.DownloaderService')
    @patch('src.service.page_nav_service.DirectoryService')
    @patch('src.service.page_nav_service.ChromeDriver')
    def test_run_browser_default_parent_directory(
            self,
            mock_chrome_driver,
            mock_dir_service,
            mock_downloader,
            mock_scraper,
            mock_logger
    ):
        """
        Test that run_browser uses an empty string as the default parent_directory.

        Calls run_browser without specifying parent_directory and verifies that both
        DirectoryService and ScarperService receive an empty string for parent_directory.

        Asserts create_directory and scraper init are called with empty parent_directory.
        """
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

        run_browser("https://example.com/videos", 1)

        mock_dir_instance.create_directory.assert_called_once_with("https://example.com/videos", "")
        mock_scraper.assert_called_once_with("https://example.com/videos", 1, "")

    @patch('src.service.page_nav_service.logger')
    @patch('src.service.page_nav_service.ScarperService')
    @patch('src.service.page_nav_service.DownloaderService')
    @patch('src.service.page_nav_service.DirectoryService')
    @patch('src.service.page_nav_service.ChromeDriver')
    def test_run_browser_stops_on_no_next_page(
            self,
            mock_chrome_driver,
            mock_dir_service,
            mock_downloader,
            mock_scraper,
            mock_logger
    ):
        """
        Test that run_browser stops pagination early when no next-page link is found.

        Requests 5 pages but mocks no next-page link after the first page. Verifies the
        scraper is called only once and an error is logged for the missing next page.

        Asserts scraper is called once, error is logged, and browser is closed.
        """
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

        mock_driver_instance.find_element.side_effect = NoSuchElementException("No next page")

        run_browser("https://example.com/videos", 5)

        mock_scraper_instance.scrape_multiple_videos.assert_called_once()
        mock_logger.error.assert_called_once()
        mock_chrome.close_browser.assert_called_once()

if __name__ == '__main__':
    unittest.main()