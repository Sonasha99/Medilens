# #!/usr/bin/env python3
# """
# Complete Medical Imaging Flask App
# Make sure this is your main app.py file
# """

# from flask import Flask, request, render_template, flash, url_for, redirect
# import os
# from werkzeug.utils import secure_filename
# import uuid
# import traceback

# # Initialize Flask app
# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'static/uploads'
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# app.secret_key = 'your-secret-key-change-this-in-production'

# # Allowed file extensions
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

# def allowed_file(filename):
#     """Check if file extension is allowed"""
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def create_upload_folder():
#     """Ensure upload folder exists"""
#     if not os.path.exists(app.config['UPLOAD_FOLDER']):
#         os.makedirs(app.config['UPLOAD_FOLDER'])
#         print(f"Created upload folder: {app.config['UPLOAD_FOLDER']}")

# # HOME ROUTE
# @app.route('/')
# def index():
#     """Home page"""
#     return render_template('index.html')

# @app.route('/home')  # Explicit 'home' endpoint
# def home():
#     return render_template('index.html') 

# # OCR SCANNER ROUTE
# @app.route('/scanner_page', methods=['GET', 'POST'])
# def scanner():
#     """OCR Scanner page"""
#     if request.method == 'POST':
#         if 'imageInput' not in request.files:
#             return render_template('scanner.html', error='No file selected')
        
#         file = request.files['imageInput']
#         if file.filename == '':
#             return render_template('scanner.html', error='No file selected')
        
#         if file and allowed_file(file.filename):
#             try:
#                 create_upload_folder()
#                 filename = secure_filename(file.filename)
#                 unique_filename = f"{uuid.uuid4().hex}_{filename}"
#                 filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
#                 file.save(filepath)
                
#                 # Placeholder OCR processing
#                 extracted_text = "Sample extracted text from the image"
#                 result = ["medical", "prescription", "dosage", "patient"]
                
#                 return render_template('scanner.html', 
#                                      extracted_text=extracted_text, 
#                                      result=result)
                                     
#             except Exception as e:
#                 return render_template('scanner.html', error=f'Error processing file: {str(e)}')
#         else:
#             return render_template('scanner.html', error='Invalid file type')
    
#     return render_template('scanner.html')

# # PHARMACY LOCATOR ROUTE
# @app.route('/stores', methods=['GET', 'POST'])
# def stores():
#     """Pharmacy locator page"""
#     if request.method == 'POST':
#         location = request.form.get('location', '').strip()
#         if not location:
#             return render_template('stores.html', error='Please enter a location')
        
#         # Placeholder pharmacy data
#         pharmacies = [
#             {
#                 'name': 'MedPlus Pharmacy',
#                 'address': f'123 Main St, {location}',
#                 'phone': '+1 (555) 123-4567',
#                 'rating': 4.5,
#                 'hours': '8:00 AM - 10:00 PM'
#             },
#             {
#                 'name': 'Apollo Pharmacy',
#                 'address': f'456 Health Ave, {location}',
#                 'phone': '+1 (555) 234-5678',
#                 'rating': 4.2,
#                 'hours': '24 Hours'
#             },
#             {
#                 'name': 'Local Pharmacy',
#                 'address': f'789 Care Blvd, {location}',
#                 'phone': '+1 (555) 345-6789',
#                 'rating': 4.0,
#                 'hours': '9:00 AM - 9:00 PM'
#             }
#         ]
        
#         return render_template('stores.html', pharmacies=pharmacies)
    
#     return render_template('stores.html')

# # ULTRASOUND ANALYSIS ROUTE
# @app.route('/report', methods=['GET', 'POST'])
# def report():
#     """Ultrasound analysis page"""
#     print(f"Report route accessed with method: {request.method}")  # Debug
    
#     if request.method == 'POST':
#         try:
#             print("Processing POST request for ultrasound analysis")  # Debug
            
#             # Check if the post request has the file part
#             if 'ultrasoundImage' not in request.files:
#                 error_msg = 'No file selected'
#                 print(f"Error: {error_msg}")  # Debug
#                 print(f"Available files: {list(request.files.keys())}")  # Debug
#                 flash(error_msg)
#                 return render_template('report.html', error=error_msg)
            
