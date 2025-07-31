import os

from Downloader.logs.logger_config import setup_logging

logger = setup_logging(__name__)

class DirectoryHandler:
    @staticmethod
    def create_directory(url) -> str:
        logger.info(f"Creating Directory for {url}")

        name = url.rsplit("/")[-3]
        video_path = name.upper()

        logger.info(f"Name of Directory: {name}")

        path = "/videos/" + video_path + '/'

        logger.info(f"Path of Directory: {path}")

        if not os.path.exists(path):
            os.makedirs(path)

        return path