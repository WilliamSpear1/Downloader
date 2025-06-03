import os

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from yt_dlp import YoutubeDL
from Video import Video
from ChromeDriverFactory import ChromeDriver

def create_directory(url):
    name = url.rsplit("/")[-3]
    video_path  = name.upper()
    path = "/videos/" + video_path + '/'
    if not os.path.exists(path):
        os.makedirs(path)
    return path

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

def download(videos, ydl_opts, path):
    for i in range(len(videos)):
        ydl_opts['outtmpl'] = path + videos[i].getTitle() + ".%(ext)s"
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(videos[i].getLink())

def run_browser(url):
    chrome = ChromeDriver(url)
    driver = chrome.browser()
    path = create_directory(url)

    for i in range(3):
        videos = scrap(driver)
        download(videos, ydl_opts, path)
        # find and click the next page line
        try:
            next_page_link = driver.find_element(By.CSS_SELECTOR, "li.next a")
            WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.next a")))
            driver.execute_script("arguments[0].click()", next_page_link)
        except NoSuchElementException:
            break
    driver.quit()

# 'outtmpl': path + '\\Channels\%(uploader)s\%(title)s ## %(uploader)s ## %(id)s.%(ext)s'
ydl_opts = {
    'ignoreerrors': True,
    'abort_on_unavailable_fragments': True,
    'quiet': True,
    'nooverwrites': True,
    'format': 'bestvideo[height<=720][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best'
}