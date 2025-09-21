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
            if "hits" in url:
                query = urlparse(url).query
                params = parse_qs(query)

                if "q" in params:
                    directory_name = params.get("q", [""])[0]
                else:
                   directory_name = params.get("spon",[""])[0]

                logger.info(f"Directory Name: {directory_name}")
            else:
                parts = urlparse(url).path.rstrip("/").split("/")
                logger.info(f"Parts: {parts}")
                directory_name = parts[-1]
                logger.info(f"Directory Name: {directory_name}")
        except IndexError:
            logger.info(f"Invalid URL Structure: {url}")
            raise ValueError(f"Cannot extract directory name from URL: {url}")

        parts = [p.upper() for p in (parent_directory, directory_name) if p]
        video_path = Path("/videos").joinpath(*parts)

        video_path.mkdir(parents=True, exist_ok=True)

        return str(video_path)

    @staticmethod
    def create_directory(parent_directory: str | None = None) -> str:
        """Create a directory for a given url under /videos."""
        logger.info(f"Creating Directory for {parent_directory}")
        path = Path("/videos").joinpath(parent_directory)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)