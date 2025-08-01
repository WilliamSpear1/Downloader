from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from Downloader.directory_handler import DirectoryHandler
from Downloader.downloader import Downloader
from Downloader.logs.logger_config import setup_logging
from Downloader.data.video import Video
from Downloader.chrome_driver_factory import ChromeDriver

logger = setup_logging(__name__)

class Scarper:
    def __init__(self, url, number_of__pages, parent_directory=""):
        self.url = url
        self.number_of_pages = number_of__pages
        self.parent_directory = parent_directory

    def scarp_multiple_videos(self, driver) -> list:
        result = []
        video_titles = driver.find_elements(By.CSS_SELECTOR, "div.item-info")

        for i in range(len(video_titles)):
            video = Video()

            try:
                video.set_link(video_titles[i].find_element(By.CSS_SELECTOR, 'a.thumb_title').get_attribute('href'))
                video.set_title(video_titles[i].find_element(By.CSS_SELECTOR, 'a.thumb_title').get_attribute('title'))
            except NoSuchElementException as e:
                logger.error(f"No Such Element Exception Has Occurred: {e}")
                break

            if video is not None:
                result.append(video)

        return result

    def run_browser(self) -> None:
        chrome = ChromeDriver(self.url)
        driver = chrome.get_driver()
        downloader = Downloader()

        logger.info(f"Url in Scarper: {self.url}")
        logger.info(f"Parent Directory in Scarper: {self.parent_directory}")

        path = DirectoryHandler.create_directory(self.url, self.parent_directory)

        for i in range(self.number_of_pages):
            logger.info("Starting page %d", i + 1)
            videos = self.scarp_multiple_videos(driver)
            downloader.download_videos(videos, path)
            # find and click the next page line
            try:
                next_page_link = driver.find_element(By.CSS_SELECTOR, "li.next a")
                WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.next a")))
                driver.execute_script("arguments[0].click()", next_page_link)
            except NoSuchElementException as e:
                logger.error(f"No Such Element Exception Has Occurred: {e}")
                break

        logger.info("Finished downloading videos.")

        chrome.close_browser()