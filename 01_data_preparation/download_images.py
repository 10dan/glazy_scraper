import sqlite3
import requests
import json
import os

def fetch_data_from_db():
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('SELECT * FROM normalized_recipes where recipe_id > 242600')
    all_rows = c.fetchall()
    conn.close()
    return all_rows

def create_directory(name):
    if not os.path.exists(name):
        os.mkdir(name)
    # otherwise delete any existing json files (.json)
    else:
        for file in os.listdir(name):
            if file.endswith(".json"):
                os.remove(os.path.join(name, file))


def download_images(recipe_dir, image_urls, recipe_id):
    for i, url in enumerate(image_urls):
        response = requests.get(url)
        if response.status_code == 200:
            with open(f"{recipe_dir}/{recipe_id}_{i}.jpg", 'wb') as f:
                f.write(response.content)
            print(f"saved image from recipe {recipe_id}, image {i}")

def save_recipe_as_json(recipe_dir, materials):
    with open(f"{recipe_dir}/recipe.json", 'w') as f:
        json.dump(materials, f, indent=4)

def main():
    all_rows = fetch_data_from_db()
    create_directory('recipe_images')

    for row in all_rows:
        recipe_id, recipe_name, cone, materials, images = row

        recipe_name = recipe_name.replace(' ', '_').replace("'", "")
        recipe_dir = os.path.join('recipe_images', f"{recipe_id}_{recipe_name}")
        create_directory(recipe_dir)
        save_recipe_as_json(recipe_dir, [cone] + json.loads(materials))
        download_images(recipe_dir, json.loads(images), recipe_id)

    
if __name__ == "__main__":
    main()
