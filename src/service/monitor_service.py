import time

import requests

from ..configuration.logger_config import setup_logging
from ..model.video import Video
from .directory_service import DirectoryService
from .downloader_service import DownloaderService

logger = setup_logging(__name__)

"""
Monitors an external task's status by polling a check URL, then downloads the resulting videos.
"""
class MonitorService:

    MAX_RETRIES = 20

    """Initialize the monitor with the task ID, check endpoint, and polling interval.

    Args:
        task_id: The external task ID to monitor.
        check_url: The base URL endpoint for checking task status.
        interval: Seconds to wait between polling attempts (defaults to 60).
    """
    def __init__(
            self,
            task_id: str,
            check_url: str,
            interval: int = 60
    ) -> None:
        self._task_id = task_id
        self._check_url = check_url
        self._interval = interval

    """Poll the external task status until it completes or times out, then download any resulting videos.

    Repeatedly calls monitor_task up to MAX_RETRIES times at the configured interval.
    If the task succeeds, creates a download directory and downloads the videos.

    Args:
        url: Optional URL used for creating the download directory.
    """
    def probe(self, url: str = "") -> None:
        downloader = DownloaderService()
        directory_handler = DirectoryService()
        status = None
        videos = []

        for _ in range(self.MAX_RETRIES):
            status = self.monitor_task()

            if status is None:
                time.sleep(self._interval)
            else:
                break

        if url:
            path = directory_handler.create_directory(url)

        if status is None:
            logger.warning(f"{self._task_id} failed monitoring timed out after {self.MAX_RETRIES} retries.")
        else:
            videos = [Video(title=title, link=link, path=path) for title, link in status.items()]

        logger.info(f"Found {len(videos)} videos on the page.")

        if videos:
            downloader.download_videos(videos)
        else:
            logger.warning("No videos found on this page.")

        return None

    """Check the current status of the external task via the check URL.

    Sends a GET request to the check endpoint with the task ID. Returns the
    result dict if the task succeeded, None if still pending or on error.

    Returns:
        A dict of video title-link pairs if the task succeeded, or None otherwise.
    """
    def monitor_task(self) -> dict | None:
        try:
            response = requests.get(
                f"{self._check_url}/{self._task_id}",
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            status = data.get('status')

            logger.info(f"Task {self._task_id} status: {data.get('status')}, result: {data.get('result')}")

            if status == 'Success':
                return data.get('result')
            elif status == 'Pending':
                return None
            else:
                logger.warning(f"Failed to retrieve status for {self._task_id}")
                return None
        except requests.RequestException as e:
            logger.error(f"Error probing task {self._task_id}: {e}")
            return None