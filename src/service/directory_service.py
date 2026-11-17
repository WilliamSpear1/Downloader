import logging
import os
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from ..configuration.logger_config import setup_logging

logger = setup_logging(__name__)

"""
Creates and manages download directories based on URL parsing and sanitization.
"""
class DirectoryService:
    """
    Create a directory for a given URL under the ./videos path.

    Parses the URL to extract a directory name. For 'hits' URLs, extracts
    the 'ps' or 'spon' query parameter; for other URLs, extracts the last
    valid path segment. The name is sanitized and uppercased before creating
    the directory.

    Args:
        url: The website URL to parse for the directory name.
        parent_directory: Optional top-level folder name for organizing downloads.

    Returns:
        The absolute path string of the created directory.

    Raises:
        ValueError: If the directory name cannot be extracted from the URL.
    """
    def create_directory(self, url: str, parent_directory: str | None = None) -> str:
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

        # Sanitize directory name
        directory_name = self.safe_dir_name(directory_name)

        # Build path
        parts = [p.upper() for p in (parent_directory, directory_name) if p]
        video_path = Path("./videos").joinpath(*parts)

        # Create directory
        try:
            video_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"CMD: {os.getcwd()}/{video_path}")
            logger.info(f"Target Path: {video_path.resolve()}")
            logger.info(f"Created directory: {video_path}")
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"Failed to create directory {video_path}. Error: {e.__class__.__name__} - {e}")
            raise

        return str(video_path)

    """
    Sanitize a string to be safe for use as a filesystem directory name.

    Replaces any character that is not alphanumeric, underscore, or hyphen
    with an underscore. Strips leading/trailing underscores; returns 'default'
    if the result is empty.

    Args:
        name: The raw directory name string.

    Returns:
        A filesystem-safe directory name string.
    """
    @staticmethod
    def safe_dir_name(name: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_\-]", "_", name).strip("_") or "default"

    """
    Extract the meaningful directory name from URL path segments.

    If the last segment is a valid name (not 'most-popular' or 'top-rated'),
    uses it; otherwise falls back to the second-to-last segment.

    Args:
        parts: List of URL path segments split by '/'.

    Returns:
        The extracted directory name string.
    """
    def _get_end(self, parts: list[str]) -> str:
        url_end = None

        if self._is_valid_end(parts[-1]):
            url_end = parts[-1]
        else:
            url_end = parts[-2]

        return url_end

    """
    Check if a URL path segment is a valid directory name.

    Segments 'most-popular' and 'top-rated' are considered invalid because
    they are site navigation labels, not content identifiers.

    Args:
        end_url: The URL path segment to validate.

    Returns:
        True if the segment is a valid directory name, False otherwise.
    """
    def _is_valid_end(self, end_url: str) -> bool:
        URL_MOST_POP = "most-popular"
        URL_TOP_RATED = "top-rated"

        if (end_url != URL_MOST_POP) and (end_url != URL_TOP_RATED):
            return True
        return False