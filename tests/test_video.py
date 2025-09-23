import pytest

from data.video import Video


class TestVideo:
    def test_init_with_hit_and_bracketed_title(self):
        title = "[Alice]MyVideo"
        link = "https://ahcdn.hits.com/"
        path = "/videos/PARENT"

        video = Video(title, link, path)

        assert video.title == title
        assert video.link == link
        assert video.path == path

    def test_init_with_hit_without_brackets(self):
        title = "Alice-Bob-MyVideo"
        link = "https://ahcdn.hits.com/"

        video = Video(title, link)

        assert video.title == "[Alice, Bob]MyVideo"

    def test_init_with_hit_without_brackets_one_name(self):
        title = "Alice-MyVideo"
        link = "https://ahcdn.hits.com/"

        video = Video(title, link)

        assert video.title == "[Alice]MyVideo"

    def test_init_non_hit_names(self):
        title = "[CATEGORY] - MOVES FOR THE GUY.+ - Sharon - Sandra Paola"
        link = "https://free.com/videos"

        video = Video(title, link)

        assert video.title ==  "[Sharon, SandraPaola]MOVESFORTHEGUY"

    def test_init_single_array(self):
        title = "Kay Lovely's Creamy Snatch"
        link = "https://free.com/videos"

        video = Video(title, link)

        assert video.title == "KayLovely'sCreamySnatch"
