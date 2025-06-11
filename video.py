import re

class Video:
    def set_link(self, value):
            self._link = value

    def get_link(self):
            return self._link

    def set_title(self, value):
        self._title = self.get_videos_titles(value)

    def get_title(self):
        return self._title

    def get_video_title(self, value):
        reg_str = re.sub(r"\s", "", value)
        text = reg_str.split('-')
        title = text[4].strip()
        names = ",".join(text[1:3]).strip()
        return "[" + names.strip() + "]" + title

    def get_videos_titles(self, value):
        reg_str = re.sub(r"\s", "", value)
        text = reg_str.split('-')
        title = text[1].strip()
        names = ",".join(text[2:]).strip()
        return "[" + names.strip() + "]" + title
