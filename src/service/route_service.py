import logging
import threading

import requests

from ..configuration.logger_config import setup_logging
from ..configuration.properties import Properties
from .page_nav_service import run_browser
from .monitor_service import MonitorService

logger = setup_logging(__name__)

"""
Routes incoming download requests to the appropriate processing backend (local Celery or external service).
"""
class RouteService:
    def __init__(self) -> None:
        self._task_id = None

    @property
    def task_id(self) -> str | None:
        return self._task_id

    @task_id.setter
    def task_id(self, value: str) -> None:
        self._task_id = value

    """
    Route a download request to the appropriate handler and return the task ID.

    Currently routes to handle_free, which queues a local Celery task.

    Args:
        url: The website URL to scrape for videos.
        parent_directory: The top-level folder name for organizing downloads.
        number_of_pages: The number of pages to scrape (defaults to 0).

    Returns:
        The Celery task ID string.

    Raises:
        TypeError: If the task ID is None after routing.
    """
    def route_url(
            self,
            url: str,
            parent_directory: str,
            number_of_pages: int = 0
    ) -> str:
        self._task_id = self.handle_free(url, parent_directory, number_of_pages)

        if self._task_id is None:
            raise TypeError("Expected Task Id to be provided a value.")

        return self._task_id

    """
    Delegate URL processing to an external service and return the remote task ID.

    Sends the URL and page count to the URL_PROCESSOR service via POST,
    then returns the task_id from the response.

    Args:
        fetch_url: The URL to be processed by the external service.
        number_of_pages: The number of pages to scrape (defaults to 0).

    Returns:
        The task ID string from the external service response.

    Raises:
        ValueError: If the response JSON does not contain 'task_id'.
    """
    def handle_hits(self, fetch_url: str, number_of_pages: int = 0) -> str:
        properties = Properties()
        url_processor = properties.get_processor_url()

        logger.info(f"URL: {fetch_url}")
        logger.info(f"URL PROCESSOR: {url_processor}")

        logger.info("Sending off data to URL Processor.")
        response = requests.post(
            url_processor,
            json={"url": fetch_url, "number_of_pages": number_of_pages}
        )
        response.raise_for_status()
        data = response.json()

        if "task_id" not in data:
            raise ValueError("Response JSON does not contain 'task_id'")
        task_id = data['task_id']

        logger.info(f"Task Id from URL Processor: {task_id}")
        return task_id

    """
    Start a background thread to monitor an external task's status.

    Polls the CHECK_URL endpoint until the task completes, then triggers
    downloading via MonitorService.

    Args:
        task_id: The external task ID to monitor.
        url: Optional URL used for directory creation after task completion.
    """
    def check_task(self, task_id: str, url: str = "") -> None:
        properties = Properties()

        check_url = properties.get_check_url()
        monitor = MonitorService(task_id, check_url)
        thread = threading.Thread(target=monitor.probe, args=(url,), daemon=True)
        thread.start()

    """
    Queue a local Celery task to scrape and download videos from the given URL.

    Args:
        url: The website URL to scrape for videos.
        parent_directory: The top-level folder name for organizing downloads.
        number_of_pages: The number of pages to scrape (defaults to 0).

    Returns:
        The local Celery task ID string.
    """
    @staticmethod
    def handle_free(url: str, parent_directory: str, number_of_pages: int = 0) -> str:
        task = run_browser.delay(url, number_of_pages, parent_directory)
        return str(task.id)
