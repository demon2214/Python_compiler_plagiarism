# Coding Test Platform Setup Instructions

## Directory Structure
Create the following directory structure:

\`\`\`
coding-test-platform/
├── app.py
├── models.py
├── auth.py
├── admin.py
├── student.py
├── plagiarism.py
├── plagiarism_detector.py
├── code_executor.py
├── requirements.txt
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── templates/
    ├── base.html
    ├── login.html
    ├── admin_dashboard.html
    ├── student_dashboard.html
    ├── question_detail.html
    ├── plagiarism_check.html
    ├── compare_codes.html
    ├── manage_users.html
    ├── manage_questions.html
    ├── my_submissions.html
    └── error.html
\`\`\`

## Installation Steps

1. **Create the main directory:**
   ```bash
   mkdir coding-test-platform
   cd coding-test-platform
