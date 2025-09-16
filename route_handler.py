import threading

import requests

from logs.logger_config import setup_logging
from properties import Properties
from scarper import Scarper
from tasks import run_browser

logger = setup_logging(__name__)

class RouteHandler:
    def __init__(self, properties: Properties):
        self._task_id = None
        self.properties = properties

    @property
    def task_id(self):
        return self._task_id

    @task_id.setter
    def task_id(self, value):
        self._task_id = value

    def route_url(self, url:str, parent_directory:str, number_of_pages:int = 0) -> str:
        website_names = self.properties.get_website_names()
        url_processor = self.properties.get_url()

        for key, value in website_names.items():
            if value in url:
                if key == "hits":
                    self._task_id = self.handle_hits(url, url_processor)
                    break
                elif key == "free":
                    self._task_id = self.handle_free(url, parent_directory, number_of_pages)
                    break

        return self._task_id

    @staticmethod
    def handle_free(url:str, parent_directory:str, number_of_pages:int = 0) -> str:
        task = run_browser.delay(url, number_of_pages, parent_directory)
        return str(task.id)

    @staticmethod
    def handle_hits(fetch_url:str, start_url:str) -> str:
        logger.info(f"URL: {fetch_url}")
        logger.info(f"URL PROCESSOR: {start_url}")

        response = requests.post(
            start_url,
            json={"url": fetch_url}
        )
        response.raise_for_status()
        data = response.json()

        if "task_id" not in data:
            raise ValueError("Response JSON does not contain 'task_id'")
        task_id = data['task_id']

        logger.info(f"Task Id from URL Processor: {task_id}")
        return task_id