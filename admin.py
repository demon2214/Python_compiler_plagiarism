from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from auth import admin_required
from models import User, Question, Submission, ExamSession
from plagiarism_detector import calculate_similarity
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    submissions = Submission.get_all()
    users = User.get_all()
    questions = Question.get_all()
    
    # Calculate statistics
    total_submissions = len(submissions)
    total_users = len([u for u in users if u['role'] == 'student'])
    total_questions = len(questions)
    high_similarity = len([s for s in submissions if s['similarity_score'] > 70])
    
    # Calculate test success rate
    successful_submissions = len([s for s in submissions if s.get('passed_tests', 0) == s.get('total_tests', 1)])
    success_rate = (successful_submissions / total_submissions * 100) if total_submissions > 0 else 0
    
    stats = {
        'total_submissions': total_submissions,
        'total_users': total_users,
        'total_questions': total_questions,
        'high_similarity': high_similarity,
        'success_rate': round(success_rate, 1)
    }
    
    return render_template('admin_dashboard.html', 
                         submissions=submissions[:10], 
                         stats=stats)

@admin_bp.route('/users')
@admin_required
def manage_users():
    users = User.get_all()
    # Convert Row objects to dictionaries to avoid JSON serialization issues
    users_list = []
    for user in users:
        users_list.append({
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'created_at': user['created_at']
        })
    return render_template('manage_users.html', users=users_list)

@admin_bp.route('/users/add', methods=['POST'])
@admin_required
def add_user():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    
    if User.create(username, password, role):
        flash(f'User {username} created successfully', 'success')
    else:
        flash('Username already exists', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/delete/<int:user_id>')
@admin_required
def delete_user(user_id):
    User.delete(user_id)
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/questions')
@admin_required
def manage_questions():
    questions = Question.get_all()
    # Convert Row objects to dictionaries
    questions_list = []
    for question in questions:
        questions_list.append({
            'id': question['id'],
            'title': question['title'],
            'description': question['description'],
            'difficulty': question['difficulty'],
            'function_name': question['function_name'],
            'test_cases': question['test_cases'],
            'example_code': question['example_code'],
            'created_at': question['created_at']
        })
    return render_template('manage_questions.html', questions=questions_list)

@admin_bp.route('/questions/add', methods=['POST'])
@admin_required
def add_question():
    title = request.form['title']
    description = request.form['description']
    difficulty = request.form['difficulty']
    function_name = request.form['function_name']
    example_code = request.form['example_code']
    
    # Parse test cases from JSON
    try:
        test_cases = json.loads(request.form['test_cases'])
    except json.JSONDecodeError:
        flash('Invalid test cases JSON format', 'error')
        return redirect(url_for('admin.manage_questions'))
    
    Question.create(title, description, difficulty, function_name, test_cases, example_code)
    flash('Question added successfully', 'success')
    return redirect(url_for('admin.manage_questions'))

@admin_bp.route('/questions/delete/<int:question_id>')
@admin_required
def delete_question(question_id):
    Question.delete(question_id)
    flash('Question deleted successfully', 'success')
    return redirect(url_for('admin.manage_questions'))

@admin_bp.route('/exam_monitoring')
@admin_required
def exam_monitoring():
    """View exam session monitoring data"""
    connection = get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect(url_for('admin.dashboard'))
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            SELECT es.*, u.username, q.title as question_title
            FROM exam_sessions es
            JOIN users u ON es.user_id = u.id
            JOIN questions q ON es.question_id = q.id
            ORDER BY es.session_start DESC
            LIMIT 50
        ''')
        sessions = cursor.fetchall()
        
        return render_template('exam_monitoring.html', sessions=sessions)
    except Exception as e:
        flash(f'Error fetching exam sessions: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))
    finally:
        cursor.close()
        connection.close()

@admin_bp.route('/users/export')
@admin_required
def export_users():
    """Export users as JSON for AJAX requests"""
    users = User.get_all()
    users_list = []
    for user in users:
        users_list.append({
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'created_at': user['created_at']
        })
    return jsonify(users_list)
