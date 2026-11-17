import pytest

from src.model.video import Video


class TestVideo:
    """Tests for Video class covering title reformatting for hit and non-hit link types."""

    def test_init_with_hit_and_bracketed_title(self):
        """
        Test that a hit link with an already-bracketed title preserves the title as-is.

        Given a title '[Alice]MyVideo' with a hit link, the Video constructor should
        parse from the end but leave the bracketed format unchanged.

        Asserts title, link, and path match the input values.
        """
        title = "[Alice]MyVideo"
        link = "https://ahcdn.hits.com/"
        path = "/videos/PARENT"

        video = Video(title, link, path)

        assert video.title == title
        assert video.link == link
        assert video.path == path

    def test_init_with_hit_without_brackets(self):
        """
        Test that a hit link without brackets reformats hyphen-separated names into brackets.

        Given a title 'Alice-Bob-MyVideo' with a hit link, the Video constructor should
        parse names from the end, converting hyphens to commas and wrapping them in brackets.

        Asserts the title is reformatted to '[Alice, Bob]MyVideo'.
        """
        title = "Alice-Bob-MyVideo"
        link = "https://ahcdn.hits.com/"

        video = Video(title, link)

        assert video.title == "[Alice, Bob]MyVideo"

    def test_init_with_hit_without_brackets_one_name(self):
        """
        Test that a hit link with a single hyphen-separated name reformats correctly.

        Given a title 'Alice-MyVideo' with a hit link, the Video constructor should
        wrap the single name in brackets.

        Asserts the title is reformatted to '[Alice]MyVideo'.
        """
        title = "Alice-MyVideo"
        link = "https://ahcdn.hits.com/"

        video = Video(title, link)

        assert video.title == "[Alice]MyVideo"

    def test_init_non_hit_names(self):
        """
        Test that a non-hit link reformats titles by parsing names from the beginning.

        Given a complex title with category, description, and names from a non-hit link,
        the Video constructor should extract names from the beginning and reformat them.

        Asserts the title is reformatted with bracketed names and cleaned description.
        """
        title = "[CATEGORY] - MOVES FOR THE GUY.+ - Sharon - Sandra Paola"
        link = "https://free.com/videos"

        video = Video(title, link)

        assert video.title ==  "[Sharon, SandraPaola]MOVESFORTHEGUY"

    def test_init_single_array(self):
        """
        Test that a non-hit link with a simple title removes spaces and special characters.

        Given a title "Kay Lovely's Snack" from a non-hit link, the Video constructor
        should remove spaces and special formatting.

        Asserts the title is reformatted to "KayLovely'sSnack".
        """
        title = "Kay Lovely's Snack"
        link = "https://free.com/videos"

        video = Video(title, link)

        assert video.title == "KayLovely'sSnack"