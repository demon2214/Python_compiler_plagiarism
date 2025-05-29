# 🛡️ Code Integrity & Plagiarism Detection Suite

A scalable, full-stack platform built with a secure **Python Flask** backend and a modern **Next.js** frontend. Designed to analyze code similarity, run code in isolation, and streamline workflows for students and administrators.

---

## 🗂️ Project Structure

```
flask_modular_app/
├── app/
│   ├── globals.css
│   ├── layout.tsx
│   ├── page.tsx
│
├── components/
│   ├── ui/
│   └── theme-provider.tsx
│
├── hooks/
│   ├── use-mobile.tsx
│   └── use-toast.ts
│
├── lib/
│   └── utils.ts
│
├── public/
│   ├── placeholder-logo.png
│   ├── placeholder-logo.svg
│   ├── placeholder-user.jpg
│   ├── placeholder.jpg
│   └── placeholder.svg
│
├── static/
│   ├── css/
│   └── js/
│
├── styles/
│   └── globals.css
│
├── templates/
│   ├── admin_dashboard.html
│   ├── base.html
│   ├── compare_codes.html
│   ├── error.html
│   ├── login.html
│   ├── manage_questions.html
│   ├── manage_users.html
│   ├── my_submissions.html
│   ├── plagiarism_check.html
│   ├── question_detail.html
│   └── student_dashboard.html
│
├── .gitignore
├── admin.py
├── app.py
├── auth.py
├── code_executor.py
├── components.json
├── models.py
├── next.config.mjs
├── package.json
├── plagiarism_detector.py
├── plagiarism.py
├── pnpm-lock.yaml
├── postcss.config.mjs
├── requirements.txt
├── setup_instructions.md
├── student.py
├── tailwind.config.ts
└── tsconfig.json
```

---

## ✨ Key Features

- 🧬 **Smart Code Similarity Analysis** (via TF-IDF & AST parsing)  
- 🔐 **Role-Based Access** for Admins and Students  
- 📈 **Interactive Dashboards** for Submissions & Reports  
- 🧪 **Secure Code Execution** within Sandboxed Environments  
- 🎨 **Composable UI** built with Tailwind CSS & ShadCN  
- 🧭 **Modern Routing** using Next.js 14 App Directory  

---

## 🧰 Tech Stack

| Layer         | Stack                                      |
|---------------|---------------------------------------------|
| 🖼️ Frontend    | Next.js 14, Tailwind CSS, TypeScript        |
| 🔧 Backend     | Flask, Python, SQLAlchemy                   |
| 🗄️ Database    | SQLite / MySQL (configurable)               |
| 🛠️ Tools       | PNPM, ShadCN UI, Chart.js                   |

---

## 🚀 Quickstart Guide

### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
```

```bash
# Install dependencies
pip install -r requirements.txt
```

```bash
# Start the Flask server
python app.py
```

### Frontend Setup
```bash
# Using PNPM
pnpm install
pnpm dev
```

📘 *Refer to `setup_instructions.md` for environment configs and database initialization..*
