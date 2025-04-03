from flask import Flask, render_template, request, redirect, url_for
import pytesseract
import cv2
import os
import numpy as np
import re
from werkzeug.utils import secure_filename
from collections import OrderedDict

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def preprocess_image(image_path):
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 🔥 Increase contrast for better OCR detection
    alpha = 1.8  # Contrast control (1.0-3.0)
    beta = 20    # Brightness control (0-100)
    contrast = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)

    # 🧼 Apply Gaussian Blur to remove noise while keeping text sharp
    blur = cv2.GaussianBlur(contrast, (3, 3), 0)

    # 🎯 Adaptive Thresholding to binarize the image
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # 🔄 Morphological Operations to preserve word spacing
    kernel = np.ones((2,2), np.uint8)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # 📸 Save the processed image for debugging
    cv2.imwrite("processed_debug.png", processed)

    return processed
   

def extract_text(image_path):
    processed_image = preprocess_image(image_path)
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed.png')
    cv2.imwrite(temp_path, processed_image)  
    text = pytesseract.image_to_string(processed_image, config='--psm 11')
    return text.strip()


def split_into_unique_words(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    words = text.split()
    unique_words=list(OrderedDict.fromkeys(words))
    print("\nCleaned Unique Words:\n", unique_words)

    return unique_words


@app.route('/', methods=['GET', 'POST'])
def upload_file():
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
            listDisplayed=split_into_unique_words(extracted_text)
            return render_template('index.html',result=listDisplayed)
    

if __name__ == '__main__':
    app.run(debug=True)