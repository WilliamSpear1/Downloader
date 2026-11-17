import json
from typing import Any

from yt_dlp.utils import DownloadError
from yt_dlp import YoutubeDL

from ..configuration.logger_config import setup_logging
from ..model.video import Video

logger = setup_logging(__name__)

"""
Downloads videos using yt-dlp, with support for duration filtering and configurable options.
"""
class DownloaderService:
    """
    Download all videos in the given list using yt-dlp.

    Loads configuration options and applies a duration filter to skip
    videos shorter than 20 minutes.

    Args:
        videos: A list of Video objects to download.
    """
    def download_videos(self, videos: list[Video]) -> None:
        logger.info(f"The Number of videos set for downloading: {len(videos)}")
        opts = self.safe_load_opts()
        opts['match_filter'] = self.skip_short_videos #Filter out videos shorter than 20 minutes

        for video in videos:
            self.download_video(video, opts)
        return None

    """
    Download a single video using yt-dlp with the given options.

    Sets the output template path and attempts to download the video,
    logging any errors or failures.

    Args:
        video: The Video object containing the title, link, and path.
        opts: The yt-dlp configuration options dictionary.
    """
    def download_video(self, video: Video, opts: Any) -> None:
        video_path = f"{video.path}/{video.title}"

        opts['outtmpl'] = video_path + ".%(ext)s"

        with YoutubeDL(opts) as ydl:
            try:
                logger.info(f"Downloading {video.title}")
                result = ydl.download([video.link])

                if result != 0:
                    logger.warning(f"Skipping {video.title}: download failed with code {result}")
            except DownloadError as e:
                logger.warning(f"Skipping {video.title}: {e}")
            except Exception as e:
                logger.error(f"Skipping {video.title}: Crash Report: ({e})")
            return None

    """
    yt-dlp match_filter callback to skip videos shorter than 20 minutes.

    Args:
        info_dict: Dictionary containing video metadata from yt-dlp.
        incomplete: Whether the video info is incomplete (duration unknown).

    Returns:
        A rejection reason string if the video should be skipped, or None to accept it.
    """
    def skip_short_videos(self, info_dict: dict, *, incomplete: bool) -> str | None:
        duration = info_dict.get("duration")

        if incomplete and duration is None:
            logger.warning("Video is incomplete and duration is unknown. Skipping.")
            return None

        if duration is not None and duration < 20 * 60:  # 20 mins in seconds
            logger.info(f"Video too short: {duration / 60:.1f} minutes")
            return f"Video too short: {duration / 60:.1f} minutes"
        return None  # Accept the video

    """
    Load yt-dlp configuration options from a JSON file.

    Reads the options from /app/src/configuration/yt_dlp.json. Falls back
    to an empty dict if the file is missing or contains invalid JSON.

    Returns:
        A dictionary of yt-dlp options, or an empty dict on failure.
    """
    def safe_load_opts(self) -> Any:
        try:
            with open("/app/src/configuration/yt_dlp.json", "r") as file:
                opts = json.load(file)
                logger.info("Loaded yt_dlp options from yt_dlp_opts.json")
                return opts
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load yt_dlp options: {e}. Using default options.")
            return {}