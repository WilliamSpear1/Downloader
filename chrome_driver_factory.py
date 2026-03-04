import logging

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

from conf.logger_config import setup_logging

logger = logging.getLogger(__name__)

class ChromeDriver:
    def __init__(self, url:str) -> None:
        self.url = url
        self.driver = self.browser()

    def get_driver(self) -> WebDriver:
        return self.driver

    def browser(self) -> WebDriver:
        options = Options()

        options.add_argument("--headless=new")  # modern headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")  # prevent /dev/shm size issues
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-quic") # Disable QUIC(UDP) to force standard TCP which the proxy can handle
        options.add_argument("--proxy-bypass-list=<-loopback>")  # Bypass proxy for localhost
        options.add_argument('--disable-http2')  # Disable HTTP/2 to prevent issues with Selenium Wire's MITM proxy
        options.add_argument('--disable-software-rasterizer')  # Disable software rasterizer to prevent GPU-related issues in headless mode
        options.add_argument('--mute-audio')  # Mute audio to prevent potential issues with audio processing in headless mode

        service = Service(log_path="/app/logs/chromedriver.log", service_args=["--verbose"])
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