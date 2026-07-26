from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import Select, WebDriverWait


class InventoryPage:
    NAME = (By.ID, "name")
    QUANTITY = (By.ID, "quantity")
    STATUS = (By.ID, "status")
    ADD_ITEM = (By.CSS_SELECTOR, "button[type='submit']")
    ALERT = (By.CSS_SELECTOR, "[role='alert']")
    ROWS = (By.CSS_SELECTOR, "[data-testid='inventory-row']")
    EMPTY_STATE = (By.CSS_SELECTOR, "[data-testid='empty-state']")

    def __init__(self, driver, base_url: str):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 8)

    def open(self):
        self.driver.get(self.base_url)
        self.wait.until(conditions.visibility_of_element_located(self.NAME))
        return self

    def add_item(self, name: str, quantity: int, status: str = "active"):
        self.driver.find_element(*self.NAME).send_keys(name)
        self.driver.find_element(*self.QUANTITY).send_keys(str(quantity))
        Select(self.driver.find_element(*self.STATUS)).select_by_value(status)
        self.driver.find_element(*self.ADD_ITEM).click()
        self.wait.until(conditions.text_to_be_present_in_element(self.ALERT, "added"))

    def row_texts(self) -> list[str]:
        return [row.text for row in self.driver.find_elements(*self.ROWS)]

