from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, session, flash
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


# Initialize REPORT_MODULE_AVAILABLE first
REPORT_MODULE_AVAILABLE = False

# Import your custom report generation functions
try:
    from report import (
        enhanced_analyze_ultrasound_image, 
        save_pdf_report, 
        generate_summary_json,
        MedicalReportGenerator
    )
    REPORT_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: report.py module not found or has issues: {e}")
    REPORT_MODULE_AVAILABLE = False

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract-ocr"

app = Flask(__name__, template_folder="./../templates/", static_folder="./../static")
app.has_run_before = False
app.secret_key = 'your_secret_key_here'  # TODO: Change this to a secure random key in production
#app.config['UPLOAD_FOLDER'] = './../src/static/uploads'  # PATH: Configure upload directory
app.config['UPLOAD_FOLDER'] = os.path.abspath('./../static/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['STATIC_FOLDER'] = os.path.abspath('./../static')

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

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# Routes
@app.route("/")
def home():
    """Home page route"""
    return render_template("index.html")

@app.route('/')
def index():
    return render_template('index.html')

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
    """Contact page route"""
    return render_template("contact.html")



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
# Debug route to check system status
@app.route('/debug')
def debug_status():
    """Debug route to check system status"""
    try:
        status = {
            'report_module_available': REPORT_MODULE_AVAILABLE,
            'model_loaded': model is not None,
            'upload_folder': app.config['UPLOAD_FOLDER'],
            'upload_folder_exists': os.path.exists(app.config['UPLOAD_FOLDER']),
            'template_folder': app.template_folder,
            'static_folder': app.static_folder,
            'available_templates': [],
            'recent_uploads': []
        }
        
        # Check available templates
        if os.path.exists(app.template_folder):
            status['available_templates'] = [f for f in os.listdir(app.template_folder) if f.endswith('.html')]
        
        # Check recent uploads
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            files = os.listdir(app.config['UPLOAD_FOLDER'])
            status['recent_uploads'] = sorted(files, key=lambda x: os.path.getctime(os.path.join(app.config['UPLOAD_FOLDER'], x)), reverse=True)[:5]
        
        # Check session data
        status['session_data'] = {
            'has_analysis_results': 'analysis_results' in session,
            'has_uploaded_filename': 'uploaded_filename' in session
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/report', methods=['GET', 'POST'])
@handle_errors
def report_page():
    """Enhanced report page with integrated analysis"""
    if request.method == 'POST':
        try:
            # Debug logging
            logger.info(f"POST request received to /report")
            logger.info(f"Files in request: {list(request.files.keys())}")
            logger.info(f"Form data: {dict(request.form)}")
            
            if 'ultrasoundImage' not in request.files:
                logger.warning("No 'ultrasoundImage' key found in request.files")
                flash('No file selected', 'error')
                return render_template('report.html')
            
            file = request.files['ultrasoundImage']
            logger.info(f"File received: {file.filename}, size: {file.content_length if hasattr(file, 'content_length') else 'unknown'}")
            
            if file.filename == '':
                logger.warning("Empty filename received")
                flash('No file selected', 'error')
                return render_template('report.html')
            
            if not allowed_file(file.filename):
                logger.warning(f"File type not allowed: {file.filename}")
                flash('Invalid file type. Please upload an image file.', 'error')
                return render_template('report.html')
            
            ensure_upload_directory()
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            logger.info(f"Saving file to: {filepath}")
            file.save(filepath)
            
            # Verify file was saved
            if not os.path.exists(filepath):
                logger.error(f"File was not saved to {filepath}")
                flash('Error saving file', 'error')
                return render_template('report.html')
            
            file_size = os.path.getsize(filepath)
            logger.info(f"File saved successfully, size: {file_size} bytes")
            
            # Check if we have the enhanced analysis capability
            logger.info(f"REPORT_MODULE_AVAILABLE: {REPORT_MODULE_AVAILABLE}")
            logger.info(f"Model available: {model is not None}")
            
            # Use enhanced analysis if report module is available
            if REPORT_MODULE_AVAILABLE and model is not None:
                logger.info("Using enhanced analysis")
                try:
                    result = enhanced_analyze_ultrasound_image(filepath, model, app.config)
                    logger.info(f"Enhanced analysis result: {result}")
                    
                    if result.get('success'):
                        # Store results in session for later access
                        session['analysis_results'] = result
                        session['uploaded_filename'] = unique_filename
                        
                        logger.info("Analysis successful, rendering results")
                        # Render results using results.html template
                        return render_template('results.html', results=result)
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        logger.error(f"Enhanced analysis failed: {error_msg}")
                        flash(f"Analysis failed: {error_msg}", 'error')
                        return render_template('report.html')
                except Exception as e:
                    logger.error(f"Exception in enhanced analysis: {str(e)}")
                    flash(f"Analysis error: {str(e)}", 'error')
                    return render_template('report.html')
            else:
                # Fallback to basic analysis if report module not available
                logger.info("Using basic analysis fallback")
                return redirect(url_for('analyze_basic', filename=unique_filename))
                
        except Exception as e:
            logger.error(f"Error in report route: {str(e)}", exc_info=True)
            try:
                flash(f'Error processing file: {str(e)}', 'error')
            except Exception:
                # If flash fails, log the error instead
                logger.error(f"Flash function failed, original error: {str(e)}")
            return render_template('report.html')
    
    logger.info("GET request to /report, rendering form")
    return render_template('report.html')

@app.route('/analyze_basic/<filename>')
def analyze_basic(filename):
    """Basic analysis fallback when report module is not available"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"Starting basic analysis for file: {filepath}")
        
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            try:
                flash('File not found', 'error')
            except Exception:
                logger.error("File not found and flash function unavailable")
            return redirect(url_for('report_page'))
        
        # Try to get basic image information
        try:
            from PIL import Image
            with Image.open(filepath) as img:
                width, height = img.size
                image_format = img.format
                image_mode = img.mode
                logger.info(f"Image info: {width}x{height}, format: {image_format}, mode: {image_mode}")
        except Exception as e:
            logger.warning(f"Could not get image info: {e}")
            width, height = "Unknown", "Unknown"
            image_format = "Unknown"
            image_mode = "Unknown"
        
        # Enhanced basic analysis result
        basic_result = {
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'image_info': {
                'width': width,
                'height': height,
                'format': image_format,
                'mode': image_mode,
                'file_size': os.path.getsize(filepath) if os.path.exists(filepath) else 0
            },
            'analysis': {
                'status': 'Basic analysis completed',
                'message': 'Image uploaded and processed successfully',
                'note': 'Advanced AI analysis features require the report module to be properly configured',
                'recommendations': [
                    'Ensure the report.py module is available for enhanced analysis',
                    'Check that the YOLO model file (best.pt) is in the correct location',
                    'Verify all required dependencies are installed'
                ]
            },
            'report_available': True,
            'pdf_report': None  # Will be generated on demand
        }
        
        logger.info("Basic analysis completed successfully")
        session['analysis_results'] = basic_result
        session['uploaded_filename'] = filename
        
        return render_template('results.html', results=basic_result)
        
    except Exception as e:
        logger.error(f"Error in basic analysis: {str(e)}", exc_info=True)
        try:
            flash('Analysis failed', 'error')
        except Exception:
            logger.error("Analysis failed and flash function unavailable")
        return redirect(url_for('report_page'))

@app.route('/download_report')
def download_report():
    """Download generated report"""
    try:

        results = session.get('analysis_results')
        if not results:
            try:
                flash('No analysis results available', 'error')
            except Exception:
                logger.error("No analysis results available and flash function unavailable")
            return redirect(url_for('report_page'))
        
        if REPORT_MODULE_AVAILABLE:
            # Use the enhanced PDF generation from report module
            pdf_path = results.get('pdf_report')
            if pdf_path and os.path.exists(pdf_path):
                return send_file(
                    pdf_path,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f"ultrasound_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                )
        
        # Fallback: generate basic PDF using ReportLab
        return generate_basic_pdf_report(results)
        
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        try:
            flash('Failed to generate report', 'error')
        except Exception:
            logger.error("Failed to generate report and flash function unavailable")
        return redirect(url_for('report_page'))

def generate_basic_pdf_report(results):
    """Generate basic PDF report using ReportLab"""
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
            alignment=1
        )
        story.append(Paragraph("Ultrasound Analysis Report", title_style))
        story.append(Spacer(1, 20))
        
        # Timestamp
        story.append(Paragraph(f"<b>Date:</b> {results.get('timestamp', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Analysis details
        analysis = results.get('analysis', {})
        for key, value in analysis.items():
            story.append(Paragraph(f"<b>{key.title()}:</b> {value}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        # Add note about enhanced features
        if not REPORT_MODULE_AVAILABLE:
            story.append(Spacer(1, 20))
            story.append(Paragraph("<b>Note:</b> Enhanced analysis features are not available. Please ensure the report module is properly configured.", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"basic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
    except Exception as e:
        logger.error(f"Error generating basic PDF: {str(e)}")
        raise

@app.route('/generate_report')
def generate_report():                                                                   
    """Generate comprehensive report using Genrepo.html template if available"""         
    try:                                                                             
        analysis_results = session.get('analysis_results')
        summary = session.get('summary')
        annotated_filename = session.get('annotated_image')                                       
        pdf_filename = session.get('pdf_filename', 'report.pdf')
        if not analysis_results:                                                                  
            flash('No analysis results available', 'error')                              
            return redirect(url_for('report_page'))
        print("✅ generate_report reached")
        print("📌 analysis_results keys:", analysis_results.keys())
        print("📌 summary keys:", summary.keys() if summary else "None")
        print("📌 annotated_image:", annotated_filename)
        print("📌 pdf_filename:", pdf_filename)                                                                                                  

        annotated_image = session.get('annotated_image')
        annotated_image_url = session.get('annotated_image_url')
                    
        #annotated_image_url = url_for('static', filename=f'uploads/{annotated_image}') if annotated_image else None
        pdf_filename = os.path.basename(session.get('pdf_report', 'report.pdf'))
        # annotated_image_url = None
        # if annotated_image:
        #     annotated_image_url = url_for('static', filename=f'predictions/{annotated_image}')
        #annotated_image_url = f"/static/uploads/{annotated_filename}" if annotated_filename else None
        print(f"✅ annotated_image = {annotated_image}")
        print(f"✅ annotated_image_url = {annotated_image_url}")
                            
        return render_template("results.html",                                           
            analysis_results=analysis_results,
            annotated_image=annotated_image,                                
            annotated_image_url=annotated_image_url,     
            summary=summary,
            pdf_filename=session.get('pdf_filename'),
            results={"success":True}                   
        )
    except Exception as e:
        import traceback
        print("❌ Exception in generate_report:", str(e))
        traceback.print_exc()  # This gives you full context
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('report_page'))
# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html') if os.path.exists(os.path.join(app.template_folder, '404.html')) else "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html') if os.path.exists(os.path.join(app.template_folder, '500.html')) else "Internal server error", 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413


# Legacy analyze route for backward compatibility
@app.route('/analyze', methods=['POST'])
@handle_errors
def analyze():
    if 'image' not in request.files:
        flash("No image file provided.", 'error')
        return redirect(url_for('report_page'))

    file = request.files['image']
    if file.filename == '':
        flash("No selected image.", 'error')
        return redirect(url_for('report_page'))

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        result = enhanced_analyze_ultrasound_image(filepath, model, app.config)

        if result.get('success'):
            print("Analysis successful — redirecting to generate_report")

            analysis_results = result['analysis_results']
            analysis_results['detected_structures'] = list(analysis_results.get('detected_structures', []))

            session['analysis_results'] = analysis_results
            session['uploaded_filename'] = filename
            session['summary'] = generate_summary_json(analysis_results)

            # ✅ Corrected line
            #session['annotated_image'] = os.path.basename(annotated_image_path)
            session['annotated_image'] = os.path.basename(result.get('annotated_image_path',''))
            session['annotated_image_url'] = result.get('annotated_image_url')
            # ✅ Store PDF path too
            pdf_path = save_pdf_report(result['pdf_report'], f"report_{filename}.pdf", app.config['UPLOAD_FOLDER'])
            if pdf_path:
                session['pdf_filename'] = f"report_{filename}.pdf"
    
            return redirect(url_for('generate_report'))

        else:
            flash(f"Analysis failed: {result.get('error', 'Unknown error')}", 'error')
            return redirect(url_for('report_page'))

    flash("Invalid image file.", 'error')
    return redirect(url_for('report_page'))


if __name__ == '__main__':
    # Ensure upload directory exists
    ensure_upload_directory()
    
    print("="*50)
    print("Medical Imaging Flask App Starting...")
    print("="*50)
    print(f"Report module available: {REPORT_MODULE_AVAILABLE}")
    print(f"Model loaded: {model is not None}")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Upload folder exists: {os.path.exists(app.config['UPLOAD_FOLDER'])}")
    print(f"Template folder: {app.template_folder}")
    print(f"Template folder exists: {os.path.exists(app.template_folder)}")
    print(f"Static folder: {app.static_folder}")
    
    # Check for required templates
    required_templates = ['index.html', 'report.html', 'results.html', 'scanner.html', 'stores.html', 'contact.html']
    missing_templates = []
    
    for template in required_templates:
        template_path = os.path.join(app.template_folder, template)
        if not os.path.exists(template_path):
            missing_templates.append(template)
    
    if missing_templates:
        print(f"WARNING: Missing templates: {missing_templates}")
    else:
        print("All required templates found")
    
    # Show available routes
    print("\nAvailable routes:")
    for rule in app.url_map.iter_rules():
        methods = ', '.join(rule.methods) if rule.methods else 'GET'
        print(f"  {rule.rule} -> {rule.endpoint} [{methods}]")
    
    print("\nDebug route available at: http://localhost:5000/debug")
    print("="*50)
    
    app.run( host='127.0.0.1', port=5000, debug=True)

   
