from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup


def wait_for_element(driver, by, value, timeout=10):
    element_present = EC.presence_of_element_located((by, value))
    WebDriverWait(driver, timeout).until(element_present)


def extract_material_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    rows = soup.select("tr.gcss-tr-ingredient, tr.gcss-tr-add")
    extracted_data = []
    for row in rows:
        try:
            material_link = row.select_one("a")["href"]
            material_name = row.select_one("div.sm\\:mt-1 a").text.strip()
            material_amount = row.select_one("td.p-1:nth-of-type(2)").text.strip()
            extracted_data.append(
                {
                    "material_id": material_link.split("/")[-1],
                    "material_name": material_name,
                    "material_amount": material_amount,
                }
            )
        except Exception as e:
            print(f"Error extracting row: {e}")
    return extracted_data


def main(headless=True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--enable-javascript")
    driver = webdriver.Chrome(options=options)
    driver.get("https://glazy.org/recipes/250893")

    try:
        WebDriverWait(driver, 4).until(
            lambda driver: (
                find_element(driver, By.CLASS_NAME, "rounded-t-lg")
                or find_element(driver, By.ID, "carousel-div-175")
            )
        )
        html_content = driver.page_source
        extracted_data = extract_material_data(html_content)  # Assuming this function is already defined
        print(extracted_data)
    except Exception as e:
        print(f"An exception occurred: {e}")
    finally:
        driver.quit()

def find_element(driver, by, value):
    try:
        elem = driver.find_element(by, value)
        print(f"Found element by {by} = {value}")
        return elem
    except NoSuchElementException:
        print(f"Element not found by {by} = {value}")
        return None



if __name__ == "__main__":
    main()
