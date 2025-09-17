from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from logs.logger_config import setup_logging
from data.video import Video

logger = setup_logging(__name__)

class Scarper:
    def __init__(self, url: str, number_of__pages: int, parent_directory: str=""):
        self.url = url
        self.number_of_pages = number_of__pages
        self.parent_directory = parent_directory

    @staticmethod
    def scrape_multiple_videos(driver: WebDriver, path:str) -> list:
        """Extract Video Elements (title + link) from current page."""
        videos = []
        video_elements = driver.find_elements(By.CSS_SELECTOR, "div.item-info")

        for element in video_elements:
            try:
                video = Video(
                    link=element.find_element(By.CSS_SELECTOR, 'a.thumb_title').get_attribute('href'),
                    title= element.find_element(By.CSS_SELECTOR, 'a.thumb_title').get_attribute('title'),
                )
                video.path = path
                videos.append(video)
            except NoSuchElementException as e:
                logger.warning(f"No Such Element Exception Has Occurred: {e}")
                continue

        logger.info(f"Found {len(videos)} videos on the page.")
        return videos