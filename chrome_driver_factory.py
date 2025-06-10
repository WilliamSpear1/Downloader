from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

class ChromeDriver:
    def __init__(self, url):
        self.url = url

    def browser(self):
        options = Options()
        service = Service(ChromeDriverManager().install())

        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=service, options=options)
        driver.get(self.url)
        return driver