from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, session
import pytesseract
import cv2
import os
import numpy as np
import requests
import re
from io import BytesIO
# from weasyprint import HTML  # Removed to avoid import errors
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
from collections import OrderedDict
from inference import yolo_inference_function
from datetime import datetime
import json
from ultralytics import YOLO
from PIL import Image
import uuid
import shutil

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
model = None

@app.before_first_request
def load_model():
    global model
    model = YOLO("best.pt")

# Preprocess image for OCR
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    alpha = 1.8  # Contrast enhancement
    beta = 20    # Brightness adjustment
    contrast = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
    blur = cv2.GaussianBlur(contrast, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    kernel = np.ones((2, 2), np.uint8)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    return processed

# Extract text from the image
def extract_text(image_path):
    processed_image = preprocess_image(image_path)
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.png')
    cv2.imwrite(temp_path, processed_image)
    text = pytesseract.image_to_string(processed_image, config='--psm 11')
    return text.strip()

# Split text into unique words
def split_into_unique_words(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    words = text.split()
    unique_words = list(OrderedDict.fromkeys(words))
    return unique_words

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scanner", methods=['GET', 'POST'])
def scanner_page():
    result = None
    if request.method == 'POST':
        if 'imageInput' not in request.files:
            return redirect(request.url)
        file = request.files['imageInput']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            extracted_text = extract_text(file_path)
            result = split_into_unique_words(extracted_text)
    return render_template('scanner.html', result=result)

@app.route("/stores", methods=['GET', 'POST'])
def stores_page():
    pharmacies = []
    error = None
    if request.method == 'POST':
        location = request.form.get('location')
        if location:
            lat, lon = get_coordinates(location)
            if lat and lon:
                pharmacies = fetch_nearby_medical_stores(lat, lon)
                if not pharmacies:
                    error = "No pharmacies found nearby."
            else:
                error = "Location not found."
        else:
            error = "Please enter a location."
    return render_template('stores.html', pharmacies=pharmacies, error=error)

@app.route("/contact")
def contact_page():
    return render_template("contact.html")

@app.route('/report', methods=['GET'])
def report_page():
    return render_template("report.html")

@app.route('/report/<filename>', methods=['GET'])
def view_report(filename):
    """View a specific report by filename"""
    try:
        # Check if the file exists
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            return "Report not found", 404
        
        # Try to get result data from session or create default
        result_data = session.get('result_data')
        if result_data:
            result_data = json.loads(result_data)
        else:
            # Create a default result structure
            result_data = {
                "filename": filename,
                "nt": "Not Detected",
                "risk": "Unknown",
                "structures": {},
                "summary": "Report data not available.",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        return render_template("Genrepo.html", results=result_data)
    except Exception as e:
        return f"Error loading report: {str(e)}", 500

def get_coordinates(location):
    geocode_url = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(location)}&format=json"
    headers = {'User-Agent': 'Mozilla/5.0 (MyPharmacyApp/1.0)'}
    response = requests.get(geocode_url, headers=headers)
    if response.status_code == 200 and response.json():
        result = response.json()[0]
        return float(result["lat"]), float(result["lon"])
    return None, None

def fetch_nearby_medical_stores(lat, lon):
    query = f"""
        [out:json];
        node["amenity"="pharmacy"](around:5000,{lat},{lon});
        out;
    """
    url = "https://overpass-api.de/api/interpreter?data=" + requests.utils.quote(query)
    headers = {'User-Agent': 'Mozilla/5.0 (MyPharmacyApp/1.0)'}
    response = requests.get(url, headers=headers)
    try:
        data = response.json()
        pharmacies = [{
            "name": elem.get("tags", {}).get("name", "Unnamed Pharmacy"),
            "lat": elem.get("lat"),
            "lon": elem.get("lon")
        } for elem in data.get("elements", [])]
        return pharmacies
    except:
        return []

key_structures = {
    0: "Thalami",
    1: "Midbrain",
    2: "Palate",
    3: "4th Ventricle",
    4: "Cisterna Magna",
    5: "NT",
    6: "Nasal Tip",
    7: "Nasal Skin",
    8: "Nasal Bone"
}

key_structure_names = list(key_structures.values())

def calculate_nt_mm(normalized_height, image_height):
    return round(normalized_height * image_height * 0.1, 2)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if file:
            # Generate unique filename to avoid conflicts
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = str(uuid.uuid4()) + file_extension
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)

            # Check if model is loaded
            if model is None:
                return jsonify({"error": "AI model not loaded. Please try again."}), 500

            image_bgr = cv2.imread(filepath)
            if image_bgr is None:
                return jsonify({"error": "Invalid image file"}), 400
                
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            image_height, image_width = image_rgb.shape[:2]

            results = model.predict(image_rgb)[0]
            boxes = results.boxes

            detected_structures = set()
            nt_measurement_mm = None

            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                class_name = key_structures.get(cls_id, f"Unknown ({cls_id})")

                print(f"Detected {class_name} with confidence {conf:.2f}")

                detected_structures.add(class_name)

                cv2.rectangle(image_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image_bgr, class_name, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                if class_name.lower() == "nt":
                    box_height = y2 - y1
                    nt_measurement_mm = calculate_nt_mm(
                        box_height / image_height, image_height)

            risk = "High" if nt_measurement_mm and nt_measurement_mm > 3.0 else "Low" if nt_measurement_mm else "Unknown"

            annotated_filename = "annotated_" + unique_filename
            annotated_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
            cv2.imwrite(annotated_path, image_bgr)

            structure_status = {name: ("Detected" if name in detected_structures else "Not Detected")
                                for name in key_structure_names}

            diagnostic_summary = ""
            if nt_measurement_mm:
                diagnostic_summary += f"Nuchal Translucency (NT) measured {nt_measurement_mm} mm. "
                diagnostic_summary += "This is considered high risk for Down Syndrome. " if risk == "High" else "This is within normal limits. "
            else:
                diagnostic_summary += "Nuchal Translucency (NT) was not detected. "

            if "Nasal Bone" in detected_structures:
                diagnostic_summary += "Nasal bone is present. "
            else:
                diagnostic_summary += "Nasal bone is not detected, which could be an additional marker. "

            if "Cisterna Magna" in detected_structures:
                diagnostic_summary += "Cisterna Magna is visible."
            else:
                diagnostic_summary += "Cisterna Magna not detected. Further imaging may be needed."

            result_data = {
                "filename": annotated_filename,
                "nt": f"{nt_measurement_mm} mm" if nt_measurement_mm else "Not Detected",
                "risk": risk,
                "structures": structure_status,
                "summary": diagnostic_summary,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            session['result_data'] = json.dumps(result_data)
            return render_template("Genrepo.html", results=result_data)
        else:
            return jsonify({"error": "Invalid file"}), 400
            
    except Exception as e:
        print(f"Error in analyze route: {str(e)}")
        return jsonify({"error": f"An error occurred during analysis: {str(e)}"}), 500

@app.route('/download/<filename>')
def download_pdf(filename):
    # PDF generation removed due to WeasyPrint issues
    return "PDF generation temporarily disabled (WeasyPrint not installed)."

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
