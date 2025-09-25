import math
from ultralytics import YOLO
from PyQt6.QtWidgets import QApplication, QWidget
from UI_Funct.UI_Buttons_Functions import UI_func
import sys

def detect():
    try:
        model_path = "C:\\Users\\macar\\PycharmProjects\\1077\\Models\\YOLO11n_B.pt"
        img = UI_func.path[0]
        model = YOLO(model_path)
        results = model([img])

        for result in results:
            boxes = result.boxes  # Boxes object for bounding box outputs
            masks = result.masks  # Masks object for segmentation masks outputs
            keypoints = result.keypoints  # Keypoints object for pose outputs
            probs = result.probs  # Probs object for classification outputs
            obb = result.obb  # Oriented boxes object for OBB outputs
            result.save(filename="result.jpg")  # save to disk
    except:
        print("")


