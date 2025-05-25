# Code Similarity Checker

A web-based application that allows users (students and admins) to check the similarity of code files to detect possible plagiarism using Python.

## Features

- **User Login System:** Students and Admins can log in via a dedicated interface.
- **Code Upload:** Students can upload code for similarity checking.
- **Similarity Detection:** Detects code similarity using custom algorithms.
- **Admin Panel:** Admin can view all uploaded submissions and their similarity reports.
- **Responsive UI:** Built using HTML, CSS, and JavaScript.

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (via `database.py`)
- **Code Processing:** Custom similarity algorithms (`similarity_checker.py`)

## Folder Structure

code_similarity_checker/
├── app.py # Main application entry
├── database.py # Handles database operations
├── models.py # Defines database models
├── similarity_checker.py # Contains similarity comparison logic
├── static/
│ ├── css/style.css # Stylesheet
│ └── js/script.js # JavaScript
├── templates/
│ ├── login.html
│ ├── student.html
│ ├── admin.html
│ └── results.html
├── requirements.txt # Python dependencies
└── readme.md # Project README

###____END_____##
