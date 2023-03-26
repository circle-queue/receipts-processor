from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
import pandas as pd
import receipts.urls as urls
import dotenv
from pathlib import Path
import os

driver = webdriver.Chrome()

ENV_FILE = Path.home() / ".env"
try:
    dotenv.load_dotenv(ENV_FILE)
    username = os.environ["RECEIPTS_SECRET_USERNAME"]
    password = os.environ["RECEIPTS_SECRET_PASSWORD"]
except Exception as error:
    raise FileNotFoundError(
        f"Please update a .env file with credentials at {ENV_FILE}"
    ) from error

# scrapy.Request(urls.LOGIN_URL, callback=)
formdata = {
    "UserName": username,
    "Password": password,
}


def read_table(element: WebElement):
    html = element.get_attribute("outerHTML")
    dfs = pd.read_html(html)
    assert len(dfs) == 1
    return dfs[0]


def keep_trying(func: callable, timeout=5):
    for i in range(timeout):
        try:
            return func()
        except:
            driver.implicitly_wait(i / 2)
    return func()


def find(by, value, e: WebElement = driver):
    def find_one(by, value):
        item, *rest = e.find_elements(by, value)
        assert not rest
        return item

    return keep_trying(lambda: find_one(by, value))


def get_next_button_if_visible():
    next_button = find("class name", "next", e=find("class name", "receipts-list"))
    return next_button if "visible" in next_button.get_attribute("class") else None


def setup():
    driver.get(urls.LOGIN_URL)
    find("id", "UserName").send_keys(username)
    find("id", "password-field").send_keys(password)
    find("class name", "button--standard").click()
    driver.get(urls.RECEIPT_URL)
    driver.get(urls.RECEIPT_URL)

    driver.implicitly_wait(1)

    try:
        find("id", "declineButton").click()
    except:
        pass


def main():
    setup()

    dfs = []
    while True:
        all_receipt = driver.find_elements("class name", "receipt")
        for i, receipt in enumerate(all_receipt):
            keep_trying(receipt.click)
            driver.find_elements("id", "newReceiptView")
            try:
                receipt_view = find("id", "newReceiptView")
                df = read_table(find("class name", "receipt-table", e=receipt_view))
            except:
                df = read_table(find("class name", "table-borderless"))
            dfs.append(df)
            find("class name", "fancybox-close").click()
        button = get_next_button_if_visible()
        if button is None:
            break

        keep_trying(button.click)

    pd.concat(dfs).set_axis(["a", "b"], axis=1).to_parquet("data.parquet")
