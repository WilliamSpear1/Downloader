from yt_dlp import YoutubeDL

class Downloader:
    ydl_opts = {
        'ignoreerrors': True,
        'abort_on_unavailable_fragments': True,
        'quiet': True,
        'nooverwrites': True,
        'ratelimit': 500000,  # 5 MB/s
        'format': 'bestvideo[height<=720][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    }

    def download_videos(self, videos, path) -> None:
        for i in range(len(videos)):
            self.ydl_opts['outtmpl'] = path + videos[i].get_title() + ".%(ext)s"
            with YoutubeDL(self.ydl_opts) as ydl:
                ydl.download(videos[i].get_link())

    def download_video(self, video, path) -> None:
            self.ydl_opts['outtmpl'] = path + video.get_title() + ".%(ext)s"
            with YoutubeDL(self.ydl_opts) as ydl:
                ydl.download(video.get_link())