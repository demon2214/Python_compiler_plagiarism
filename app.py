from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import init_db, get_db_connection
from auth import auth_bp
from admin import admin_bp
from student import student_bp
from plagiarism import plagiarism_bp
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(plagiarism_bp, url_prefix='/plagiarism')

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('role') == 'admin':
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('student.dashboard'))

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
