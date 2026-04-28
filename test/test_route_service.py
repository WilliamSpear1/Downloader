import unittest
from unittest.mock import Mock, patch, MagicMock, call
import threading

from src.service.route_service import RouteService


class TestRouteService(unittest.TestCase):

    def setUp(self):
        self.service = RouteService()

    def test_init(self):
        """Test RouteService initialization."""
        self.assertIsNone(self.service.task_id)

    def test_task_id_getter(self):
        """Test task_id property getter."""
        self.service._task_id = "test-task-123"
        self.assertEqual(self.service.task_id, "test-task-123")

    def test_task_id_setter(self):
        """Test task_id property setter."""
        self.service.task_id = "new-task-456"
        self.assertEqual(self.service.task_id, "new-task-456")

    @patch('src.service.route_service.Properties')
    @patch.object(RouteService, 'handle_hits')
    @patch.object(RouteService, 'check_task')
    def test_route_url_hits_website(self, mock_check_task, mock_handle_hits, mock_properties):
        """Test route_url routing to handle_hits for hits website."""
        mock_props = Mock()
        mock_properties.return_value = mock_props
        mock_props.get_website_names.return_value = {
            "hits": "hits.com",
            "free": "videos.com"
        }
        mock_handle_hits.return_value = "task-hits-123"

        url = "https://hits.com/video/123"
        result = self.service.route_url(url, None, 2)

        self.assertEqual(result, "task-hits-123")
        self.assertEqual(self.service.task_id, "task-hits-123")
        mock_handle_hits.assert_called_once_with(url, 2)
        mock_check_task.assert_called_once_with("task-hits-123", url)

    @patch('src.service.route_service.Properties')
    @patch.object(RouteService, 'handle_free')
    def test_route_url_free_website(self, mock_handle_free, mock_properties):
        """Test route_url routing to handle_free for free website."""
        mock_props = Mock()
        mock_properties.return_value = mock_props
        mock_props.get_website_names.return_value = {
            "hits": "hits.com",
            "free": "videos.com"
        }
        mock_handle_free.return_value = "task-free-456"

        url = "https://videos.com/video/456"
        parent_dir = "MyVideos"
        result = self.service.route_url(url, parent_dir, 3)

        self.assertEqual(result, "task-free-456")
        self.assertEqual(self.service.task_id, "task-free-456")
        mock_handle_free.assert_called_once_with(url, parent_dir, 3)

    @patch('src.service.route_service.Properties')
    def test_route_url_unknown_website(self, mock_properties):
        """Test route_url with unknown website returns None."""
        mock_props = Mock()
        mock_properties.return_value = mock_props
        mock_props.get_website_names.return_value = {
            "hits": "hits.com",
            "free": "videos.com"
        }

        url = "https://unknown.com/video/789"
        result = self.service.route_url(url, None, 1)

        self.assertIsNone(result)
        self.assertIsNone(self.service.task_id)

    @patch('src.service.route_service.requests.post')
    @patch('src.service.route_service.Properties')
    @patch('src.service.route_service.logger')
    def test_handle_hits_success(self, mock_logger, mock_properties, mock_post):
        """Test handle_hits successfully retrieves task_id from processor."""
        mock_props = Mock()
        mock_properties.return_value = mock_props
        mock_props.get_processor_url.return_value = "http://processor.local/process"

        mock_response = Mock()
        mock_response.json.return_value = {"task_id": "celery-task-abc123"}
        mock_post.return_value = mock_response

        url = "https://hits.com/video/123"
        result = self.service.handle_hits(url, 2)

        self.assertEqual(result, "celery-task-abc123")
        mock_post.assert_called_once_with(
            "http://processor.local/process",
            json={"url": url, "number_of_pages": 2}
        )
        mock_response.raise_for_status.assert_called_once()

    @patch('src.service.route_service.requests.post')
    @patch('src.service.route_service.Properties')
    def test_handle_hits_missing_task_id(self, mock_properties, mock_post):
        """Test handle_hits raises ValueError when response lacks task_id."""
        mock_props = Mock()
        mock_properties.return_value = mock_props
        mock_props.get_processor_url.return_value = "http://processor.local/process"

        mock_response = Mock()
        mock_response.json.return_value = {"status": "processing"}  # No task_id
        mock_post.return_value = mock_response

        url = "https://hits.com/video/123"

        with self.assertRaises(ValueError) as cm:
            self.service.handle_hits(url, 2)

        self.assertIn("task_id", str(cm.exception))

    @patch('src.service.route_service.requests.post')
    @patch('src.service.route_service.Properties')
    def test_handle_hits_http_error(self, mock_properties, mock_post):
        """Test handle_hits propagates HTTP errors."""
        mock_props = Mock()
        mock_properties.return_value = mock_props
        mock_props.get_processor_url.return_value = "http://processor.local/process"

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 500")
        mock_post.return_value = mock_response

        url = "https://hits.com/video/123"

        with self.assertRaises(Exception):
            self.service.handle_hits(url, 2)

    @patch('src.service.route_service.Properties')
    @patch('src.service.route_service.MonitorService')
    @patch('src.service.route_service.threading.Thread')
    def test_check_task_starts_monitoring_thread(self, mock_thread_class, mock_monitor, mock_properties):
        """Test check_task spawns a monitoring thread."""
        mock_props = Mock()
        mock_properties.return_value = mock_props
        mock_props.get_check_url.return_value = "http://checker.local/check"

        mock_monitor_instance = Mock()
        mock_monitor.return_value = mock_monitor_instance

        mock_thread = Mock()
        mock_thread_class.return_value = mock_thread

        task_id = "task-123"
        url = "https://hits.com/video"

        self.service.check_task(task_id, url)

        # Verify MonitorService was instantiated correctly
        mock_monitor.assert_called_once_with(task_id, "http://checker.local/check")

        # Verify Thread was created with correct target and args
        mock_thread_class.assert_called_once()
        call_kwargs = mock_thread_class.call_args[1]
        self.assertEqual(call_kwargs['target'], mock_monitor_instance.probe)
        self.assertEqual(call_kwargs['args'], (url,))
        self.assertTrue(call_kwargs['daemon'])

        # Verify thread was started
        mock_thread.start.assert_called_once()

    @patch('src.service.route_service.run_browser')
    def test_handle_free_success(self, mock_run_browser):
        """Test handle_free returns Celery task ID."""
        mock_task = Mock()
        mock_task.id = "celery-task-xyz789"
        mock_run_browser.delay.return_value = mock_task

        url = "https://xvideos.com/video/456"
        parent_dir = "MyVideos"
        num_pages = 3

        result = self.service.handle_free(url, parent_dir, num_pages)

        self.assertEqual(result, "celery-task-xyz789")
        mock_run_browser.delay.assert_called_once_with(url, num_pages, parent_dir)

    @patch('src.service.route_service.run_browser')
    def test_handle_free_returns_string_task_id(self, mock_run_browser):
        """Test handle_free converts task ID to string."""
        mock_task = Mock()
        mock_task.id = 12345  # Non-string ID
        mock_run_browser.delay.return_value = mock_task

        result = self.service.handle_free("https://videos.com/video", "ParentDir", 2)

        self.assertEqual(result, "12345")
        self.assertIsInstance(result, str)

    @patch('src.service.route_service.Properties')
    @patch.object(RouteService, 'handle_hits')
    @patch.object(RouteService, 'check_task')
    def test_route_url_default_number_of_pages(self, mock_check_task, mock_handle_hits, mock_properties):
        """Test route_url with default number_of_pages."""
        mock_props = Mock()
        mock_properties.return_value = mock_props
        mock_props.get_website_names.return_value = {
            "hits": "hits.com",
            "free": "videos.com"
        }
        mock_handle_hits.return_value = "task-123"

        url = "https://hits.com/video/123"
        result = self.service.route_url(url, None)

        mock_handle_hits.assert_called_once_with(url, 0)

    @patch('src.service.route_service.Properties')
    @patch.object(RouteService, 'handle_hits')
    @patch.object(RouteService, 'check_task')
    def test_route_url_multiple_calls(self, mock_check_task, mock_handle_hits, mock_properties):
        """Test route_url updates task_id on multiple calls."""
        mock_props = Mock()
        mock_properties.return_value = mock_props
        mock_props.get_website_names.return_value = {
            "hits": "hits.com",
            "free": "videos.com"
        }
        mock_handle_hits.side_effect = ["task-1", "task-2"]

        # First call
        result1 = self.service.route_url("https://hits.com/video/1", None)
        self.assertEqual(result1, "task-1")
        self.assertEqual(self.service.task_id, "task-1")

        # Second call
        result2 = self.service.route_url("https://hits.com/video/2", None)
        self.assertEqual(result2, "task-2")
        self.assertEqual(self.service.task_id, "task-2")


if __name__ == '__main__':
    unittest.main()