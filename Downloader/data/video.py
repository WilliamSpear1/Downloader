import re

class Video:
    def __init__(self, title="", link="") -> None:
        self._title = title
        self._link = link

    def set_link(self, link) -> None:
            self._link = link

    def get_link(self) -> str:
            return self._link

    def set_title(self, video_title) -> None:
        self._title = self.get_videos_titles(video_title)

    def get_title(self) -> str:
        return self._title

    def get_video_title(self, value) -> str:
        reg_str = re.sub(r"\s", "", value)
        text = reg_str.split('-')
        title = text[4].strip()
        names = ",".join(text[1:3]).strip()
        return "[" + names.strip() + "]" + title

    def get_videos_titles(self, value) -> str:
        reg_str = re.sub(r"\s", "", value)
        text = reg_str.split('-')
        title = text[1].strip()
        names = ",".join(text[2:]).strip()
        return "[" + names.strip() + "]" + title