import sqlite3
import json
import os

cones = {
    "04-11",
    "02",
    "3",
    "6-8",
    "7-9",
    "08-1",
    "4-8",
    "6-12",
    "10",
    "7-10",
    "1",
    "4-10",
    "1-6",
    "6-7",
    "9-12",
    "9-10",
    "7",
    "05½-10",
    "5-6",
    "4",
    "10-12",
    "4-5½",
    "8-11",
    "5-9",
    "05½-04",
    "9-11",
    "7-8",
    "8-12",
    "4-7",
    "4-6",
    "03",
    "5½-9",
    "04-1",
    "04-10",
    "5½-10",
    "5",
    "08-2",
    "06",
    "6",
    "07-5",
    "06-6",
    "08-05½",
    "6-10",
    "07",
    "015",
    "6-11",
    "N/A",
    "4-5",
    "06-04",
    "5-5½",
    "06-02",
    "04-02",
    "11",
    "9",
    "5½",
    "5-7",
    "07-06",
    "8-9",
    "?",
    "11-12",
    "05½-03",
    "6-9",
    "10-11",
    "8-10",
    "07-6",
    "9-14",
    "9-13",
    "8",
    "1-10",
    "04",
    "04-03",
    "3-11",
    "5½-7",
    "10-14",
    "05-04",
    "4-12",
    "05",
    "06-05",
    "5-8",
    "3-5",
    "04-3",
    "5-10",
    "012-08",
    "5½-6",
}


def clean_cone(cone_str):
    if cone_str in {"N/A", "?"}:
        return 0.5

    multiplier = -1 if cone_str.startswith("0") else 1

    if "-" in cone_str:
        low, high = map(str.strip, cone_str.split("-"))
        low = float(low.replace("½", ".5")) * multiplier
        high = float(high.replace("½", ".5")) * multiplier
        return (low + high) / 2
    else:
        return float(cone_str.replace("½", ".5")) * multiplier


cleaned_cones = {clean_cone(cone) for cone in cones if clean_cone(cone) is not None}
max_cone = max(cleaned_cones)
min_cone = min(cleaned_cones)


def normalize_cone(cone):
    return (cone - min_cone) / (max_cone - min_cone)


def normalize_recipe(recipe):
    total_amt = sum(float(ingredient["amt"]) for ingredient in recipe)
    return {
        ingredient["name"]: float(ingredient["amt"]) / total_amt
        for ingredient in recipe
    }


def update_db():
    # delete existing normalized_recipes.db
    try:
        os.remove("normalized_recipes.db")
    except FileNotFoundError:
        pass

    # Connect to the original database
    conn = sqlite3.connect("recipes.db")
    c = conn.cursor()

    # Create and connect to a new database for storing normalized data
    new_conn = sqlite3.connect("normalized_recipes.db")
    new_c = new_conn.cursor()
    new_c.execute(
        """CREATE TABLE IF NOT EXISTS normalized_recipes
                   (recipe_id INTEGER PRIMARY KEY, recipe_name TEXT, cone REAL, materials TEXT, images TEXT)"""
    )
    
    unique_materials = set()
    c.execute("SELECT * FROM recipes")
    for row in c.fetchall():
        recipe_id, recipe_name, cone, image_urls, materials = row
        parsed_mats = json.loads(materials.replace("'", '"'))
        unique_materials.update(ingredient["name"] for ingredient in parsed_mats)

    c.execute("SELECT * FROM recipes")
    for row in c.fetchall():
        recipe_id, recipe_name, cone, image_urls, materials = row

        recipe_name = recipe_name.replace(" ", "_").replace("'", "").replace("/", "")
        
        cleaned_cone = clean_cone(cone)
        normalized_cone = normalize_cone(cleaned_cone)

        parsed_mats = json.loads(materials.replace("'", '"'))
        parsed_imgs = json.loads(image_urls.replace("'", '"'))

        new_imgs = json.dumps(parsed_imgs)
        normalized_materials = normalize_recipe(parsed_mats)
        normalized_material_vector = [0] * len(unique_materials)
        material_to_index = {
            material: index for index, material in enumerate(unique_materials)
        }

        for material, normalized_amt in normalized_materials.items():
            index = material_to_index[material]
            normalized_material_vector[index] = normalized_amt

        new_c.execute(
            "INSERT INTO normalized_recipes (recipe_id, recipe_name, cone, materials, images) VALUES (?, ?, ?, ?, ?)",
            (
                recipe_id,
                recipe_name,
                normalized_cone,
                json.dumps(normalized_material_vector),
                new_imgs,
            ),
        )

    new_conn.commit()
    new_conn.close()
    conn.close()


if __name__ == "__main__":
    update_db()
