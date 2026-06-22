class DirectoryCreationError(Exception):
    def __init__(self, video_path, error):
        self.video_path = video_path
        self.error_message = str(error)
        super().__init__(f"Directory Creation Error at: {self.video_path} : {self.error_message}")