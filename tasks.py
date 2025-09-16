from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from celery_app import celery_app
from directory_handler import DirectoryHandler
from downloader import Downloader
from chrome_driver_factory import ChromeDriver
from selenium.common import NoSuchElementException

from selenium.webdriver.common.by import By
from logs.logger_config import setup_logging
from scarper import Scarper

logger = setup_logging(__name__)

@celery_app.task(name="tasks.run_browser")
def run_browser(url:str, number_of_pages:int, parent_directory:str="") -> None:
    """Run the chrome driver, scrape videos across multiple pages, and download them."""
    chrome = ChromeDriver(url)
    driver = chrome.get_driver()
    downloader = Downloader()
    directory_handler = DirectoryHandler()
    scarper = Scarper(url, number_of_pages, parent_directory)

    logger.info(f"Starting scrape -> {url}, Parent Dir: {parent_directory}")

    path = directory_handler.create_directory_url(url=url, parent_directory=parent_directory)

    try:
        for page in range(1, number_of_pages + 1):
            logger.info(f"Processing page {page}/{number_of_pages}")

            videos = scarper.scrape_multiple_videos(driver, path)

            if videos:
                downloader.download_videos(videos)
            else:
                logger.warning("No videos found on this page.")

            # find and click the next page if it exists
            try:
                next_page_link = driver.find_element(By.CSS_SELECTOR, "li.next a")
                WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li.next a")))
                driver.execute_script("arguments[0].click()", next_page_link)
            except NoSuchElementException as e:
                logger.error(f"No Such Element Exception Has Occurred: {e}")
                break
    except Exception as e:
        logger.error(f"Unexpected error during scraping: {e}", exc_info=True)
    finally:
        chrome.close_browser()
        logger.info("Scarping session finished. Browser closed.")
