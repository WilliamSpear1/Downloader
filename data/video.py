import re
from enum import nonmember
from typing import Optional

from logs.logger_config import setup_logging

logger = setup_logging(__name__)

class Video:
    def __init__(self, title: str = "", link: str = "", path = "") -> None:
        if link and "hit" in link:
            self._title = self.get_videos_title(video_title=title, title_position=-1)
        else:
            self._title = self.get_videos_title(video_title=title, title_position=1)
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

    def get_videos_title(
        self,
        video_title:str,
        title_position:int,
    ) -> str:
        """
           Extracts the name(s) and title from a formatted video string.

           Example:
               Input: 'Alice-Bob-Charlie-MyVideo'
               Output: [Alice, Bob, Charlie]MyVideo
            Vise Vera:
                Input: 'MyVideo-Alice-Bob-Charlie'
                Output: [Charlie, Bob, Alice]MyVideo

           Args:
               video_title: The raw title string (e.g., "Alice-Bob-MyVideo")
               title_position: Index of the title within the split parts

           Returns:
                A formatted string "[Names]Title" or just "Title".
           """
        if title_position == -1 and "[" in video_title:
            logger.info("Video Title are ready formatted.")
            return video_title

        no_space_string = re.sub(r"\s", "", self._clean_title(video_title)) # Remove white space from string
        parts = no_space_string.split('-')

        if 1 >= len(parts) >= title_position: # if there is only one element in title then just return it with no spaces.
            return no_space_string

        title = parts[title_position].strip()

        if title_position != -1:
            names = parts[title_position +1:]
        else:
            names = parts[:title_position]

        names_str = ", ".join(n.strip() for n in names if n.strip())

        if names_str:
            return f"[{names_str}]{title}"

        return title

    def _clean_title(self,url:str) -> str:
        return re.sub(r"[.,+,]", "", url).strip("_")