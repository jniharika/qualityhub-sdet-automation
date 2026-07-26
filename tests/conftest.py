from __future__ import annotations

import os
import threading
from pathlib import Path

import pytest
from werkzeug.serving import make_server

from app import create_app


@pytest.fixture()
def app(tmp_path: Path):
    database = tmp_path / "test-qualityhub.db"
    application = create_app(
        {
            "TESTING": True,
            "DATABASE": str(database),
            "SECRET_KEY": "test-secret",
        }
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def live_server(app):
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    thread.join(timeout=5)


@pytest.fixture(scope="session")
def browser_driver():
    selenium = pytest.importorskip("selenium")
    from selenium import webdriver
    from selenium.common.exceptions import WebDriverException
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions

    browser_name = os.getenv("BROWSER", "chrome").lower()
    driver = None
    for attempt in range(2):
        try:
            if browser_name == "firefox":
                options = FirefoxOptions()
                options.add_argument("-headless")
                driver = webdriver.Firefox(options=options)
            else:
                options = ChromeOptions()
                options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--window-size=1440,1000")
                driver = webdriver.Chrome(options=options)
            break
        except WebDriverException:
            if attempt == 1:
                raise

    driver.set_page_load_timeout(15)
    yield driver
    driver.quit()