#             file = request.files['ultrasoundImage']
#             print(f"File received: {file.filename}")  # Debug
            
#             # If user does not select file, browser also submits empty part without filename
#             if file.filename == '':
#                 error_msg = 'No file selected'
#                 print(f"Error: {error_msg}")  # Debug
#                 flash(error_msg)
#                 return render_template('report.html', error=error_msg)
            
#             if file and allowed_file(file.filename):
#                 print("File is valid, processing...")  # Debug
                
#                 # Create upload folder if it doesn't exist
#                 create_upload_folder()
                
#                 # Generate unique filename to avoid conflicts
#                 filename = secure_filename(file.filename)
#                 unique_filename = f"{uuid.uuid4().hex}_{filename}"
#                 filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
#                 # Save the file
#                 file.save(filepath)
#                 print(f"File saved to: {filepath}")  # Debug
                
#                 # Verify file was saved
#                 if os.path.exists(filepath):
#                     file_size = os.path.getsize(filepath)
#                     print(f"File exists, size: {file_size} bytes")  # Debug
                    
#                     # Process the image (placeholder for actual analysis)
#                     analysis_result = analyze_ultrasound_image(filepath)
                    
#                     return render_template('report.html', 
#                                          image_path=filepath,
#                                          analysis_result=analysis_result)
#                 else:
#                     error_msg = 'Failed to save uploaded file'
#                     print(f"Error: {error_msg}")  # Debug
#                     return render_template('report.html', error=error_msg)
                    
#             else:
#                 error_msg = 'Invalid file type. Please upload an image file.'
#                 print(f"Error: {error_msg}")  # Debug
#                 allowed_ext = ', '.join(ALLOWED_EXTENSIONS)
#                 return render_template('report.html', 
#                                      error=f'{error_msg} Allowed: {allowed_ext}')
        
#         except Exception as e:
#             error_msg = f'Unexpected error: {str(e)}'
#             print(f"Exception in report route: {error_msg}")  # Debug
#             print(traceback.format_exc())  # Full traceback
#             return render_template('report.html', error=error_msg)
    
#     # GET request - show the form
#     print("Showing report form (GET request)")  # Debug
#     return render_template('report.html')

# def analyze_ultrasound_image(image_path):
#     """
#     Placeholder function for ultrasound image analysis
#     Replace this with your actual YOLO model analysis
#     """
#     print(f"Analyzing image: {image_path}")  # Debug
    
#     # Dummy analysis result
#     analysis_result = {
#         'detections': [
#             {'class_name': 'Fetal Head', 'confidence': 0.85},
#             {'class_name': 'Spine', 'confidence': 0.72}
#         ],
#         'summary': 'Image processed successfully. Detected fetal structures with good visibility.'
#     }
    
#     return analysis_result

# # CONTACT ROUTE
# @app.route('/contact', methods=['GET', 'POST'])
# def contact():
#     """Contact page"""
#     if request.method == 'POST':
#         name = request.form.get('name', '').strip()
#         email = request.form.get('email', '').strip()
#         subject = request.form.get('subject', '').strip()
#         message = request.form.get('message', '').strip()
        
#         if not all([name, email, subject, message]):
#             return render_template('contact.html', error='Please fill in all fields')
        
#         # Here you would normally send the email or save to database
#         # For now, just show success message
#         success_msg = f'Thank you {name}! Your message has been received.'
#         return render_template('contact.html', success=success_msg)
    
#     return render_template('contact.html')

# # DEBUG ROUTES
# @app.route('/debug')
# def debug_info():
#     """Debug information page"""
#     info = {
#         'Flask version': flask.__version__ if 'flask' in globals() else 'Unknown',
#         'Upload folder': app.config['UPLOAD_FOLDER'],
#         'Upload folder exists': os.path.exists(app.config['UPLOAD_FOLDER']),
#         'Max content length': app.config['MAX_CONTENT_LENGTH'],
#         'Template folder': app.template_folder,
#         'Static folder': app.static_folder,
#         'Routes': [str(rule) for rule in app.url_map.iter_rules()]
#     }
    
