import os
import shutil
import cv2
import json

def roi_selection(event, x, y, flags, param):
    global drawing, top_left_pt, bottom_right_pt
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        top_left_pt = (x, y)
        
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        bottom_right_pt = (x, y)
        cv2.rectangle(img, top_left_pt, bottom_right_pt, (0, 255, 0), 2)
        cv2.imshow('Select ROI', img)

source_dir = "recipe_images"
destination_dir = "recipe_images_done"

drawing = False
top_left_pt, bottom_right_pt = None, None

if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)

for recipe_folder in os.listdir(source_dir):
    if os.path.isdir(os.path.join(source_dir, recipe_folder)):
        
        dest_folder_path = os.path.join(destination_dir, recipe_folder)
        if not os.path.exists(dest_folder_path):
            os.makedirs(dest_folder_path)
        
        shutil.copy(os.path.join(source_dir, recipe_folder, "recipe.json"),
                    os.path.join(dest_folder_path, "recipe.json"))
        
        for img_file in os.listdir(os.path.join(source_dir, recipe_folder)):
            if img_file.endswith(".jpg"):
                img_path = os.path.join(source_dir, recipe_folder, img_file)
                
                img = cv2.imread(img_path)
                cv2.namedWindow('Select ROI')
                cv2.setMouseCallback('Select ROI', roi_selection)
                
                while True:
                    cv2.imshow('Select ROI', img)
                    
                    if cv2.waitKey(1) & 0xFF == ord('s'):
                        break
                
                cv2.destroyAllWindows()
                
                if top_left_pt and bottom_right_pt:
                    cropped_img = img[top_left_pt[1]:bottom_right_pt[1], top_left_pt[0]:bottom_right_pt[0]]
                    cropped_img = cv2.resize(cropped_img, (512, 512))
                    
                    cv2.imwrite(os.path.join(dest_folder_path, img_file), cropped_img)
