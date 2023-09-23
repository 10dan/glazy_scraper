import os
import shutil
import cv2

def roi_selection(event, x, y, flags, param):
    global cropped_img, img_display

    if event == cv2.EVENT_MOUSEMOVE:
        img_display = img.copy()
        x_start = max(0, x - 256)
        y_start = max(0, y - 256)
        x_end = min(img.shape[1], x + 256)
        y_end = min(img.shape[0], y + 256)
        cv2.rectangle(img_display, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
        cv2.imshow('Select ROI', img_display)

    if event == cv2.EVENT_LBUTTONDOWN:
        cropped_img = img[y_start:y_end, x_start:x_end]

source_dir = "recipe_images"
destination_dir = "recipe_images_done"

cropped_img = None

if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)

# Get a list of all directories
all_dirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]

# Sort directories by recipe_id
sorted_dirs = sorted(all_dirs, key=lambda x: int(x.split('_')[0]))

for recipe_folder in sorted_dirs:
    dest_folder_path = os.path.join(destination_dir, recipe_folder)
    if not os.path.exists(dest_folder_path):
        os.makedirs(dest_folder_path)

    for img_file in os.listdir(os.path.join(source_dir, recipe_folder)):
        if img_file.endswith(".jpg"):
            img_path = os.path.join(source_dir, recipe_folder, img_file)
            
            img = cv2.imread(img_path)
            img_display = img.copy()
            
            cv2.namedWindow('Select ROI')
            cv2.setMouseCallback('Select ROI', roi_selection)

            while True:
                cv2.imshow('Select ROI', img_display)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('s'):
                    if cropped_img is not None:
                        cv2.imwrite(os.path.join(dest_folder_path, img_file), cropped_img)
                        shutil.copy(os.path.join(source_dir, recipe_folder, "recipe.json"),
                        os.path.join(dest_folder_path, "recipe.json"))
                    break
                elif key == ord('x'):
                    break

            cv2.destroyAllWindows()