#     return f"<pre>{str(info)}</pre>"

# @app.route('/test_upload', methods=['GET', 'POST'])
# def test_upload():
#     """Simple upload test"""
#     if request.method == 'POST':
#         print("=== TEST UPLOAD DEBUG ===")
#         print(f"Request files: {list(request.files.keys())}")
#         print(f"Request form: {dict(request.form)}")
        
#         for key, file in request.files.items():
#             print(f"File key: {key}, filename: {file.filename}, content_type: {file.content_type}")
        
#         return f"Test complete. Check console for debug info."
    
#     return '''
#     <!DOCTYPE html>
#     <html>
#     <head><title>Upload Test</title></head>
#     <body>
#         <h2>Simple Upload Test</h2>
#         <form method="POST" enctype="multipart/form-data">
#             <input type="file" name="test_file" accept="image/*"><br><br>
#             <button type="submit">Test Upload</button>
#         </form>
#     </body>
#     </html>
#     '''

# # ERROR HANDLERS
# @app.errorhandler(404)
# def not_found_error(error):
#     """Handle 404 errors"""
#     return f'''
#     <h1>404 - Page Not Found</h1>
#     <p>The requested URL was not found on the server.</p>
#     <p>Available routes:</p>
#     <ul>
#         <li><a href="/">Home</a></li>
#         <li><a href="/scanner">OCR Scanner</a></li>
#         <li><a href="/stores">Pharmacy Locator</a></li>
#         <li><a href="/report">Ultrasound Analysis</a></li>
#         <li><a href="/contact">Contact</a></li>
#         <li><a href="/debug">Debug Info</a></li>
#         <li><a href="/test_upload">Test Upload</a></li>
#     </ul>
#     ''', 404

# @app.errorhandler(413)
# def too_large(e):
#     """Handle file too large errors"""
#     return render_template('report.html', 
#                          error='File too large. Maximum size is 16MB.'), 413

# @app.errorhandler(500)
# def internal_error(error):
#     """Handle 500 errors"""
#     print(f"Internal server error: {error}")
#     print(traceback.format_exc())
#     return '''
#     <h1>500 - Internal Server Error</h1>
#     <p>Something went wrong on the server.</p>
#     <p><a href="/">Go back to home</a></p>
#     ''', 500

# # MAIN EXECUTION
# if __name__ == '__main__':
#     print("Starting Medical Imaging Flask App...")
#     print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
#     print(f"Template folder: {app.template_folder}")
#     print(f"Static folder: {app.static_folder}")
    
#     # Create upload folder if it doesn't exist
#     create_upload_folder()
    
#     # Show available routes
#     print("\nAvailable routes:")
#     for rule in app.url_map.iter_rules():
#         print(f"  {rule.rule} -> {rule.endpoint}")
    
#     print("\n🚀 Starting server on http://127.0.0.1:5000")
#     print("Available pages:")
#     print("  - Home: http://127.0.0.1:5000/")
#     print("  - OCR Scanner: http://127.0.0.1:5000/scanner")
#     print("  - Pharmacy Locator: http://127.0.0.1:5000/stores")
#     print("  - Ultrasound Analysis: http://127.0.0.1:5000/report")
#     print("  - Contact: http://127.0.0.1:5000/contact")
#     print("  - Debug Info: http://127.0.0.1:5000/debug")
#     print("  - Test Upload: http://127.0.0.1:5000/test_upload")
    
#     app.run(debug=True, host='127.0.0.1', port=5000)


from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, session
import pytesseract
import cv2
import os
import numpy as np
import requests
import re
from io import BytesIO
# Replaced WeasyPrint with reportlab (lighter alternative)
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
from collections import OrderedDict
#from ai_backend.inference import  run_detection, generate_ultrasound_report
from datetime import datetime
import json
from ultralytics import YOLO
from PIL import Image
import uuid
import shutil
import logging
from functools import wraps
import os

from report import enhanced_analyze_ultrasound_image, save_pdf_report, generate_summary_json
from report import MedicalReportGenerator
# import report import enhanced_analyze_ultrasound_image, save_pdf_report, generate_summary_json
#app = Flask(__name__)

