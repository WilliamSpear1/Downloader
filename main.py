import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from yt_dlp import YoutubeDL

# Variables
url = sys.argv[1]
name_of_directory = sys.argv[2]
options = Options()
service = Service(executable_path="/opt/chromedriver/chromedriver-linux64/chromedriver")

options.add_argument("--headless")
options.add_argument("--no-sandbox")

#options.add_argument(r"--user-data-dir=/home/wilabeast/.config/google-chrome")

driver = webdriver.Chrome(service=service, options=options)

driver.get(url) # starting url
video_titles = driver.find_elements(By.CSS_SELECTOR, 'div[id="thumbnail"')

path = "/home/wilabeast/Videos/Youtube/" + name_of_directory +'/'
if not os.path.exists(path):
    os.makedirs(path)

#'outtmpl': path + '\\Channels\%(uploader)s\%(title)s ## %(uploader)s ## %(id)s.%(ext)s'
ydl_opts = {
    'username': 'spearmanwm@gmail.com',
    'password': 'ADj74EBL3sH9tN6',
    'ignoreerrors': True,
    'abort_on_unavailable_fragments': True,
    'rejectitle': True,
    'cookiefile': '/home/wilabeast/Downloads/cookies.txt',
    'format': 'bestvideo[height<=720][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': path + '%(title)s.%(ext)s',
    'quiet': True
}

vurls =[]

for i in range(len(video_titles)):
    vurls.append(video_titles[i].find_element(By.CSS_SELECTOR, 'a#thumbnail').get_attribute('href'))

with YoutubeDL(ydl_opts) as ydl:
    ydl.download(vurls)

driver.quit()
