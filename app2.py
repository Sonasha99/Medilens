from flask import Flask, render_template, request, redirect, url_for
from ultralytics import YOLO
import os
from PIL import Image
import uuid
import cv2
import shutil

app = Flask(__name__)

# Set up the directory for saving uploads and predictions
UPLOAD_FOLDER = 'static/uploads/'
OUTPUT_FOLDER = 'static/predictions/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER


# Load your YOLOv8 model
model = YOLO('best.pt')  # Replace with 'yolov8n.pt' if needed
print(model.names)

# Ensure upload/output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def home():
    return render_template('report.html', report=None, image_path=None)

@app.route('/report')
def report():
    return render_template("report.html")

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['image']
    if not file:
        return redirect(url_for('home'))

    # Save uploaded file
    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Run YOLOv8 model prediction
    results = model.predict(filepath, save=True, project=app.config['OUTPUT_FOLDER'], name=filename.split('.')[0], exist_ok=True)
    print(results[0].boxes)
    print(results[0].names)  # check class names
    print(results[0].boxes.cls)  # class indexes
    
    #
    result = results[0]

    # YOLO saves predictions like: static/predictions/filename/filename.jpg
    pred_dir = os.path.join(app.config['OUTPUT_FOLDER'], filename.split('.')[0])
    pred_img_filename = filename  # same as original filename
    pred_img_path = os.path.join('predictions', filename.split('.')[0], pred_img_filename)

    # Get YOLO's saved output image
    result_dir = results[0].save_dir
    boxed_image_path = os.path.join(result_dir, filename)
    final_path = os.path.join(UPLOAD_FOLDER, filename)
    shutil.copy(boxed_image_path, final_path)

    # Extract labels
    labels = [model.names[int(cls)] for cls in result.boxes.cls]
    print("Detected Labels:", labels) 
   

    #labels = [r.names[int(cls)] for cls in results[0].boxes.cls]  # detected classes
    def label_found(name): return "Yes" if name in labels else "No"

    nt_measurement = round(1.5 + 0.1 * len(labels), 2)
    # Generate report data from results (dummy example here)
    #labels = [r.names[int(cls)] for cls in results[0].boxes.cls]  # detected classes
    
    report = {
        # "Thalami": label_found("Thalami"),
        # "Midbrain": label_found("Midbrain"),
        # "Palate": label_found("Palate"),
        # "4th Ventricle": label_found("4th Ventricle"),
        # "Cisterna Magna": label_found("Cisterna Magna"),
        # "NT Measurement": nt_measurement,
        # "Nasal Tip": label_found("Nasal Tip"),
        # "Nasal Skin": label_found("Nasal Skin"),
        # "Nasal Bone": label_found("Nasal Bone"),
        # "Presence of Nasal Bone": label_found("Nasal Bone"),
        # "Cisterna Magna Visibility": label_found("Cisterna Magna"),
        # "Down Syndrome Risk": "Low" if nt_measurement < 3.0 and label_found("Nasal Bone") == "Yes" else "High"
        "Thalami": "Detected" if "Thalami" in labels else "Not Detected",
        "Midbrain": "Detected" if "Midbrain" in labels else "Not Detected",
        "Palate": "Detected" if "Palate" in labels else "Not Detected",
        "4th Ventricle": "Detected" if "4th Ventricle" in labels else "Not Detected",
        "Cisterna Magna": "Detected" if "Cisterna Magna" in labels else "Not Detected",
        "NT Measurement": "1.4",  # placeholder
        "Nasal Tip": "Detected" if "Nasal Tip" in labels else "Not Detected",
        "Nasal Skin": "Detected" if "Nasal Skin" in labels else "Not Detected",
        "Nasal Bone": "Detected" if "Nasal Bone" in labels else "Not Detected",
        "Presence of Nasal Bone": "Yes" if "Nasal Bone" in labels else "No",
        "Cisterna Magna Visibility": "Visible" if "Cisterna Magna" in labels else "Not Visible",
        "Down Syndrome Risk": "Low" if "Nasal Bone" in labels and float(report_data["NT Measurement"]) < 2.5 else "High"
    }
    return render_template(
        "report.html",
        image_path=pred_img_path,
        report=report,
        labels=labels
    )

    # Get the YOLO output image path
    output_img_path = os.path.join(app.config['OUTPUT_FOLDER'], filename.split('.')[0], filename)
    image_relative_path = os.path.relpath(output_img_path, 'static')

    return render_template('report.html', report=report, labels=labels, image_path=image_relative_path)

@app.route('/scanner')
def scanner_page():
    return "Prescription Scanner Page (under construction)"

@app.route('/contact')
def contact_page():
    return "Contact Page (under construction)"

@app.route('/stores')
def stores_page():
    return "Medical Stores Page (under construction)"

if __name__ == '__main__':
    app.run(debug=True)
