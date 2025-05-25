from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from similarity_checker import CodeSimilarityChecker
from models import User, Question, Submission, SimilarityGroup
from datetime import datetime, timedelta
import uuid
import os
import ast
import astunparse

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize components
similarity_checker = CodeSimilarityChecker()

# Sample questions
QUESTIONS = {
    1: {
        'id': 1,
        'title': 'Factorial Calculation',
        'description': 'Write a function to calculate the factorial of a number.',
        'test_cases': [
            {'input': '5', 'output': '120'},
            {'input': '0', 'output': '1'},
            {'input': '7', 'output': '5040'}
        ]
    },
    2: {
        'id': 2,
        'title': 'Fibonacci Sequence',
        'description': 'Write a function to generate the nth Fibonacci number.',
        'test_cases': [
            {'input': '5', 'output': '5'},
            {'input': '8', 'output': '21'},
            {'input': '1', 'output': '1'}
        ]
    }
}

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    
    return render_template('student.html', question=QUESTIONS[1])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Hardcoded users for demo (replace with database check in production)
        if username == 'student' and password == 'student123':
            session['user_id'] = 1
            session['username'] = 'student'
            session['is_admin'] = False
            return redirect(url_for('home'))
        elif username == 'admin' and password == 'admin123':
            session['user_id'] = 2
            session['username'] = 'admin'
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/run', methods=['POST'])
def run_code():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    code = data.get('code')
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    try:
        # Create a restricted globals dictionary
        restricted_globals = {
            '__builtins__': {
                'range': range,
                'print': print,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'len': len,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'None': None,
                'True': True,
                'False': False
            }
        }
        
        local_vars = {}
        exec(code, restricted_globals, local_vars)
        
        # Check if solution function exists
        if 'solution' not in local_vars:
            return jsonify({'output': 'Error: No "solution" function found'})
        
        # Test with sample inputs
        test_results = []
        for test_case in QUESTIONS[1]['test_cases']:
            try:
                input_val = int(test_case['input'])
                expected = int(test_case['output'])
                result = local_vars['solution'](input_val)
                test_results.append({
                    'input': input_val,
                    'expected': expected,
                    'actual': result,
                    'passed': result == expected
                })
            except Exception as e:
                test_results.append({
                    'input': test_case['input'],
                    'error': str(e)
                })
        
        return jsonify({
            'output': test_results,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'output': f"Error: {str(e)}",
            'status': 'error'
        })

@app.route('/submit', methods=['POST'])
def submit_code():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    data = request.json
    code = data.get('code')
    question_id = data.get('question_id', 1)
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    # Run the code to get output
    output = run_code().get_json()
    
    submission_id = str(uuid.uuid4())
    Submission.create(
        submission_id,
        session['user_id'],
        question_id,
        code,
        str(output)
    )
    
    return jsonify({
        'status': 'success',
        'message': 'Code submitted successfully',
        'output': output
    })

@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    return render_template('admin.html', questions=QUESTIONS.values())

@app.route('/admin/similarity')
def admin_similarity():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    question_id = int(request.args.get('question_id', 1))
    submissions = Submission.get_by_question(question_id)
    
    # Check for similar submissions
    similar_groups = similarity_checker.find_similar_submissions([
        {'id': s.id, 'code': s.code} for s in submissions
    ])
    
    # Save the groups to database
    for group in similar_groups:
        SimilarityGroup.create(
            question_id,
            [s['id'] for s in group['submissions']],
            group['avg_similarity']
        )
    
    # Get all similarity groups from database
    groups = SimilarityGroup.get_by_question(question_id)
    
    return render_template('results.html', 
                        groups=groups,
                        question=QUESTIONS.get(question_id))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)