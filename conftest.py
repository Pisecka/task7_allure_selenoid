import pytest
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


DRIVERS = os.path.expanduser("~/Documents/drivers")


def driver_factory(browser):
    if browser == "chrome":
        service = Service(executable_path=os.path.join(DRIVERS, "chromedriver"))
        driver = webdriver.Chrome(service=service)
    elif browser == "firefox":
        service = Service(executable_path=os.path.join(DRIVERS, "geckodriver"))
        driver = webdriver.Firefox(service=service)
    elif browser == "opera":
        driver = webdriver.Opera(executable_path=os.path.join(DRIVERS, "operadriver"))
    elif browser == "edge":
        service = Service(executable_path=os.path.join(DRIVERS, "msedgedriver"))
        driver = webdriver.Edge(service=service)
    else:
        raise Exception("Driver not supported")
    return driver


def pytest_addoption(parser):
    parser.addoption("--browser", default="chrome")
    parser.addoption("--b_version", default="98.0")
    parser.addoption("--url", default="https://demo.opencart.com/")
    parser.addoption("--executor", action="store", default="localhost")


@pytest.fixture(scope="session", autouse=True)
def get_environment(pytestconfig):
    props = {
        'Browser': 'Chrome',
        'Browser.Version': '98.0',
        'Shell': os.getenv('SHELL')
    }

    tests_root = pytestconfig.rootdir
    with open(f'{tests_root}/allure-results/environment.properties', 'w') as f:
        env_props = '\n'.join([f'{k}={v}' for k, v in props.items()])
        f.write(env_props)


@pytest.fixture
def browser(request):
    browser = request.config.getoption("--browser")
    b_version = request.config.getoption("--b_version")
    executor = request.config.getoption("--executor")
    url = request.config.getoption("--url")

    if executor == "local":
        driver = driver_factory(browser)
    else:
        executor_url = f"http://{executor}:4444/wd/hub"
        caps = {
            "browserName": browser,
            "browserVersion": b_version,
            "screenResolution": "1280x720",
            "name": "Karina",
            "selenoid:options": {
                "enableVNC": True,
                "enableVideo": False,
            #     "enableLog": logs
            },
            # 'acceptSslCerts': True,
            # 'acceptInsecureCerts': True,
            # 'timeZone': 'Europe/Moscow',
            'goog:chromeOptions': {}
        }

        driver = webdriver.Remote(
            command_executor=executor_url,
            desired_capabilities=caps
        )

    # set base_url as attribute
    driver.url = url

    # set time - 5 sec
    driver.t = 5

    driver.maximize_window()
    driver.get(url)
    request.addfinalizer(driver.quit)
    return driver