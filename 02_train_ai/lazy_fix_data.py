import os
import json
import shutil

def check_json_format(directory):
    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)
        if os.path.isdir(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.json'):
                    file_path = os.path.join(folder_path, file_name)
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if len(data) != 196:
                            print("error length! bad!!")
                    # if not isinstance(data, list) or len(data) != 195:
                    #     print(f'Error: {file_path} wrong length')
                    # elif not all(isinstance(item, (int, float)) for item in data):
                    #     print(f'Error: {file_path} non-numeric values.')

directory = "recipe_images_done"
# check_json_format(directory)

def check_and_remove_malformed(directory):
    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)
        if os.path.isdir(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.json'):
                    file_path = os.path.join(folder_path, file_name)
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    if len(data) != 196:
                        print(f'Removing malformed recipe folder: {folder_path}')
                        shutil.rmtree(folder_path)  # This will delete the folder and all its contents
                        break  # No need to check other files in this folder

# check_and_remove_malformed(directory)