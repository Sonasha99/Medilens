from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import os

# ✅ Correct import name based on your actual function
from inference import yolo_inference_function

app = Flask(__name__)

# ✅ Upload folder and allowed file types
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# ✅ Check if uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ Home page
@app.route('/')
def index():
    return render_template('index.html')

# ✅ Scanner page
@app.route('/scanner')
def scanner_page():
    return render_template('scanner.html')

@app.route('/stores')
def stores_page():
    return render_template('stores.html')  # ← make sure stores.html exists
# Contact page route
@app.route('/contact')
def contact_page():
    return render_template('contact.html')  # Ensure you have a 'contact.html' template


# ✅ Analyze route
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # ✅ Run YOLOv8 model
        image_path, labels = yolo_inference_function(file_path)

        return render_template('report.html', image_path=image_path, labels=labels)

    return redirect(request.url)

# ✅ Start the app
if __name__ == '__main__':
    app.run(debug=True)
