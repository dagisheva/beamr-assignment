import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture
def download_dir(tmp_path):
    dl_dir = str(tmp_path / "downloads")
    os.makedirs(dl_dir, exist_ok=True)
    return dl_dir


@pytest.fixture
def driver(download_dir):
    """Set up Chrome WebDriver with download directory and optional headless mode."""
    options = webdriver.ChromeOptions()

    if os.environ.get("HEADLESS", "").lower() in ("1", "true", "yes"):
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    }
    options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()

    yield driver

    driver.quit()
