import os
import re
import pytest
from pages.heictojpg_page import HeicToJpgPage


class TestHeicCompression:
    """Test suite for heictojpg.com — HEIC to JPG conversion with compression."""

    HEIC_FILE = os.path.join(os.path.dirname(__file__), "..", "test_data", "IMG_5415.HEIC")

    def test_compression_reduces_file_size(self, driver, download_dir):
        """
        Test that heictojpg.com converts a HEIC file to JPG and reduces its size.

        Steps:
        1. Navigate to heictojpg.com
        2. Upload a HEIC file via drag-and-drop onto the drop zone
        3. Wait for conversion to complete (Download button becomes enabled)
        4. Assert on the web page that output size < input size
        5. Click Download
        6. Wait for the file to download
        7. Assert downloaded file has .jpg extension
        8. Assert downloaded file size < original file size on disk

        Preconditions:
        - test_data/IMG_5415.HEIC exists and has not been previously compressed
        """
        if not os.path.exists(self.HEIC_FILE):
            pytest.skip(f"Test HEIC file not found: {self.HEIC_FILE}")

        original_size = os.path.getsize(self.HEIC_FILE)

        page = HeicToJpgPage(driver)
        page.open()
        page.upload(self.HEIC_FILE)
        page.wait_for_conversion()

        input_mb = page.get_input_size_mb()
        output_mb = page.get_output_size_mb()
        reduction_text = page.get_reduction_text()
        print(f"Page stats — Input: {input_mb} MB, Output: {output_mb} MB, Savings: {reduction_text}")

        assert output_mb < input_mb, (
            f"Expected output ({output_mb} MB) to be smaller than input ({input_mb} MB)"
        )

        match = re.search(r"-(\d+)%", reduction_text)
        assert match and int(match.group(1)) > 0, (
            f"Expected reduction percentage like '-25%', got: '{reduction_text}'"
        )

        page.click_download()
        downloaded_file = page.wait_for_download(download_dir)

        assert downloaded_file.lower().endswith(".jpg"), (
            f"Expected a .jpg file, got: {os.path.basename(downloaded_file)}"
        )

        compressed_size = os.path.getsize(downloaded_file)
        print(f"Disk — Original: {original_size:,} bytes, Compressed: {compressed_size:,} bytes, "
              f"Reduction: {(1 - compressed_size / original_size) * 100:.1f}%")

        assert compressed_size < original_size, (
            f"Compressed file ({compressed_size:,} bytes) is not smaller "
            f"than original ({original_size:,} bytes)"
        )
