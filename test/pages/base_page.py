from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    """Base class for all page objects. Provides common methods for interacting with web elements."""

    def __init__(self, driver, timeout=30):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def find(self, locator):
        """Wait for element to be present and return it."""
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        """Wait for element to be clickable and click it."""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def wait_for_visible(self, locator, timeout=60):
        """Wait for element to be visible with custom timeout."""
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
