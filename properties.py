import configparser
import os

from logs.logger_config import setup_logging

logger = setup_logging(__name__)

class Properties:
    def __init__(self):
        self._website_names = {}
        self._url = ""

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
       self._url  = value

    @property
    def website_names(self):
        return self._website_names

    @website_names.setter
    def website_names(self, value):
        self._website_names = value

    def get_website_names(self) -> dict:
        hits = os.environ.get('HITS')
        free = os.environ.get('FREE')
        many = os.environ.get('MANY')

        logger.info(f"HITS: {hits}")
        logger.info(f"FREE: {free}")
        logger.info(f"MANY: {many}")

        self._website_names = {
            "hits": hits,
            "free": free,
            "many": many
        }

        return self._website_names

    def get_url(self) -> str:
        url = os.environ.get('URL_PROCESSOR')
        logger.info(f"URL: {url}")
        self._url = url

        logger.info(f"URL: {self._url}")

        return self._url