import os
import json
from PIL import Image
import numpy as np

def crop_center(image, crop_width=32, crop_height=32):
    width, height = image.size
    left = (width - crop_width) / 2
    top = (height - crop_height) / 2
    right = (width + crop_width) / 2
    bottom = (height + crop_height) / 2
    return image.crop((left, top, right, bottom))

def prepare_data():
    recipe_vectors = []
    glaze_images = []

    for folder in os.listdir('recipe_images'):
        with open(f'recipe_images/{folder}/recipe.json', 'r') as f:
            recipe = json.load(f)
        
        for image_file in os.listdir(f'recipe_images/{folder}'):
            if image_file.endswith('.jpg'):
                image = Image.open(f'recipe_images/{folder}/{image_file}').convert('RGB')
                cropped_image = crop_center(image)
                recipe_vectors.append(recipe)
                glaze_images.append(np.array(cropped_image))

    # Convert to NumPy arrays
    recipe_vectors = np.array(recipe_vectors)
    glaze_images = np.array(glaze_images)

    # Save to disk
    np.save('pickled_vectors.npy', recipe_vectors)
    np.save('pickled_images.npy', glaze_images)
# prepare_data()

vectors, images = np.load('pickled_vectors.npy'), np.load('pickled_images.npy')
print(vectors.shape, images.shape)