app = Flask(__name__, template_folder="./../src/templates", static_folder="src/static")
app.has_run_before = False
app.secret_key = 'your_secret_key_here'  # TODO: Change this to a secure random key in production
app.config['UPLOAD_FOLDER'] = './../src/static/uploads'  # PATH: Configure upload directory
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

import os
print("Template directory is:", os.path.abspath(app.template_folder))

# Initialize model as None
model = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PATH: Set the path for Tesseract OCR - UNCOMMENT AND MODIFY FOR WINDOWS
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Windows path
# pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # Linux path
# pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"  # macOS path

# Error handling decorator
def handle_errors(f):
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
    """Initialize the application once before first request"""
    if not hasattr(app, 'initialized'):
        global model
        if model is None:
            try:
                # PATH: Model file path - ensure best.pt exists in your project directory
                model_path = "./../best.pt"  # PATH: Modify this path as needed
                if os.path.exists(model_path):
                    model = YOLO(model_path)
                    logger.info("YOLO model loaded successfully")
                else:
                    logger.error(f"Model file not found at {model_path}")
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {str(e)}")
                raise  # Re-raise the exception to fail fast
        app.initialized = True

# Create upload directory if it doesn't exist
def ensure_upload_directory():
    """Ensure upload directory exists"""
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        logger.info(f"Created upload directory: {app.config['UPLOAD_FOLDER']}")

# Improved file validation
def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Preprocess image for OCR with better error handling
def preprocess_image(image_path):
    """Preprocess image for better OCR results"""
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not read image file")
        
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
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise

# Extract text from the image with better error handling
def extract_text(image_path):
    """Extract text from image using OCR"""
    try:
        processed_image = preprocess_image(image_path)
        # PATH: Temporary processed image path
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.png')
        cv2.imwrite(temp_path, processed_image)
        
        text = pytesseract.image_to_string(processed_image, config='--psm 11')
        
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text: {str(e)}")
        return ""

# Split text into unique words
def split_into_unique_words(text):
    """Split text into unique words while preserving order"""
    if not text:
        return []
    
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    words = text.split()
    unique_words = list(OrderedDict.fromkeys(words))
    return unique_words

# Routes
@app.route("/")
def home():
    """Home page route"""
    return render_template("index.html")

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/scanner", methods=['GET', 'POST'])
@handle_errors
def scanner_page():
    """Scanner page route with improved error handling"""
    result = None
    error_message = None
    
    if request.method == 'POST':
        if 'imageInput' not in request.files:
            error_message = "No file uploaded"
        else:
            file = request.files['imageInput']
            if file.filename == '':
                error_message = "No file selected"
            elif not allowed_file(file.filename):
                error_message = "Invalid file type. Please upload an image file."
            else:
                try:
                    ensure_upload_directory()
                    filename = secure_filename(file.filename)
                    # Add timestamp to filename to avoid conflicts
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
                    filename = timestamp + filename
                    # PATH: File upload path
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    extracted_text = extract_text(file_path)
                    result = split_into_unique_words(extracted_text)
                    
                    # Clean up uploaded file after processing
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        
                except Exception as e:
                    error_message = f"Error processing image: {str(e)}"
    
    return render_template('scanner.html', result=result, error=error_message)

@app.route("/stores", methods=['GET', 'POST'])
@handle_errors
def stores_page():
    """Stores page route with improved error handling"""
    pharmacies = []
    error = None
    
    if request.method == 'POST':
        location = request.form.get('location', '').strip()
        if location:
            try:
                lat, lon = get_coordinates(location)
                if lat and lon:
                    pharmacies = fetch_nearby_medical_stores(lat, lon)
                    if not pharmacies:
                        error = "No pharmacies found nearby. Try a different location."
                else:
                    error = "Location not found. Please try a different search term."
            except Exception as e:
                error = "Error fetching pharmacy data. Please try again."
                logger.error(f"Error in stores search: {str(e)}")
        else:
            error = "Please enter a location."
    
    return render_template('stores.html', pharmacies=pharmacies, error=error)

@app.route("/contact")
def contact_page():
    """Contact page route"""
    return render_template("contact.html")

