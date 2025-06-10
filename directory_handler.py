import os

class DirectoryHandler:
    @staticmethod
    def create_directory(url):
        name = url.rsplit("/")[-3]
        video_path = name.upper()
        path = "/videos/" + video_path + '/'
        if not os.path.exists(path):
            os.makedirs(path)
        return path