
# 🩺 MediLens 2

MediLens 2 is an AI-powered healthcare assistant that helps users scan prescriptions, find nearby medical stores, and access essential health tools in one place.

---

## ✨ Features

- 🧾 Upload & scan handwritten prescriptions using AI
- 🔍 Extract & identify medicines from scanned images
- 💊 Locate nearby pharmacies using live maps
- 📊 Generate basic medical reports from ultrasound
- 📱 Mobile-responsive and user-friendly design

---

## 🛠️ Tech Stack

| Layer       | Technologies Used                        |
|------------|-------------------------------------------|
| **Frontend**  | HTML, CSS, Jinja2 (Flask Templates)       |
| **Backend**   | Python (Flask), OpenStreetMap + Leaflet.js |
| **ML/OCR**    | Custom model with Tesseract / inference.py |
| **Deployment**| Render (backend) + Vercel (frontend static files) |

---

## 🗂 Folder Structure

| File/Folder              | Description                              |
|--------------------------|------------------------------------------|
| `app.py`                 | Main Flask backend application           |
| `detect.py` / `inference.py` | ML and OCR processing logic              |
| `templates/`             | HTML (Jinja2) files served via Flask     |
| `static/`                | CSS, JS, icons, and frontend assets      |
| `render.yaml`            | Backend deployment config (Render)       |
| `vercel.json`            | (Optional) Frontend deploy config (Vercel)|
| `requirements.txt`       | Python dependencies                      |

---

## 🚀 Live Deployment - https://medilens-i8kf.onrender.com/

> 💡 If you’ve deployed the full app on Render alone (frontend + backend via Flask), just use the backend link.

---

## 🧑‍💻 How to Run Locally

### 1. Clone the repo

```bash
git clone https://github.com/taneesha1/medilens-2.git
cd medilens-2
````

---

### 2. Install backend dependencies

```bash
pip install -r requirements.txt
import pytesseract
pip install opencv-python
pip install reportlab
pip install ultralytics

```

---

### 3. Start the Flask server

```bash
 cd backend
python app2.py
```

🌐 Visit `http://127.0.0.1:5000` in your browser.

---

## 📦 Deployment Guide

### Deploy on Render 

1. Create a [Render](https://render.com) account
2. Connect your GitHub repo
3. Set:

   * **Build Command:** `pip install -r requirements.txt`
   * **Branch : ** Backend
   * **Start Command:** `python app2.py`
   * **Environment:** `Python`


## 📸 Screenshots
*Home Page*
![image](https://github.com/user-attachments/assets/32a4ca0a-8455-4448-a58a-4a3fdf7d2e07)
*Prescription Scanner page*
![image](https://github.com/user-attachments/assets/eef8eb28-029d-4174-b84d-888336da28be)



