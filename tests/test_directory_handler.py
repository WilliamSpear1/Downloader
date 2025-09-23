from unittest.mock import patch

import pytest

from directory_handler import DirectoryHandler

@pytest.fixture
def handler():
    return DirectoryHandler()

@patch("directory_handler.Path.mkdir")
def test_safe_dir_name_basic(mock_mkdir, handler):
    assert handler.safe_dir_name("abc/def") == "abc_def"
    assert handler.safe_dir_name("abc def") == "abc_def"
    assert handler.safe_dir_name("abc-def") == "abc-def"
    assert handler.safe_dir_name("!@#") == "default"

@patch("directory_handler.Path.mkdir")
def test_create_directory_url_hits_category(mock_mkdir, handler):
    url = "https://www.hits.com/videos.php?p=1&s=l&spon=category-hits"
    Parent = "Parent"
    result = handler.create_directory_url(url=url, parent_directory=Parent)
    assert "VIDEOS" in result.upper()
    assert "PARENT" in result.upper()
    assert "CATEGORY-HITS" in result.upper()
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

@patch("directory_handler.Path.mkdir")
def test_create_directory_url_hits_name(mock_mkdir, handler):
    url = "https://www.hits.com/videos.php?p=1&s=l&ps=name"
    Parent = None
    result = handler.create_directory_url(url=url, parent_directory=Parent)
    assert "VIDEOS" in result.upper()
    assert "NAME" in result.upper()
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

@patch("directory_handler.Path.mkdir")
def test_create_directory_hits_name(mock_mkdir, handler):
    url = "https://www.pornhits.com/video/525405/video-title/"
    Parent = "Parent"
    result = handler.create_directory(parent_directory=Parent)
    assert "VIDEOS" in result.upper()
    assert "PARENT" in result.upper()
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

def test_create_directory_url_invalid(handler):
    url = "https://exmaple.com/"
    with pytest.raises(ValueError):
        handler.create_directory_url(url)