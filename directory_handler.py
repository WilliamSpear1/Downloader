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

    @staticmethod
    def check_directory(url):
        #TODO: Implement a method to check if the directory exists.
        # Along with grabbing the name of the video and dropping after everything before the
        # first backslash.
        name = url.rsplit("/")[-3]
        video_path = name.upper()
        path = "/videos/" + video_path + '/'
        if not os.path.exists(path):
            os.makedirs(path)
        return path
