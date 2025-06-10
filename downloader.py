from yt_dlp import YoutubeDL

class Downloader:
    ydl_opts = {
        'ignoreerrors': True,
        'abort_on_unavailable_fragments': True,
        'quiet': True,
        'nooverwrites': True,
        'format': 'bestvideo[height<=720][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    }

    @staticmethod
    def download_videos(self, videos, path):
        for i in range(len(videos)):
            self.ydl_opts['outtmpl'] = path + videos[i].getTitle() + ".%(ext)s"
            with YoutubeDL(self.ydl_opts) as ydl:
                ydl.download(videos[i].getLink())

    @staticmethod
    def download_video(self, video, path):
            self.ydl_opts['outtmpl'] = path + video.getTitle() + ".%(ext)s"
            with YoutubeDL(self.ydl_opts) as ydl:
                ydl.download(video.getLink())