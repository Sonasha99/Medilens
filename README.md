Perfect! Here's the updated `README.md` with a clear **Frontend / Backend folder structure section** so others can easily understand which files belong where:

---

```markdown
# MediLens 2

MediLens 2 is a healthcare-focused web application designed to streamline medical tasks like prescription scanning, medicine lookup, and basic medical record support.

## 🚀 Features

- 🧾 Upload and scan medical prescriptions
- 🔍 Extract and identify medicine names using OCR
- 💊 Search and display medicine information
- 📁 (Optional) Manage basic health records
- 📲 Responsive UI for mobile and desktop

## 🛠️ Tech Stack

- **Frontend:** React.js, Tailwind CSS
- **Backend:** Node.js, Express.js
- **OCR/ML Integration:** Tesseract.js or relevant library
- **Database:** MongoDB (if included)
- **Deployment:** Render / Vercel / Netlify

---
## file location 
1.app.py, detect.py, inference.py → This is a Flask (Python) backend project.
2.package.json → Suggests there might be some Node.js/JavaScript frontend or UI dependency, but it's in the same folder as the Python code.
3.requirements.txt → Confirms this is primarily a Python project.
4.vercel.json, render.yaml → Deployment configs (Vercel likely for frontend/API, Render for backend).


> 📌 Note: If both frontend and backend are in the same repo, you can run each part separately using `npm install` and `npm start` inside each folder.

---

## 🧑‍💻 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/taneesha1/medilens-2.git
cd medilens-2
````

### 2. Start Backend

```bash
cd backend
npm install
npm start
```

### 3. Start Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm start
```

---

## 📸 Screenshots

*Place UI screenshots here (optional).*

---



## 📄 License

MIT License. See [LICENSE](LICENSE) for more details.

```

---

Would you like me to check the repo structure and tailor this section more precisely to the actual folders like `src`, `api`, or `controllers` if they exist?
```
