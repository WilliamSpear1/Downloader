import logging
import time

import requests

from src.model.video import Video
from src.service.directory_service import DirectoryService
from src.service.downloader_service import DownloaderService

logger = logging.getLogger(__name__)

class MonitorService:
    MAX_RETRIES = 20

    def __init__(self, task_id: str, check_url: str, interval: int=60):
        self._task_id = task_id
        self._check_url = check_url
        self._interval = interval

    def probe(self, url:str="") -> None:
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