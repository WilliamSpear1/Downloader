import os
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from logs.logger_config import setup_logging

logger = setup_logging(__name__)

class DirectoryHandler:

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
            directory_name = self._get_end(parts)

        if not directory_name:
            logger.error(f"Cannot extract directory name from the URL")
            raise ValueError(f"Cannot extract directory name from URL: {url}")

        # Create directory
        if parent_directory:
            video_path = '/videos' + '/' + parent_directory + '/' + directory_name + '/'
        else:
            video_path = '/videos' + '/' + directory_name + '/'

        os.makedirs(video_path, exist_ok=True)
        logger.info(f"Created directory: {video_path}")

        # Verify write permissions
        test_file = video_path / ".write_test"
        test_file.touch()
        test_file.unlink()

        logger.info(f"✓ Created directory: {video_path}")
        logger.info(f"✓ Permissions verified for: {video_path}")
        return str(video_path)

    @staticmethod
    def create_directory(parent_directory: str | None = None) -> str:
        """Create a directory for a given url under /videos."""
        logger.info(f"Creating Directory for {parent_directory}")
        path = Path("/videos").joinpath(parent_directory)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    @staticmethod
    def safe_dir_name(name: str) -> str:
        """Sanitize string to be filesystem-safe."""
        return re.sub(r"[^a-zA-Z0-9_\-]", "_", name).strip("_") or "default"

    def _get_end(self, parts: list) -> str:
        url_end = None

        if self._is_valid_end(parts[-1]):
            url_end = parts[-1]
        else:
            url_end = parts[-2]

        return url_end

    def _is_valid_end(self, end_url: str) -> bool:
        URL_MOST_POP = "most-popular"
        URL_TOP_RATED = "top-rated"

        if (end_url != URL_MOST_POP) and (end_url != URL_TOP_RATED):
            return True
        return False