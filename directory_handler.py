import os
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from logs.logger_config import setup_logging

logger = setup_logging(__name__)

class DirectoryHandler:
    @staticmethod
    def safe_dir_name(name: str) -> str:
        """Sanitize string to be filesystem-safe."""
        return re.sub(r"[^a-zA-Z0-9_\-]", "_", name).strip("_") or "default"

    def create_directory_url(self, url: str, parent_directory: str | None = None) -> str:
        """Create a directory for a given url under /videos path."""
        logger.info(f"Creating Directory for {url}")

        directory_name = None
        parsed = urlparse(url)

        if "hits" in url:
            params = parse_qs(parsed.query)
            directory_name = params.get("ps", [None])[0] or params.get("spon", [None])[0]
        else:
            parts = parsed.path.rstrip("/").split("/")
            if parts and parts[-1]:
                directory_name = parts[-1]

        if not directory_name:
            logger.error(f"Cannot extract directory name from the URL")
            raise ValueError(f"Cannot extract directory name from URL: {url}")

        # Sanitize directory name
        directory_name = self.safe_dir_name(directory_name)

        # Build path
        parts = [p.upper() for p in (parent_directory, directory_name) if p]
        video_path = Path("/videos").joinpath(*parts)

        # Create directory
        video_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {video_path}")

        return str(video_path)

    @staticmethod
    def create_directory(parent_directory: str | None = None) -> str:
        """Create a directory for a given url under /videos."""
        logger.info(f"Creating Directory for {parent_directory}")
        path = Path("/videos").joinpath(parent_directory)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)