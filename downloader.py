import logging
from yt_dlp.utils import DownloadError
from yt_dlp import YoutubeDL
from data.video import Video

logger = logging.getLogger(__name__)

class Downloader:
    def skip_short_videos(info_dict, incomplete):
        duration = info_dict.get("duration")
        if duration is not None and duration < 20 * 60:  # 20 mins in seconds
            logger.info(f"Video too short: {duration / 60:.1f} minutes")
            return f"Video too short: {duration / 60:.1f} minutes"
        return None  # Accept the video

    ydl_opts = {
        # General Settings
        'quiet': True,
        'ignoreerrors': True,
        'no_abort_on_error': True,
        'nooverwrites': True,
        'ratelimit': 500000,  # ~5 MB/s
        'downloader': 'ffmpeg',
        'hls_use_mpegts': True,
        'check_formats': True,
        'extractor_args': {
            'youtube': {
                "player_client": ['android', 'web'],
                'skip': ['dash', 'hls']  # Skip DASH formats that often cause issues
            }
        },

         # Stop if a fragment is missing
        'abort_on_unavailable_fragments': False,
        'format': (
            'bestvideo[height>=720][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/'
            'best[height>=720][ext=mp4]/'
            'best[height>=720]'
        ),
        'retries': 10,                                 # number of times to retry the whole download
        'fragment_retries': 20,                 # retries per fragment
        'retry_streams': 5,                        # retry the whole stream if fragments fail
        'socket_timeout': 60,                    # increase timeout to handle slow fragments
        "match_filter": skip_short_videos, # 1200 seconds = 20 mins
        'merge_output_format': 'mp4',      # Merge video and audio into mp4 container
        'force-write-archive': True,                 # Force writing the archive file to prevent duplicates
        'simulate': False,                          # Set to True for testing without downloading
        'download_archive': '/app/log/downloaded_videos.txt'  # Keep track of downloaded videos to avoid duplicates
    }

    def download_videos(self, videos:list) -> None:
        logger.info(f"The Number of videos set for downloading: {len(videos)}")
        for video in videos:
            self.download_video(video)

    def download_video(self, video:Video) -> None:
        video_path = f"{video.path}/{video.title}"

        opts = self.ydl_opts.copy()
        opts['outtmpl'] = video_path + ".%(ext)s"

        with YoutubeDL(opts) as ydl:
            # Extract info *without downloading* to see available formats
            try:
                # probe metadata
                # safe to download
                logger.info(f"Downloading {video.title}")
                result = ydl.download([video.link])

                if result != 0:
                    logger.warning(f"Skipping {video.title}: download failed with code {result}")
            except DownloadError as e:
                logger.warning(f"Skipping {video.title}: {e}")
            except Exception as e:
                logger.error(f"Skipping {video.title}: Crash Report: ({e})")
            return None
