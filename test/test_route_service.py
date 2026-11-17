import unittest
from unittest.mock import Mock, patch, MagicMock, call

from src.service.route_service import RouteService


class TestRouteService(unittest.TestCase):
    """Tests for RouteService covering URL routing, task ID management, and external service integration."""

    def setUp(self) -> None:
        """Set up a RouteService instance for each test."""
        self.service = RouteService()

    def test_init(self):
        """
        Test that a newly created RouteService has no task ID set.

        Asserts task_id is None after initialization.
        """
        self.assertIsNone(self.service.task_id)

    def test_task_id_getter(self):
        """
        Test that the task_id property returns the stored value.

        Sets an internal task ID and verifies the getter returns it.

        Asserts the returned task_id matches the set value.
        """
        self.service._task_id = "test-task-123"
        self.assertEqual(self.service.task_id, "test-task-123")

    def test_task_id_setter(self):
        """
        Test that the task_id property stores the assigned value.

        Sets a task ID via the property and verifies it's stored correctly.

        Asserts the task_id matches the assigned value.
        """
        self.service.task_id = "new-task-456"
        self.assertEqual(self.service.task_id, "new-task-456")

    @patch('src.service.route_service.Properties')
    @patch.object(RouteService, 'handle_hits')
    @patch.object(RouteService, 'check_task')
    def test_route_url_hits_website(
            self,
            mock_check_task,
            mock_handle_hits,
            mock_properties
    ):
        """
        Test that route_url correctly routes a Hits website URL to handle_hits.

        Mocks Properties to recognize a Hits URL and handle_hits to return a task ID.
        Verifies handle_hits is called with the URL and page count, and check_task
        is called to monitor the external task.

        Asserts the returned task ID matches and both handle_hits and check_task are called.
        """
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
        """
        Test that route_url correctly routes a free website URL to handle_free.

        Mocks Properties to recognize a free URL and handle_free to return a task ID.
        Verifies handle_free is called with the URL, parent directory, and page count.

        Asserts the returned task ID matches and handle_free is called with correct args.
        """
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
        """
        Test that route_url returns None for an unrecognized website.

        Mocks Properties with known website names that don't match the given URL.
        Verifies the service returns None when no handler matches.

        Asserts both the return value and task_id are None.
        """
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
    def test_handle_hits_success(
            self,
            mock_logger,
            mock_properties,
            mock_post
    ):
        """
        Test that handle_hits successfully retrieves a task ID from the external processor.

        Mocks a successful POST request to the URL_PROCESSOR service returning a task_id.
        Verifies the correct payload is sent and the task_id is extracted.

        Asserts the returned task ID matches and the POST request has correct args.
        """
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
        """
        Test that handle_hits raises ValueError when the response lacks a task_id.

        Mocks a POST response that returns JSON without a 'task_id' key.
        Verifies the service raises a ValueError.

        Asserts ValueError is raised with 'task_id' in the message.
        """
        mock_props = Mock()
        mock_properties.return_value = mock_props
        mock_props.get_processor_url.return_value = "http://processor.local/process"

        mock_response = Mock()
        mock_response.json.return_value = {"status": "processing"}
        mock_post.return_value = mock_response

        url = "https://hits.com/video/123"

        with self.assertRaises(ValueError) as cm:
            self.service.handle_hits(url, 2)

        self.assertIn("task_id", str(cm.exception))

    @patch('src.service.route_service.requests.post')
    @patch('src.service.route_service.Properties')
    def test_handle_hits_http_error(self, mock_properties, mock_post):
        """
        Test that handle_hits propagates HTTP errors from the external processor.

        Mocks a POST response that raises an exception on raise_for_status.
        Verifies the exception is propagated to the caller.

        Asserts the exception is raised.
        """
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
    def test_check_task_starts_monitoring_thread(
            self,
            mock_thread_class,
            mock_monitor,
            mock_properties
    ):
        """
        Test that check_task spawns a daemon thread to monitor an external task.

        Mocks MonitorService and threading.Thread to verify a monitoring thread is created
        with the correct target (probe method) and args, and that it's started as a daemon.

        Asserts MonitorService and Thread are initialized correctly and thread.start is called.
        """
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

        mock_monitor.assert_called_once_with(task_id, "http://checker.local/check")

        mock_thread_class.assert_called_once()
        call_kwargs = mock_thread_class.call_args[1]
        self.assertEqual(call_kwargs['target'], mock_monitor_instance.probe)
        self.assertEqual(call_kwargs['args'], (url,))
        self.assertTrue(call_kwargs['daemon'])

        mock_thread.start.assert_called_once()

    @patch('src.service.route_service.run_browser')
    def test_handle_free_success(self, mock_run_browser):
        """
        Test that handle_free queues a Celery task and returns the task ID.

        Mocks run_browser.delay to return a task object with an ID.
        Verifies the delay method is called with correct args and the ID is returned.

        Asserts the returned task ID matches and run_browser.delay is called correctly.
        """
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
        """
        Test that handle_free converts a non-string task ID to a string.

        Mocks run_browser.delay to return a task with an integer ID.
        Verifies the ID is converted to a string before returning.

        Asserts the returned value is a string matching the integer ID.
        """
        mock_task = Mock()
        mock_task.id = 12345
        mock_run_browser.delay.return_value = mock_task

        result = self.service.handle_free("https://videos.com/video", "ParentDir", 2)

        self.assertEqual(result, "12345")
        self.assertIsInstance(result, str)

    @patch('src.service.route_service.Properties')
    @patch.object(RouteService, 'handle_hits')
    @patch.object(RouteService, 'check_task')
    def test_route_url_default_number_of_pages(
            self,
            mock_check_task,
            mock_handle_hits,
            mock_properties
    ):
        """
        Test that route_url defaults number_of_pages to 0 when not specified.

        Calls route_url without number_of_pages and verifies handle_hits receives 0.

        Asserts handle_hits is called with number_of_pages=0.
        """
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
    def test_route_url_multiple_calls(
            self,
            mock_check_task,
            mock_handle_hits,
            mock_properties
    ):
        """
        Test that route_url updates task_id on subsequent calls.

        Makes two consecutive route_url calls and verifies the task_id property
        is updated each time to reflect the latest task.

        Asserts each call returns the correct task ID and task_id property is updated.
        """
        mock_props = Mock()
        mock_properties.return_value = mock_props
        mock_props.get_website_names.return_value = {
            "hits": "hits.com",
            "free": "videos.com"
        }
        mock_handle_hits.side_effect = ["task-1", "task-2"]

        result1 = self.service.route_url("https://hits.com/video/1", None)
        self.assertEqual(result1, "task-1")
        self.assertEqual(self.service.task_id, "task-1")

        result2 = self.service.route_url("https://hits.com/video/2", None)
        self.assertEqual(result2, "task-2")
        self.assertEqual(self.service.task_id, "task-2")

if __name__ == '__main__':
    unittest.main()