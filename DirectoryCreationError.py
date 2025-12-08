import sys
import traceback


class DirectoryCreationError(Exception):
    def __init__(self, video_path, error):
        self.video_path = video_path
        self.error = error
        super().__init__(f"Directory Creation Error: {video_path}")