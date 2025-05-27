🔐 Code Similarity & Plagiarism Detection Platform
A modular full-stack platform with Python Flask backend and modern Next.js frontend to securely detect code plagiarism, execute code, and manage student/admin workflows.

📦 Project Structure

<details> <summary>Click to expand</summary>
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
</details>



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