@app.route('/report', methods=['GET'])
def report_page():
    """Report page route"""
    return render_template("report.html")

# Utility functions with improved error handling
def get_coordinates(location):
    """Get coordinates from location name using OpenStreetMap"""
    try:
        geocode_url = f"https://nominatim.openstreetmap.org/search"
        params = {
            'q': location,
            'format': 'json',
            'limit': 1
        }
        headers = {'User-Agent': 'Mozilla/5.0 (MyPharmacyApp/1.0)'}
        
        response = requests.get(geocode_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data:
            result = data[0]
            return float(result["lat"]), float(result["lon"])
        return None, None
    except Exception as e:
        logger.error(f"Error getting coordinates: {str(e)}")
        return None, None

def fetch_nearby_medical_stores(lat, lon, radius=5000):
    """Fetch nearby medical stores using Overpass API"""
    try:
        query = f"""
            [out:json];
            (
                node["amenity"="pharmacy"](around:{radius},{lat},{lon});
                way["amenity"="pharmacy"](around:{radius},{lat},{lon});
                rel["amenity"="pharmacy"](around:{radius},{lat},{lon});
            );
            out center;
        """
        
        url = "https://overpass-api.de/api/interpreter"
        headers = {'User-Agent': 'Mozilla/5.0 (MyPharmacyApp/1.0)'}
        
        response = requests.post(url, data=query, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        pharmacies = []
        
        for elem in data.get("elements", []):
            name = elem.get("tags", {}).get("name", "Unnamed Pharmacy")
            
            # Handle different element types (node, way, relation)
            if elem.get("type") == "node":
                lat_coord = elem.get("lat")
                lon_coord = elem.get("lon")
            else:
                # For ways and relations, use center coordinates
                center = elem.get("center", {})
                lat_coord = center.get("lat")
                lon_coord = center.get("lon")
            
            if lat_coord and lon_coord:
                pharmacies.append({
                    "name": name,
                    "lat": lat_coord,
                    "lon": lon_coord,
                    "address": elem.get("tags", {}).get("addr:full", "Address not available")
                })
        
        return pharmacies
    except Exception as e:
        logger.error(f"Error fetching medical stores: {str(e)}")
        return []

# Ultrasound analysis configuration
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
    """Calculate NT measurement in millimeters"""
    return round(normalized_height * image_height * 0.1, 2)

# Improved PDF generation using ReportLab instead of WeasyPrint
def generate_pdf_report(result_data):
    """Generate PDF report using ReportLab (lighter than WeasyPrint)"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("Ultrasound Analysis Report", title_style))
        story.append(Spacer(1, 20))
        
        # Timestamp
        story.append(Paragraph(f"<b>Date:</b> {result_data.get('timestamp', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # NT Measurement
        story.append(Paragraph(f"<b>Nuchal Translucency (NT):</b> {result_data.get('nt', 'Not Detected')}", styles['Normal']))
        story.append(Paragraph(f"<b>Risk Assessment:</b> {result_data.get('risk', 'Unknown')}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Structures table
        structures = result_data.get('structures', {})
        if structures:
            story.append(Paragraph("<b>Detected Structures:</b>", styles['Heading2']))
            
            # Create table data
            table_data = [['Structure', 'Status']]
            for structure, status in structures.items():
                table_data.append([structure, status])
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 12))
        
        # Summary
        summary = result_data.get('summary', '')
        if summary:
            story.append(Paragraph("<b>Diagnostic Summary:</b>", styles['Heading2']))
            story.append(Paragraph(summary, styles['Normal']))
        
        # Add image if available
        filename = result_data.get('filename')
        if filename:
            # PATH: Image path for PDF
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(image_path):
                story.append(Spacer(1, 20))
                story.append(Paragraph("<b>Annotated Image:</b>", styles['Heading2']))
                story.append(Spacer(1, 12))
                
                # Add image to PDF (resize to fit page)
                img = ReportLabImage(image_path, width=4*inch, height=3*inch)
                story.append(img)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise


# all the functionality in analyze route added ---> YOLOv8 inference, structure detection, NT measurement, and risk scoring
# i should have used external infernece (if anyone wants to do, they can)

@app.route('/analyze', methods=['POST'])
@handle_errors
def analyze():
    """Analyze ultrasound image with improved error handling"""
    if model is None:
        return jsonify({'error': 'Model not loaded. Please try again later.'}), 500
    
    if 'image' not in request.files:
        return redirect(url_for('report_page'))

    file = request.files['image']
    if file.filename == '':
        return redirect(url_for('report_page'))

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        ensure_upload_directory()
        filename = secure_filename(file.filename)
        # Add unique identifier to prevent conflicts
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        # PATH: File path for analysis
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        # Read and process image
        image_bgr = cv2.imread(filepath)
        if image_bgr is None:
            raise ValueError("Could not read uploaded image")
        
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        image_height, image_width = image_rgb.shape[:2]

        # Run YOLO inference
        results = model.predict(image_rgb)[0]
        boxes = results.boxes

        detected_structures = set()
        nt_measurement_mm = None

        # Process detections
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                class_name = key_structures.get(cls_id, f"Unknown ({cls_id})")

                logger.info(f"Detected {class_name} with confidence {conf:.2f}")
                detected_structures.add(class_name)

                # Draw bounding box
                cv2.rectangle(image_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image_bgr, f"{class_name} ({conf:.2f})", (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Calculate NT measurement
                if class_name.lower() == "nt":
                    box_height = y2 - y1
                    nt_measurement_mm = calculate_nt_mm(box_height / image_height, image_height)

        # Determine risk level
        risk = "High" if nt_measurement_mm and nt_measurement_mm > 3.0 else "Low" if nt_measurement_mm else "Unknown"

        # Save annotated image
        annotated_filename = f"annotated_{unique_filename}"
        # PATH: Annotated image path
        annotated_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
        cv2.imwrite(annotated_path, image_bgr)

        # Clean up original uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)

        # Prepare results
        structure_status = {
            name: ("Detected" if name in detected_structures else "Not Detected")
            for name in key_structure_names
        }

        # Generate diagnostic summary
        diagnostic_summary = generate_diagnostic_summary(nt_measurement_mm, detected_structures, risk)

        result_data = {
            "filename": annotated_filename,
            "nt": f"{nt_measurement_mm} mm" if nt_measurement_mm else "Not Detected",
            "risk": risk,
            "structures": structure_status,
            "summary": diagnostic_summary,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save to session
        session['result_data'] = json.dumps(result_data)
        return render_template("Genrepo.html", results=result_data)

    except Exception as e:
        logger.error(f"Error in analyze route: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

def generate_diagnostic_summary(nt_measurement_mm, detected_structures, risk):
    """Generate diagnostic summary based on analysis results"""
    summary_parts = []
    
    if nt_measurement_mm:
        summary_parts.append(f"Nuchal Translucency (NT) measured {nt_measurement_mm} mm.")
        if risk == "High":
            summary_parts.append("This measurement is above the normal range and may indicate increased risk for chromosomal abnormalities.")
        else:
            summary_parts.append("This measurement is within normal limits.")
    else:
        summary_parts.append("Nuchal Translucency (NT) was not detected in this image.")

    if "Nasal Bone" in detected_structures:
        summary_parts.append("Nasal bone is present, which is a positive finding.")
    else:
        summary_parts.append("Nasal bone was not detected, which could be an additional marker for assessment.")

    if "Cisterna Magna" in detected_structures:
        summary_parts.append("Cisterna Magna is visible and appears normal.")
    else:
        summary_parts.append("Cisterna Magna not clearly visualized. Further imaging may be recommended.")

    return " ".join(summary_parts)

@app.route('/download_pdf')
@handle_errors
def download_pdf():
    """Download PDF report using ReportLab"""
    try:
        result_data = json.loads(session.get('result_data', '{}'))
        if not result_data:
            return jsonify({'error': 'No analysis data available'}), 400
        
        pdf_buffer = generate_pdf_report(result_data)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"ultrasound_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({'error': 'Failed to generate PDF report'}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413


if __name__ == '__main__':
    ensure_upload_directory()
    # For production, set debug=False and use a proper WSGI server
    app.run(debug=True, host='0.0.0.0', port=5000)
