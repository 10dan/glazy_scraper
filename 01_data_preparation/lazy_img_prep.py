# For this one, im just gonna take the middle 256 pixels.
# Would take me way too long to do it manually. (70h)
# ok, yea maybe we will have lots of bad data.. but maybe itll average out to be more accurate overall?

import os
from PIL import Image, UnidentifiedImageError
import shutil

script_path = os.path.realpath(__file__)
parent_directory = os.path.dirname(os.path.dirname(script_path))

old_directory = os.path.join(parent_directory, 'recipe_images')
new_directory = os.path.join(parent_directory, 'recipe_images_lazy')

if not os.path.exists(new_directory):
    os.makedirs(new_directory)

def crop_center(img, crop_width, crop_height):
    img_width, img_height = img.size
    return img.crop(((img_width - crop_width) // 2,
                     (img_height - crop_height) // 2,
                     (img_width + crop_width) // 2,
                     (img_height + crop_height) // 2))

for recipe in os.listdir(old_directory): 

    new_recipe_dir = os.path.join(new_directory, recipe)
    if not os.path.exists(new_recipe_dir):
        os.makedirs(new_recipe_dir)

    for file in os.listdir(os.path.join(old_directory, recipe)):
        print(file)
        if file.endswith('.json'):
            # Copy the json file
            shutil.copy(
                os.path.join(old_directory, recipe, file),
                os.path.join(new_recipe_dir, file),
            )
        if file.endswith('.jpg'):
            # Crop the image
            img_path = os.path.join(old_directory, recipe, file)
            try:
                img = Image.open(img_path)
                cropped_img = crop_center(img, 256, 256).convert('RGB')
                cropped_img.save(os.path.join(new_recipe_dir, file))
            except UnidentifiedImageError:
                print(f"Cannot identify image file {img_path}")
            except Exception as e:
                print(f"An error occurred while processing {img_path}: {e}")


