import os
import time

import requests

from data.video import Video
from directory_handler import DirectoryHandler
from downloader import Downloader
from logs.logger_config import setup_logging

logger = setup_logging(__name__)

class Monitor:
    def __init__(self, task_id: str, check_url: str, parent_directory: str="", interval: int=10):
        self._task_id = task_id
        self._check_url = check_url
        self._parent_directory = parent_directory
        self._interval = interval

    def probe(self, parent_directory:str="") -> None:
        downloader = Downloader()
        directory_handler = DirectoryHandler()
        status  = None

        while status is None:
            status = self.monitor_task()
            if status is None:
                time.sleep(self._interval)

        videos = [Video(title=title, link=link) for title, link in status.items()]
        logger.info(f"Found {len(videos)} videos on the page.")

        for video in videos:
            logger.info(f"Link: {video.link}")
            logger.info(f"Title: {video.title}")

            video.path = directory_handler.create_directory_title(title=video.title, parent_directory=parent_directory)
            logger.info(f"Video Path Variable: {video.path}")

        if videos:
            downloader.download_videos(videos)
        else:
            logger.warning("No videos found on this page.")
        return None

    def monitor_task(self) -> dict | None:
        logger.info(f"Probing for: {self._task_id}")
        logger.info(f"CHECK URL: {self._check_url}")

        try:
            response = requests.get(
                f"{self._check_url}/{self._task_id}",
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            status = data.get ('status')
            logger.info(f"Task {self._task_id} status: {data.get('status')}, result: {data.get('result')}")
            if status == 'Success':
                return data.get('result')
            elif status == 'Pending':
                return None
            else:
                return status
        except requests.RequestException as e:
            logger.error(f"Error probing task {self._task_id}: {e}")
            return None