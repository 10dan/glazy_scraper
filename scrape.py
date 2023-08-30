from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sqlite3

def wait_for_element(driver, by, value, timeout=10):
    element_present = EC.presence_of_element_located((by, value))
    WebDriverWait(driver, timeout).until(element_present)


def extract_material_data(html_content, recipe_id):
    soup = BeautifulSoup(html_content, "html.parser")
    rows = soup.select("tr.gcss-tr-ingredient, tr.gcss-tr-add")

    # Extract title
    title_element = soup.select_one(
        ".text-2xl.font-bold.leading-7.sm\\:text-3xl.mr-2.mb-1.inline-flex span.break-all"
    )
    title_content = title_element.text.strip() if title_element else "N/A"

    # Extract cone information
    cone_element = soup.select_one(".text-3xl.font-base.leading-7.mt-1.mb-2")
    cone_info = cone_element.text.strip() if cone_element else "N/A"
    cone_info = cone_info.replace("△", "").strip()

    # Extract images
    image_list = []

    # Handle carousel images
    carousel_images = soup.select(".keen-slider__slide")
    if carousel_images:
        for img in carousel_images:
            img_src = img.get("src", "N/A")
            image_list.append(img_src)
    else:
        # Handle lone image
        lone_image = soup.select_one(".rounded-t-lg")
        if lone_image:
            img_src = lone_image.get("src", "N/A")
            image_list.append(img_src)

    extracted_data = {
        "recipe_id": recipe_id,
        "title": title_content,
        "cone": cone_info,
        "images": image_list,
        "materials": [],
    }
    for row in rows:
        try:
            material_link = row.select_one("a")["href"]
            material_name = row.select_one("div.sm\\:mt-1 a").text.strip()
            material_amount = row.select_one("td.p-1:nth-of-type(2)").text.strip()
            extracted_data["materials"].append(
                {
                    "name": material_name,
                    "amt": material_amount,
                    "id": material_link.split("/")[-1],
                }
            )
        except Exception as e:
            print(f"Error extracting row: {e}")
    return extracted_data


def scrape_page(recipe_id):
    print(f"scraping recipe: {recipe_id}")
    url = f"https://glazy.org/recipes/{recipe_id}"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--enable-javascript")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 3).until(
            lambda driver: (
                find_ele(driver, By.CLASS_NAME, "rounded-t-lg")
                or find_ele(driver, By.CSS_SELECTOR, "[id^='carousel-div-']")
            )
        )
        html_content = driver.page_source
        extracted_data = extract_material_data(html_content, recipe_id)
        store_data(extracted_data)
        print("recipe saved!")
    except Exception as e:
        print(f"No image found. {e}")
    finally:
        driver.quit()


def find_ele(driver, by, value):
    try:
        elem = driver.find_element(by, value)
        return elem
    except NoSuchElementException:
        return None
    
def store_data(extracted_data):
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute("INSERT INTO recipes (recipe_id, title, cone, images, materials) VALUES (?, ?, ?, ?, ?)",
              (extracted_data['recipe_id'],
               extracted_data['title'],
               extracted_data['cone'],
               str(extracted_data['images']),
               str(extracted_data['materials'])))
    conn.commit()
    conn.close()

def create_table():
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS recipes
                (recipe_id INTEGER PRIMARY KEY,
                title TEXT,
                cone TEXT,
                images TEXT,
                materials TEXT)''')
    conn.commit()
create_table()

def fetch_all_data():
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('SELECT * FROM recipes')
    all_rows = c.fetchall()
    for row in all_rows:
        print(row)
    conn.close()

# Loop through recipe IDs
for recipe_id in range(2000, 257931):
    scrape_page(recipe_id)
