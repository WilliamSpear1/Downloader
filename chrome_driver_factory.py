from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

from logs.logger_config import setup_logging

logger = setup_logging(__name__)

class ChromeDriver:
    def __init__(self, url:str) -> None:
        self.url = url
        self.driver = self.browser()

    def get_driver(self) -> WebDriver:
        return self.driver

    def browser(self) -> WebDriver:
        options = Options()
        service = Service(ChromeDriverManager().install())

        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=service, options=options)
        driver.get(self.url)
        return driver

    def close_browser(self) -> None:
        if self.driver:
            self.driver.quit()
            logger.info("Downloaded URL: %s", self.url)
            logger.info("Browser closed successfully.")
        else:
            logger.info("No browser instance to close.")