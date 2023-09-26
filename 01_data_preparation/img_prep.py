import os
import shutil
import cv2

json_copied = False  # Flag to check if recipe.json has been copied for the current recipe folder
next_image = False  # Flag to move to the next image
x_start, y_start, x_end, y_end = 0, 0, 0, 0 

def roi_selection(event, x, y, flags, param):
    global cropped_img, img_display, json_copied, dest_folder_path, next_image
    global x_start, y_start, x_end, y_end
    
    if event == cv2.EVENT_MOUSEMOVE:
        img_display = img.copy()
        x_start = max(0, x - 256)
        y_start = max(0, y - 256)
        x_end = min(img.shape[1], x + 256)
        y_end = min(img.shape[0], y + 256)
        cv2.rectangle(img_display, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
        cv2.imshow("Select ROI", img_display)

    if event == cv2.EVENT_LBUTTONDOWN:
        cropped_img = img[y_start:y_end, x_start:x_end]
        
        if cropped_img.size == 0:  # Check if the cropped image is empty
            return
        
        # Resize the cropped image to 512x512
        cropped_img = cv2.resize(cropped_img, (512, 512))
        
        dest_folder_path = os.path.join(destination_dir, recipe_folder)
        if not os.path.exists(dest_folder_path):
            os.makedirs(dest_folder_path)  # Create the directory here
        if not json_copied:
            shutil.copy(
                os.path.join(source_dir, recipe_folder, "recipe.json"),
                os.path.join(dest_folder_path, "recipe.json"),
            )
            json_copied = True
        cv2.imwrite(os.path.join(dest_folder_path, img_file), cropped_img)
        next_image = True  # Set the flag to move to the next image

source_dir = "recipe_images"
destination_dir = "recipe_images_done"
# Hours logged:
# 2023-09-23: 2.0 3.29%


start_from_recipe_id = 10884  # Set this to the recipe_id from where you want to start the cropping process
cropped_img = None

if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)

# Get a list of all directories
all_dirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]

# Sort directories by recipe_id
sorted_dirs = sorted(all_dirs, key=lambda x: int(x.split("_")[0]))

for recipe_folder in sorted_dirs:
    current_recipe_id = int(recipe_folder.split("_")[0])
    print(f"looking for recipe: {current_recipe_id} / 252810. %complete: {current_recipe_id / 252810 * 100:.2f}")
    if current_recipe_id < start_from_recipe_id:
        continue  # Skip to the next iteration of the loop

    json_copied = False  # Reset the flag for each new recipe folder

    img_number = 0 # Only want to look at 2 pics at most - this will count for us.
    for img_file in os.listdir(os.path.join(source_dir, recipe_folder)):
        if img_number == 2:
            break
        if img_file.endswith(".jpg"):
            next_image = False
            img_path = os.path.join(source_dir, recipe_folder, img_file)
            img = cv2.imread(img_path)
            if img is None:
                print(f"Failed to read {img_path}. Skipping.")
                continue
            img_display = img.copy()
            cv2.namedWindow("Select ROI")
            cv2.setMouseCallback("Select ROI", roi_selection)
            
            while True:
                cv2.imshow("Select ROI", img_display)
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord("x") or next_image:
                    img_number += 1
                    break
            
            cv2.destroyAllWindows()
