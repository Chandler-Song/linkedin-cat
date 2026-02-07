import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

timeout = 2
# Login & Scroll

def scroll_and_load(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Pause to allow loading

        # Try to click the "Show more results" button if it exists
        try:
            show_more_button = driver.find_element(
                By.XPATH,
                "//button[contains(@class, 'scaffold-finite-scroll__load-button')]",
            )
            if show_more_button:
                show_more_button.click()
                time.sleep(2)  # Give some time for new results to load
        except NoSuchElementException:
            pass  # Continue if no button is found

        # Check if the page height has stopped increasing
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Scroll to the middle of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
    time.sleep(2)
    # Scroll to a random position
    driver.execute_script("window.scrollTo(0, Math.floor(Math.random() * 10000000));")
    time.sleep(2)
    # Scroll back to the top
    driver.execute_script("window.scrollTo(0, 0);")


# Getter setter

def wait_element(driver, by, element, timeout=timeout) -> None:
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, element)))


def get_element(driver, by, element, timeout=timeout):
    return driver.find_element(by, element)


def get_elements(driver, by, element, timeout=timeout):
    return driver.find_elements(by, element)


def get_object(driver, by, element, timeout=timeout):
    wait_element(driver, by, element, timeout)
    return get_element(driver, by, element)


def get_objects(driver, by, element, timeout=timeout):
    wait_element(driver, by, element, timeout)
    return get_elements(driver, by, element)


# Extractor

def extract_element_text(driver, by, element, timeout=timeout):
    try:
        return get_object(driver, by, element, timeout=timeout).text.strip()
    except NoSuchElementException:
        return "Not available"


def extract_many_element_text(driver, by, element, timeout=timeout):
    try:
        items = get_objects(driver, by, element, timeout=timeout)
        temp = []
        for i in items:
            temp.append(i.text.strip())

        return temp
    except NoSuchElementException:
        return "Not available"


def extract_element_attribute(driver, by, element, attribute):
    try:
        return get_object(driver, by, element, timeout=timeout).get_attribute(attribute)
    except NoSuchElementException:
        return "Not available"


def extract_many_element_attribute(driver, by, element, attribute):
    try:
        items = get_objects(driver, by, element, timeout=timeout)
        temp = []
        for i in items:
            temp.append(i.get_attribute(attribute))
        return temp
    except NoSuchElementException:
        return "Not available"


def save_to_json(data, filename="profile.json"):
    """Saves the extracted profile data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


from urllib.parse import unquote
def extract_and_decode_username(url):
    """
    从 LinkedIn 个人资料 URL 中提取用户名并将其解码为汉字。

    参数:
        url (str): LinkedIn 个人资料的 URL。

    返回:
        str: 解码后的用户名。
    """
    # 去除结尾的 "/"
    url = url.rstrip('/')

    # 提取用户名部分
    username_encoded = url.split('/')[-1]

    # 解码为汉字
    username_decoded = unquote(username_encoded)

    return username_decoded


