import logging
import threading

import requests

from ..configuration.logger_config import setup_logging
from ..configuration.properties import Properties
from .page_nav_service import run_browser
from .monitor_service import MonitorService

logger = setup_logging(__name__)

class RouteService:
    def __init__(self):
        self._task_id = None

    @property
    def task_id(self):
        return self._task_id

    @task_id.setter
    def task_id(self, value):
        self._task_id = value

    def route_url(self, url:str, parent_directory:str, number_of_pages:int = 0) -> str:
        properties = Properties()
        website_names = properties.get_website_names()

        for key, value in website_names.items():
            if value in url:
                if key == "hits":
                    self._task_id = self.handle_hits(url, number_of_pages)
                    self.check_task(self._task_id, url)
                    break
                elif key == "free":
                    self._task_id = self.handle_free(url, parent_directory, number_of_pages)
                    break

        return self._task_id

    def handle_hits(self, fetch_url:str, number_of_pages:int = 0) -> str:
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

    def check_task(self, task_id:str,url:str="") -> None:
        properties = Properties()

        check_url = properties.get_check_url()
        monitor = MonitorService(task_id, check_url)
        thread = threading.Thread(target=monitor.probe, args=(url,), daemon=True)
        thread.start()

    @staticmethod
    def handle_free(url: str, parent_directory: str, number_of_pages: int = 0) -> str:
        task = run_browser.delay(url, number_of_pages, parent_directory)
        return str(task.id)
