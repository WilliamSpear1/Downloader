import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from logs.logger_config import setup_logging

logger = setup_logging(__name__)

class DirectoryHandler:
    @staticmethod
    def create_directory_url(url:str, parent_directory:str | None = None) -> str:
        """Create a directory for a given url under /videos."""
        logger.info(f"Creating Directory for {url}")

        try:
                parts = urlparse(url).path.rstrip("/").split("/")
                logger.info(f"Parts: {parts}")
                name = parts[-1]
                logger.info(f"Name: {name}")
        except IndexError:
            logger.info(f"Invalid URL Structure: {url}")
            raise ValueError(f"Cannot extract directory name from URL: {url}")

        parts = [p.upper() for p in (parent_directory, name) if p]
        video_path = Path("/videos").joinpath(*parts)

        video_path.mkdir(parents=True, exist_ok=True)

        return str(video_path)

    @staticmethod
    def create_directory_title(title: str, parent_directory: str | None = None) -> str:
        """Create a directory for a given url under /videos."""
        logger.info(f"Creating Directory for {title}")

        if parent_directory:
            path = parent_directory.upper() + "/" +  title
        else:
            path = title

        video_path = "/videos/" + path

        if not os.path.exists(video_path):
            os.makedirs(video_path)

        return video_path
