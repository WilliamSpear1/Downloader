
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from directory_handler import DirectoryHandler
from downloader import Downloader
from video import Video
from chrome_driver_factory import ChromeDriver

def scrap(driver):
    result = []
    video_titles = driver.find_elements(By.CSS_SELECTOR, "div.item-info")

    for i in range(len(video_titles)):
        video = Video()

        try:
            video.setLink(video_titles[i].find_element(By.CSS_SELECTOR, 'a.thumb_title').get_attribute('href'))
            video.setTitle(video_titles[i].find_element(By.CSS_SELECTOR, 'a.thumb_title').get_attribute('title'))
        except NoSuchElementException:
            break

        if video is not None:
            result.append(video)

    return result

def run_browser(url):
    chrome                 = ChromeDriver(url)
    driver                   = chrome.browser()

    path = DirectoryHandler.create_directory(url)

    for i in range(3):
        videos = scrap(driver)
        Downloader.download_videos(videos, path)
        # find and click the next page line
        try:
            next_page_link = driver.find_element(By.CSS_SELECTOR, "li.next a")
            WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.next a")))
            driver.execute_script("arguments[0].click()", next_page_link)
        except NoSuchElementException:
            break
    driver.quit()