import logging
import os

logger = logging.getLogger(__name__)

class Properties:
    def __init__(self):
        self._website_names = {}
        self._url = ""

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value) -> None:
       self._url  = value

    @property
    def website_names(self) -> dict:
        return self._website_names

    @website_names.setter
    def website_names(self, value) -> None:
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

    def get_processor_url(self) -> str|None:
        url = os.environ.get('URL_PROCESSOR')
        logger.info(f"URL: {url}")
        self._url = url

        logger.info(f"URL: {self._url}")

        return self._url

    def get_check_url(self) -> str|None:
        url = os.environ.get('CHECK_URL')
        logger.info(f"URL: {url}")
        self._url = url

        logger.info(f"URL: {self._url}")

        return self._url
