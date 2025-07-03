import logging

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from directory_handler import DirectoryHandler
from downloader import Downloader
from video import Video
from chrome_driver_factory import ChromeDriver

logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)

def scarp_multiple_videos(driver):
    result = []
    video_titles = driver.find_elements(By.CSS_SELECTOR, "div.item-info")

    for i in range(len(video_titles)):
        video = Video()

        try:
            video.set_link(video_titles[i].find_element(By.CSS_SELECTOR, 'a.thumb_title').get_attribute('href'))
            video.set_title(video_titles[i].find_element(By.CSS_SELECTOR, 'a.thumb_title').get_attribute('title'))
        except NoSuchElementException:
            break

        if video is not None:
            result.append(video)

    return result

def scarp_single_video(driver, url):
    video = Video()

    try:
        video.set_link(url)
        #TODO: Find way to get the title from the video page.
        video.set_title(driver.find_element(By.CSS_SELECTOR, 'div.headline h1').get_('title'))
    except NoSuchElementException:
        return None

    return video

def run_browser(url):
    chrome = ChromeDriver(url)
    driver   = chrome.browser()
    downloader = Downloader()

    logging.info("Creating directory for downloads.")

    path = DirectoryHandler.create_directory(url)
    #TODO: Find a way to to indicate if downloading multiple videos or a single video.
    logging.info("Going to download Videos")
    for i in range(5):
        logging.info("Starting page %d", i + 1)
        videos = scarp_multiple_videos(driver)
        downloader.download_videos(videos, path)
        # find and click the next page line
        try:
            next_page_link = driver.find_element(By.CSS_SELECTOR, "li.next a")
            WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.next a")))
            driver.execute_script("arguments[0].click()", next_page_link)
        except NoSuchElementException:
            break

    logging.info("Finished downloading videos.")

    driver.quit()