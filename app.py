from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from similarity_checker import CodeSimilarityChecker
from models import User, Question, Submission, SimilarityGroup
from database import mysql, init_app
from config import Config
import uuid
import os
import ast
import astunparse
import logging

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
init_app(app)

# Initialize components
similarity_checker = CodeSimilarityChecker()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 10 Questions with non-boolean answers
QUESTIONS = {
    1: {
        'id': 1,
        'title': 'Sum of Two Numbers',
        'description': 'Write a function that takes two numbers and returns their sum.',
        'starter_code': 'def solution(a, b):\n    # Your code here\n    pass',
        'test_cases': [
            {'input': '5, 3', 'output': '8'},
            {'input': '-1, 1', 'output': '0'},
            {'input': '0, 0', 'output': '0'}
        ]
    },
    2: {
        'id': 2,
        'title': 'Factorial Calculation',
        'description': 'Write a function to calculate the factorial of a number.',
        'starter_code': 'def solution(n):\n    # Your code here\n    pass',
        'test_cases': [
            {'input': '5', 'output': '120'},
            {'input': '0', 'output': '1'},
            {'input': '7', 'output': '5040'}
        ]
    },
    3: {
        'id': 3,
        'title': 'Fibonacci Sequence',
        'description': 'Write a function to generate the nth Fibonacci number.',
        'starter_code': 'def solution(n):\n    # Your code here\n    pass',
        'test_cases': [
            {'input': '5', 'output': '5'},
            {'input': '8', 'output': '21'},
            {'input': '1', 'output': '1'}
        ]
    },
    4: {
        'id': 4,
        'title': 'String Reversal',
        'description': 'Write a function that reverses a string.',
        'starter_code': 'def solution(s):\n    # Your code here\n    pass',
        'test_cases': [
            {'input': '"hello"', 'output': '"olleh"'},
            {'input': '"Python"', 'output': '"nohtyP"'},
            {'input': '""', 'output': '""'}
        ]
    },
    5: {
        'id': 5,
        'title': 'List Sum',
        'description': 'Write a function that sums all numbers in a list.',
        'starter_code': 'def solution(lst):\n    # Your code here\n    pass',
        'test_cases': [
            {'input': '[1, 2, 3]', 'output': '6'},
            {'input': '[-1, 0, 1]', 'output': '0'},
            {'input': '[]', 'output': '0'}
        ]
    },
    6: {
        'id': 6,
        'title': 'Count Vowels',
        'description': 'Write a function that counts the number of vowels in a string.',
        'starter_code': 'def solution(s):\n    # Your code here\n    pass',
        'test_cases': [
            {'input': '"hello"', 'output': '2'},
            {'input': '"Python"', 'output': '1'},
            {'input': '"rhythm"', 'output': '0'}
        ]
    },
    7: {
        'id': 7,
        'title': 'Max Number',
        'description': 'Write a function that returns the largest number in a list.',
        'starter_code': 'def solution(lst):\n    # Your code here\n    pass',
        'test_cases': [
            {'input': '[1, 5, 3]', 'output': '5'},
            {'input': '[-1, -5, -3]', 'output': '-1'},
            {'input': '[0]', 'output': '0'}
        ]
    },
    8: {
        'id': 8,
        'title': 'Multiply List',
        'description': 'Write a function that multiplies all numbers in a list.',
        'starter_code': 'def solution(lst):\n    # Your code here\n    pass',
        'test_cases': [
            {'input': '[1, 2, 3]', 'output': '6'},
            {'input': '[2, 4, 5]', 'output': '40'},
            {'input': '[]', 'output': '1'}
        ]
    },
    9: {
        'id': 9,
        'title': 'Palindrome Score',
        'description': 'Write a function that returns 1 if a string is a palindrome, 0 otherwise.',
        'starter_code': 'def solution(s):\n    # Your code here\n    pass',
        'test_cases': [
            {'input': '"madam"', 'output': '1'},
            {'input': '"hello"', 'output': '0'},
            {'input': '"racecar"', 'output': '1'}
        ]
    },
    10: {
        'id': 10,
        'title': 'GCD Calculation',
        'description': 'Write a function that calculates the greatest common divisor of two numbers.',
        'starter_code': 'def solution(a, b):\n    # Your code here\n    pass',
        'test_cases': [
            {'input': '48, 18', 'output': '6'},
            {'input': '17, 5', 'output': '1'},
            {'input': '0, 5', 'output': '5'}
        ]
    }
}

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    
    question_id = int(request.args.get('question_id', 1))
    question = QUESTIONS.get(question_id, QUESTIONS[1])
    
    return render_template('student.html', 
                         question=question,
                         questions=QUESTIONS)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.get_by_username(username)
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            
            if user['is_admin']:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('home'))
        
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
    question_id = data.get('question_id', 1)
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    try:
        question = QUESTIONS.get(int(question_id), QUESTIONS[1])
        test_cases = question['test_cases']
        
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
        
        if 'solution' not in local_vars:
            return jsonify({'output': 'Error: No "solution" function found'})
        
        test_results = []
        for test_case in test_cases:
            try:
                input_str = test_case['input']
                if ',' in input_str:
                    input_args = [ast.literal_eval(x.strip()) for x in input_str.split(',')]
                    result = local_vars['solution'](*input_args)
                else:
                    input_val = ast.literal_eval(input_str)
                    result = local_vars['solution'](input_val)
                
                expected = ast.literal_eval(test_case['output'])
                passed = result == expected
                
                test_results.append({
                    'input': test_case['input'],
                    'expected': str(expected),
                    'actual': str(result),
                    'passed': passed
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
        logger.error(f"Code execution failed: {str(e)}")
        return jsonify({
            'output': f"Error: {str(e)}",
            'status': 'error'
        })

@app.route('/submit', methods=['POST'])
def submit_code():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        code = data.get('code')
        question_id = data.get('question_id', 1)
        
        if not code:
            return jsonify({'error': 'No code provided'}), 400
        
        # First validate the code by running it
        run_response = run_code()
        run_data = run_response.get_json()
        
        if run_response.status_code != 200 or run_data.get('status') != 'success':
            return jsonify({
                'status': 'error',
                'message': 'Code failed to run',
                'output': run_data.get('output', 'Unknown error')
            })
        
        # If code runs successfully, submit it
        submission_id = str(uuid.uuid4())
        
        Submission.create(
            submission_id=submission_id,
            user_id=session['user_id'],
            question_id=question_id,
            code=code,
            output=str(run_data)
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Code submitted successfully',
            'submission_id': submission_id,
            'output': run_data
        })
        
    except Exception as e:
        logger.error(f"Submission failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to submit code',
            'error': str(e) if app.debug else None
        }), 500

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
    
    similar_groups = similarity_checker.find_similar_submissions([
        {'id': s['id'], 'code': s['code']} for s in submissions
    ])
    
    for group in similar_groups:
        SimilarityGroup.create(
            question_id=question_id,
            submission_ids=[s['id'] for s in group['submissions']],
            avg_similarity=group['avg_similarity']
        )
    
    groups = SimilarityGroup.get_by_question(question_id)
    
    return render_template('results.html', 
                         groups=groups,
                         question=QUESTIONS.get(question_id))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)