import os
import time
import glob
import base64
import zipfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage


class HeicToJpgPage(BasePage):
    """Page Object for heictojpg.com — HEIC to JPG conversion with compression."""

    URL = "https://heictojpg.com/"

    # Upload
    DROP_ZONE = (By.CSS_SELECTOR, "label[class*='dropzone-border']")

    # Stats panel (populated after conversion)
    STATS_IN_SIZE = (By.ID, "stats-in-size")    # e.g. "1.6"
    STATS_OUT_SIZE = (By.ID, "stats-out-size")  # e.g. "1.1"
    STATS_SAVINGS = (By.ID, "stats-savings")    # e.g. "-16%"

    # Download button loses opacity-20 class when conversion is complete
    DOWNLOAD_BUTTON_ENABLED = (
        By.XPATH,
        "//button[@id='download-all-button' and not(contains(@class,'opacity-20'))]"
    )

    def open(self):
        self.driver.get(self.URL)
        return self

    def upload(self, file_path):
        """Simulate drag-and-drop of a HEIC file onto the drop zone.

        Selenium's ActionChains cannot drag files from the OS filesystem into
        the browser. Instead, we read the file in Python, encode it as base64,
        and reconstruct a File object in JavaScript — then dispatch dragenter,
        dragover, and drop events on the drop zone. This exercises the same
        event handlers as a real user drag-and-drop.
        """
        absolute_path = os.path.abspath(file_path)
        filename = os.path.basename(file_path)

        with open(absolute_path, "rb") as f:
            file_b64 = base64.b64encode(f.read()).decode("utf-8")

        drop_zone = self.wait_for_visible(self.DROP_ZONE)

        self.driver.execute_script("""
            var b64 = arguments[0], name = arguments[1], target = arguments[2];
            var bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
            var file = new File([bytes], name, {type: 'image/heic'});
            var dt = new DataTransfer();
            dt.items.add(file);
            ['dragenter', 'dragover', 'drop'].forEach(function(evtName) {
                target.dispatchEvent(new DragEvent(evtName, {
                    bubbles: true, cancelable: true, dataTransfer: dt
                }));
            });
        """, file_b64, filename, drop_zone)
        return self

    def wait_for_conversion(self, timeout=120):
        """Wait until conversion is complete: download button becomes enabled."""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.DOWNLOAD_BUTTON_ENABLED),
            message=f"Conversion did not complete within {timeout}s"
        )
        return self

    def get_reduction_text(self):
        """Return the savings percentage text shown on the page (e.g. '-16%').

        The savings element is in the DOM from page load but hidden (CSS
        'invisible'). We wait for it to become visible before reading its text.
        """
        return self.wait_for_visible(self.STATS_SAVINGS).text

    def get_input_size_mb(self):
        """Return the input file size in MB as shown on the page (float)."""
        return float(self.wait_for_visible(self.STATS_IN_SIZE).text)

    def get_output_size_mb(self):
        """Return the output file size in MB as shown on the page (float)."""
        return float(self.wait_for_visible(self.STATS_OUT_SIZE).text)

    def click_download(self):
        self.click(self.DOWNLOAD_BUTTON_ENABLED)
        return self

    def wait_for_download(self, download_dir, timeout=60):
        """Wait for the zip archive to download, extract it, and return the .jpg path."""
        end_time = time.time() + timeout
        while time.time() < end_time:
            completed = glob.glob(os.path.join(download_dir, "*.zip"))
            if completed:
                zip_path = max(completed, key=os.path.getmtime)
                # Guard against reading a partially written file:
                # compare size before and after a short pause — if still
                # growing, loop back and wait for the next iteration.
                size_before = os.path.getsize(zip_path)
                time.sleep(0.5)
                if os.path.getsize(zip_path) != size_before:
                    continue
                return self._extract_jpg(zip_path, download_dir)
            time.sleep(1)
        raise TimeoutError(f"No completed zip download in {download_dir} after {timeout}s")

    def _extract_jpg(self, zip_path, extract_dir):
        """Extract the zip and return the path to the first .jpg file inside."""
        with zipfile.ZipFile(zip_path, "r") as zf:
            jpg_names = [n for n in zf.namelist() if n.lower().endswith(".jpg")]
            if not jpg_names:
                raise FileNotFoundError(f"No .jpg files found inside {zip_path}")
            zf.extractall(extract_dir)
        return os.path.join(extract_dir, jpg_names[0])
