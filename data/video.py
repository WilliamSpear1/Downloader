import re
from typing import Optional

from logs.logger_config import setup_logging

logger = setup_logging(__name__)

class Video:
    def __init__(self, title: str = "", link: str = "", path = "") -> None:
        if "hit" in link:
            if "[" in title:
                self._title = title
            else:
                self._title = self.get_videos_title(video_title=title, title_position=0, name_position=1)
        else:
            self._title = self.get_videos_title(video_title=title, title_position=1, name_position=2)
        self._link = link
        self._path = path

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, link):
        self._link = link

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @staticmethod
    def get_videos_title(
        video_title:str,
        title_position:int,
        name_position:int,
        other_name_position: Optional[int] = None
    ) -> str:
        """
        Extracts the name and title from a formatted video string.

        Example:
            Input: 'Alice-Bob-Charlie-MyVideo'
            Output: [Bob, Charlie]MyVideo

        Args:
            video_title:  String that is the title of the video
            title_position: position of title in of video
            name_position: position of name in video
            other_name_position: in case there is more than one name associated with the video.

        Returns:
             A formatted string [Names]Title.
        """
        logger.info(f"Video Title: {video_title}")

        no_space_string = re.sub(r"\s", "", video_title) # Remove white space from string
        logger.info(f"No Space String: {no_space_string}")
        parts = no_space_string.split('-')
        logger.info(f"Parts: {parts}")
        title = parts[title_position].strip()
        logger.info(f"Title: {title}")
        names = ",".join(parts[name_position:other_name_position]).strip()
        logger.info(f"Names: {names}")

        if names:
            video_title = f"[{names}]{title}"
        else:
            video_title = f"{title}"

        return video_title
