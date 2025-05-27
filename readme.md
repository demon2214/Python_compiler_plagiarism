🔐 Code Similarity & Plagiarism Detection Platform
A modular full-stack platform with Python Flask backend and modern Next.js frontend to securely detect code plagiarism, execute code, and manage student/admin workflows.

📦 Project Structure

flask_modular_app/
├── app.py                       # Flask backend entry
├── plagiarism_detector.py       # Core similarity logic
├── code_executor.py             # Code execution engine
├── auth.py, admin.py, student.py# Role-specific modules
├── models.py                    # SQLAlchemy models
├── app/                         # Next.js frontend app
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/                  # UI Components
│   └── ui/                      # Reusable Tailwind components
├── requirements.txt             # Flask dependencies
├── package.json / pnpm-lock.yaml# Frontend dependencies
├── tailwind.config.ts / postcss.config.mjs
└── setup_instructions.md        # Local setup help




✨ Features

  🧠 AI-based Code Similarity Detection (TF-IDF + AST)

  🔐 Admin & Student Login Flows

  📊 Visual Results Dashboard

  🖥️ Code Execution in Sandboxed Environment

  🎨 Modular UI with Tailwind CSS + ShadCN UI

  ⚙️ Next.js 14 App Directory Routing


⚙️ Technologies Used

Layer	Stack
  🎯 Frontend	Next.js 14, Tailwind CSS, TypeScript
  🧠  Backend	Flask, Python, SQLAlchemy
  💽 Database	SQLite / MySQL (configurable)
  📦 Tools	PNPM, ShadCN UI, Chart.js



🚀 Setup Guide
Backend

bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Run Flask server
python app.py
Frontend

bash
# Using pnpm
pnpm install
pnpm dev


📘 Refer setup_instructions.md for environment variables and DB setup.
