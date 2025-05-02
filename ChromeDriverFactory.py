from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

class ChromeDriver:
    def __init__(self, url):
        self.url = url

    def browser(self):
        options = Options()
        #service = Service(executable_path="/opt/chromedriver/chromedriver-linux64/chromedriver")
        service = Service(executable_path="/usr/bin/chromedriver")

        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(service=service, options=options)
        driver.get(self.url)
        return driver