import json
import logging
from typing import Any

from yt_dlp.utils import DownloadError
from yt_dlp import YoutubeDL
from src.models.video import Video

logger = logging.getLogger(__name__)

class Downloader:
    def download_videos(self, videos:list) -> None:
        logger.info(f"The Number of videos set for downloading: {len(videos)}")
        opts = self.safe_load_opts()
        opts['match_filter'] = self.skip_short_videos #Filter out videos shorter than 20 minutes

        for video in videos:
            self.download_video(video, opts)
        return None

    def download_video(self, video:Video, opts:Any) -> None:
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

    def skip_short_videos(self, info_dict, *, incomplete) -> str|None:
        duration = info_dict.get("duration")

        if incomplete and duration is None:
            logger.warning("Video is incomplete and duration is unknown. Skipping.")
            return None

        if duration is not None and duration < 20 * 60:  # 20 mins in seconds
            logger.info(f"Video too short: {duration / 60:.1f} minutes")
            return f"Video too short: {duration / 60:.1f} minutes"
        return None  # Accept the video

    def safe_load_opts(self) -> Any:
        try:
            with open("src/configuration/yt_dlp.json", "r") as file:
                opts = json.load(file)
                logger.info("Loaded yt_dlp options from yt_dlp_opts.json")
                return opts
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load yt_dlp options: {e}. Using default options.")
            return {}