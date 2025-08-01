import os

from Downloader.logs.logger_config import setup_logging

logger = setup_logging(__name__)

class DirectoryHandler:
    @staticmethod
    def create_directory(url, parent_directory) -> str:

        logger.info(f"Creating Directory for {url}")

        name = url.rsplit("/")[-2]
        video_path = ""

        if parent_directory:
            logger.info("here")
            video_path = parent_directory.upper() + "/" + name.upper()
        else:
            logger.info("Here")
            video_path = name.upper()

        logger.info(f"Name of Directory: {name}")
        logger.info(f"Video Path: {video_path}")

        path = "/videos/" + video_path + '/'

        logger.info(f"Path of Directory: {path}")

        if not os.path.exists(path):
            os.makedirs(path)

        return path