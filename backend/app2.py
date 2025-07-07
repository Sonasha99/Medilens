# Ultrasound-related portions have been commented out for now.

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, session, flash
import pytesseract
import cv2
import os
import numpy as np
import requests
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import logging
from werkzeug.utils import secure_filename
from collections import OrderedDict
from datetime import datetime
import uuid

# Initialize REPORT_MODULE_AVAILABLE first
REPORT_MODULE_AVAILABLE = False

# --- ULTRASOUND SECTION START ---
# from ultralytics import YOLO
# from report import enhanced_analyze_ultrasound_image, save_pdf_report, generate_summary_json
# from report import MedicalReportGenerator
# try:
#     from report import (
#         enhanced_analyze_ultrasound_image,
#         save_pdf_report,
#         generate_summary_json,
#         MedicalReportGenerator
#     )
#     REPORT_MODULE_AVAILABLE = True
# except ImportError as e:
#     print(f"Warning: report.py module not found or has issues: {e}")
#     REPORT_MODULE_AVAILABLE = False
# --- ULTRASOUND SECTION END ---

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract-ocr"

app = Flask(__name__, template_folder="./../templates/", static_folder="./../static")
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = os.path.abspath('./../static/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['STATIC_FOLDER'] = os.path.abspath('./../static')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_errors(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({'error': 'An error occurred processing your request'}), 500
    return decorated_function

@app.before_request
def initialize_app():
    if not hasattr(app, 'initialized'):
        # --- ULTRASOUND SECTION START ---
        # global model
        # if model is None:
        #     try:
        #         model_path = "./../best.pt"
        #         if os.path.exists(model_path):
        #             model = YOLO(model_path)
        #             logger.info("YOLO model loaded successfully")
        #         else:
        #             logger.error(f"Model file not found at {model_path}")
        #     except Exception as e:
        #         logger.error(f"Failed to load YOLO model: {str(e)}")
        #         raise
        # --- ULTRASOUND SECTION END ---
        app.initialized = True

def ensure_upload_directory():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        logger.info(f"Created upload directory: {app.config['UPLOAD_FOLDER']}")

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    contrast = cv2.convertScaleAbs(gray, alpha=1.8, beta=20)
    blur = cv2.GaussianBlur(contrast, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    kernel = np.ones((2, 2), np.uint8)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    return processed

def extract_text(image_path):
    processed_image = preprocess_image(image_path)
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'processed.png'), processed_image)
    return pytesseract.image_to_string(processed_image, config='--psm 11').strip()

def split_into_unique_words(text):
    text = re.sub(r"[^\w\s]", "", text.lower())
    return list(OrderedDict.fromkeys(text.split()))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scanner", methods=['GET', 'POST'])
def scanner_page():
    result = None
    if request.method == 'POST':
        file = request.files.get('imageInput')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            result = split_into_unique_words(extract_text(file_path))
    return render_template('scanner.html', result=result)

@app.route("/stores", methods=['GET', 'POST'])
def stores_page():
    pharmacies, error = [], None
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

def get_coordinates(location):
    response = requests.get(
        f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(location)}&format=json",
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    if response.status_code == 200 and response.json():
        result = response.json()[0]
        return float(result['lat']), float(result['lon'])
    return None, None

def fetch_nearby_medical_stores(lat, lon):
    query = f"""
        [out:json];
        node["amenity"="pharmacy"](around:5000,{lat},{lon});
        out;
    """
    response = requests.get(
        "https://overpass-api.de/api/interpreter?data=" + requests.utils.quote(query),
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    try:
        data = response.json()
        return [{
            "name": elem.get("tags", {}).get("name", "Unnamed Pharmacy"),
            "lat": elem.get("lat"),
            "lon": elem.get("lon")
        } for elem in data.get("elements", [])]
    except:
        return []

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html') if os.path.exists(os.path.join(app.template_folder, '404.html')) else "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html') if os.path.exists(os.path.join(app.template_folder, '500.html')) else "Internal server error", 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

if __name__ == '__main__':
    ensure_upload_directory()
    print("\nMedical Imaging Flask App (Ultrasound features disabled)")
    print("Upload folder:", app.config['UPLOAD_FOLDER'])
    print("Available routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    app.run(host='127.0.0.1', port=5000, debug=True)

