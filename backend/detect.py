# detect.py
from ultralytics import YOLO
import cv2
import os

model = YOLO("yolov8n.pt")

def run_detection(image_path):
    results = model(image_path)[0]
    
    # Save annotated image
    output_path = os.path.join("static", "predicted.jpg")
    results.save(save_dir="static")  # saves image in static/
    
    # You can extract labels if needed
    labels = [model.names[int(cls)] for cls in results.boxes.cls]
    
    return output_path, labels

