# 🔍 Code Similarity Checker

A web-based application that helps detect code plagiarism by comparing uploaded code files for similarity. It provides interfaces for both **students** and **administrators** to manage submissions and view similarity results.

---

## ✨ Features

- 🔐 **User Authentication**  
  Secure login for students and administrators.

- 📤 **Code Uploading**  
  Students can upload their code for similarity analysis.

- 🧠 **Similarity Detection**  
  Compares uploaded code files using custom-built algorithms.

- 🛠️ **Admin Dashboard**  
  View all submissions, manage users, and check similarity reports.

- 🎨 **Responsive Interface**  
  Built using HTML, CSS, and JavaScript for a clean user experience.

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask , XAMPP
- **Frontend:** HTML, CSS, JavaScript  
- **Database:** SQLite  
- **Similarity Engine:** Custom logic in `similarity_checker.py`

---

## 📁 Folder Structure

code_similarity_checker/
├── app.py # Main application entry point
├── database.py # Handles DB operations
├── models.py # Database models
├── similarity_checker.py # Core similarity logic
├── static/
│ ├── css/style.css # Stylesheet
│ └── js/script.js # JavaScript code
├── templates/
│ ├── login.html # Login page
│ ├── student.html # Student dashboard
│ ├── admin.html # Admin dashboard
│ └── results.html # Similarity results
├── requirements.txt # Python dependencies
└── readme.md # Project documentation

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/3genei/code_similarity_checker.git
cd code_similarity_checker
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```


