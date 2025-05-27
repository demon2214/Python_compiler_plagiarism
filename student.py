from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from auth import login_required
from models import Question, Submission, ExamSession
from code_executor import execute_code, test_code_with_cases
from plagiarism_detector import calculate_similarity
import json

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@login_required
def dashboard():
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
    return render_template('student_dashboard.html', questions=questions_list)

@student_bp.route('/question/<int:question_id>')
@login_required
def question_detail(question_id):
    question = Question.get_by_id(question_id)
    if not question:
        flash('Question not found', 'error')
        return redirect(url_for('student.dashboard'))
    
    # Start exam session
    ExamSession.create_or_update(session['user_id'], question_id)
    
    # Convert Row object to dictionary
    question_dict = {
        'id': question['id'],
        'title': question['title'],
        'description': question['description'],
        'difficulty': question['difficulty'],
        'function_name': question['function_name'],
        'test_cases': question['test_cases'],
        'example_code': question['example_code'],
        'created_at': question['created_at']
    }
    
    return render_template('question_detail.html', question=question_dict)

@student_bp.route('/run_code', methods=['POST'])
@login_required
def run_code():
    code = request.json.get('code', '')
    result = execute_code(code)
    return jsonify(result)

@student_bp.route('/test_code', methods=['POST'])
@login_required
def test_code():
    data = request.json
    code = data.get('code', '')
    function_name = data.get('function_name', '')
    test_cases = data.get('test_cases', [])
    
    result = test_code_with_cases(code, function_name, test_cases)
    return jsonify(result)

@student_bp.route('/submit_code', methods=['POST'])
@login_required
def submit_code():
    question_id = request.form['question_id']
    code = request.form['code']
    test_results_json = request.form.get('test_results', '{}')
    user_id = session['user_id']
    
    try:
        test_results = json.loads(test_results_json) if test_results_json else {}
    except:
        test_results = {}
    
    # Get question details for testing
    question = Question.get_by_id(question_id)
    if not question:
        flash('Question not found', 'error')
        return redirect(url_for('student.dashboard'))
    
    # Run tests if not already done
    if not test_results or 'results' not in test_results:
        test_results = test_code_with_cases(code, question['function_name'], question['test_cases'])
    
    passed_tests = test_results.get('passed', 0)
    total_tests = test_results.get('total', 0)
    
    # Calculate similarity with existing submissions
    existing_submissions = Submission.get_by_question(question_id)
    max_similarity = 0
    
    for submission in existing_submissions:
        if submission['user_id'] != user_id:  # Don't compare with own submissions
            similarity = calculate_similarity(code, submission['code'])
            max_similarity = max(max_similarity, similarity)
    
    # Save submission with test results
    Submission.create(user_id, question_id, code, test_results, passed_tests, total_tests, max_similarity)
    
    # End exam session
    ExamSession.end_session(user_id, question_id)
    
    # Flash appropriate message
    if passed_tests == total_tests:
        flash(f'Perfect! All {total_tests} test cases passed! 🎉', 'success')
    elif passed_tests > 0:
        flash(f'Partial success: {passed_tests}/{total_tests} test cases passed', 'warning')
    else:
        flash(f'No test cases passed. Please review your solution.', 'error')
    
    if max_similarity > 70:
        flash(f'Warning: High similarity detected ({max_similarity:.1f}%)', 'warning')
    
    return redirect(url_for('student.question_detail', question_id=question_id))

@student_bp.route('/log_exam_session', methods=['POST'])
@login_required
def log_exam_session():
    data = request.json
    question_id = data.get('question_id')
    action = data.get('action')
    user_id = session['user_id']
    
    if action == 'start':
        ExamSession.create_or_update(user_id, question_id)
    elif action == 'end':
        ExamSession.end_session(user_id, question_id)
    
    return jsonify({'success': True})

@student_bp.route('/log_violation', methods=['POST'])
@login_required
def log_violation():
    data = request.json
    question_id = data.get('question_id')
    violation_type = data.get('violation_type')
    user_id = session['user_id']
    
    ExamSession.log_violation(user_id, question_id, violation_type)
    
    return jsonify({'success': True})

@student_bp.route('/submissions')
@login_required
def my_submissions():
    submissions = Submission.get_by_user(session['user_id'])
    # Convert Row objects to dictionaries
    submissions_list = []
    for submission in submissions:
        submissions_list.append({
            'id': submission['id'],
            'user_id': submission['user_id'],
            'question_id': submission['question_id'],
            'code': submission['code'],
            'test_results': submission['test_results'],
            'passed_tests': submission['passed_tests'],
            'total_tests': submission['total_tests'],
            'similarity_score': submission['similarity_score'],
            'submitted_at': submission['submitted_at'],
            'question_title': submission['question_title']
        })
    return render_template('my_submissions.html', submissions=submissions_list)
