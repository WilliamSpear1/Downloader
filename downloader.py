from yt_dlp import YoutubeDL

from data.video import Video
from logs.logger_config import setup_logging

logger = setup_logging(__name__)

class Downloader:
    ydl_opts = {
        # General Settings
        'quiet': True,
        'ignoreerrors': False,
        'nooverwrites': True,
        'ratelimit': 500000,  # ~5 MB/s
        'downloader': 'ffmpeg',
        'hls_use_mpegts': True,

         # Stop if a fragment is missing
        'abort_on_unavailable_fragments': True,
        'format': (
            'bestvideo[height>=720][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/'
            'best[height>=720][ext=mp4]/'
            'best[height>=720]'
        ),

        # Merge video and audio into mp4 container
        'merge_output_format': 'mp4'
    }

    def download_videos(self, videos:list) -> None:
        logger.info(f"The Number of videos set for downloading: {len(videos)}")
        for video in videos:
            self.download_video(video)

    def download_video(self, video:Video) -> None:
        logger.info(f"Video Path: {video.path}")
        logger.info(f"Video Title: {video.title}")
        logger.info(f"Video Link: {video.link}")
        video_path = video.path + "/" + video.title
        logger.info(f"Path: {video_path}")

        opts = self.ydl_opts.copy()
        opts['outtmpl'] = video_path + ".%(ext)s"

        with YoutubeDL(opts) as ydl:
            # Extract info *without downloading* to see available formats
            try:
                # probe metadata
                info = ydl.extract_info(video.link, download=False)
            except Exception as e:
                logger.warning(f"Skipping {video.title}: failed to extract info ({e})")
                return

            if not info or 'formats' not in info:
                logger.warning(f"Skipping {video.title}: no formats available")
                return

                # check if our selector finds a match
            selector = ydl.build_format_selector(opts['format'])
            chosen = selector(info)

            if not chosen:
                logger.warning(f"Skipping {video.title}: no format matched {opts['format']}")
                return

            # safe to download
            logger.info(f"Downloading {video.title}")
            ydl.download([video.link])