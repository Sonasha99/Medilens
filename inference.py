from ultralytics import YOLO
import cv2
import os

# Load model once
model = YOLO("yolov8n.pt")  # replace with your custom model if needed

def yolo_inference_function(image_path):
    # Load your YOLOv8 model (you can use a pretrained model or load your own custom trained model)
    model = torch.hub.load('yolov8n.pt')
    model.eval() 
    

    # Load the image
    image = Image.open(image_path)

    # Apply necessary transformations to the image (resize, normalize, etc.)
    transform = transforms.Compose([
        transforms.Resize((640, 640)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image = transform(image).unsqueeze(0)  # Add batch dimension

    # Perform inference
    results = model(image)  # Run inference on the image

    # Process the results (you may need to adjust based on your model's output)
    labels = results.names  # Get class names from the results
    predictions = results.pred[0]  # Predicted bounding boxes and labels
    
    # Extract detected labels (e.g., "person", "car", etc.)
    detected_labels = [labels[int(pred[5])] for pred in predictions if pred[4] > 0.5]  # Confidence threshold of 0.5

    # Return the image path and detected labels
    return image_path, detected_labels
def generate_ultrasound_report(labels):
    print("🔍 Running YOLOv8 prediction...")
    report = {}

    structures = {label["name"]: label["bbox"] for label in labels}

    # NT Measurement (mock logic – replace with actual)
    if "Nuchal Translucency (NT)" in structures:
        nt_box = structures["Nuchal Translucency (NT)"]
        nt_measurement = abs(nt_box[3] - nt_box[1])  # height
        report["NT Measurement"] = f"{nt_measurement:.2f} pixels"
    else:
        report["NT Measurement"] = "Not detected"

    # Nasal Bone Presence
    report["Nasal Bone"] = "Present" if "Nasal Bone" in structures else "Absent"

    # Cisterna Magna
    report["Cisterna Magna"] = "Visible" if "Cisterna Magna" in structures else "Not visible"

    # Risk assessment (very basic logic – enhance later)
    if report["NT Measurement"] != "Not detected":
        nt_value = float(report["NT Measurement"].split()[0])
        if nt_value > 3.0:
            report["Down Syndrome Risk"] = "High Risk"
        else:
            report["Down Syndrome Risk"] = "Low Risk"
    else:
        report["Down Syndrome Risk"] = "Unknown"

    return report
