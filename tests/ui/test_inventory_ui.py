import pytest

from tests.ui.pages.inventory_page import InventoryPage


@pytest.mark.ui
def test_user_can_add_an_active_inventory_item(browser_driver, live_server):
    page = InventoryPage(browser_driver, live_server).open()

    page.add_item("Selenium Grid Node", 3)

    assert any(
        "selenium grid node" in text.lower() and "active" in text.lower()
        for text in page.row_texts()
    )


@pytest.mark.ui
def test_user_can_add_a_discontinued_item(browser_driver, live_server):
    page = InventoryPage(browser_driver, live_server).open()

    page.add_item("Legacy Test Appliance", 0, status="discontinued")

    assert any(
        "legacy test appliance" in text.lower() and "discontinued" in text.lower()
        for text in page.row_texts()
    )
