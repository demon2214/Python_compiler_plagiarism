import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime
import json

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',  # Default XAMPP password is empty
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

DATABASE_NAME = 'coding_test_platform'

def get_db_connection():
    """Get database connection"""
    try:
        connection = mysql.connector.connect(
            **DB_CONFIG,
            database=DATABASE_NAME
        )
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_database():
    """Create database if it doesn't exist"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"Database '{DATABASE_NAME}' created successfully or already exists")
        
        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error creating database: {e}")

def init_db():
    """Initialize database with tables and sample data"""
    # First create the database
    create_database()
    
    connection = get_db_connection()
    if not connection:
        print("Failed to connect to database")
        return
    
    cursor = connection.cursor()
    
    try:
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('student', 'admin') NOT NULL DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_role (role)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        ''')
        
        # Questions table with test cases
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                difficulty ENUM('Easy', 'Medium', 'Hard') NOT NULL,
                function_name VARCHAR(100) NOT NULL,
                test_cases JSON NOT NULL,
                example_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_difficulty (difficulty),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        ''')
        
        # Submissions table with test results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                question_id INT NOT NULL,
                code TEXT NOT NULL,
                test_results JSON,
                passed_tests INT DEFAULT 0,
                total_tests INT DEFAULT 0,
                similarity_score DECIMAL(5,2) DEFAULT 0.00,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_question_id (question_id),
                INDEX idx_similarity (similarity_score),
                INDEX idx_submitted_at (submitted_at)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        ''')
        
        # Exam sessions table for monitoring
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exam_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                question_id INT NOT NULL,
                session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tab_switches INT DEFAULT 0,
                fullscreen_exits INT DEFAULT 0,
                camera_enabled BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
                INDEX idx_user_session (user_id, question_id),
                INDEX idx_active (is_active)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        ''')
        
        # Create default admin user
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT IGNORE INTO users (username, password, role) 
            VALUES (%s, %s, %s)
        ''', ('admin', admin_password, 'admin'))
        
        # Create sample questions with test cases
        sample_questions = [
            {
                'title': 'Hello World',
                'description': 'Write a function called "hello_world" that returns the string "Hello, World!".\n\nYour function should not take any parameters and must return exactly "Hello, World!"',
                'difficulty': 'Easy',
                'function_name': 'hello_world',
                'test_cases': [
                    {'input': [], 'expected': 'Hello, World!', 'description': 'Basic test'}
                ],
                'example_code': '# Example:\ndef hello_world():\n    return "Hello, World!"\n\n# Test your function:\nresult = hello_world()\nprint(result)'
            },
            {
                'title': 'Sum of Two Numbers',
                'description': 'Write a function called "add_numbers" that takes two numbers as parameters and returns their sum.\n\nThe function should work with both integers and floating-point numbers.',
                'difficulty': 'Easy',
                'function_name': 'add_numbers',
                'test_cases': [
                    {'input': [2, 3], 'expected': 5, 'description': 'Add two positive integers'},
                    {'input': [-1, 1], 'expected': 0, 'description': 'Add negative and positive'},
                    {'input': [0, 0], 'expected': 0, 'description': 'Add zeros'},
                    {'input': [2.5, 3.7], 'expected': 6.2, 'description': 'Add floating point numbers'}
                ],
                'example_code': '# Example:\ndef add_numbers(a, b):\n    return a + b\n\n# Test your function:\nresult = add_numbers(5, 3)\nprint(f"5 + 3 = {result}")'
            },
            {
                'title': 'Calculate Average',
                'description': 'Write a function called "calculate_average" that takes a list of numbers and returns their average.\n\nIf the list is empty, return 0. The result should be a floating-point number.',
                'difficulty': 'Easy',
                'function_name': 'calculate_average',
                'test_cases': [
                    {'input': [[10, 20, 30]], 'expected': 20.0, 'description': 'Average of three numbers'},
                    {'input': [[]], 'expected': 0, 'description': 'Empty list'},
                    {'input': [[5]], 'expected': 5.0, 'description': 'Single number'},
                    {'input': [[1, 2, 3, 4, 5]], 'expected': 3.0, 'description': 'Average of five numbers'}
                ],
                'example_code': '# Example:\ndef calculate_average(numbers):\n    if not numbers:\n        return 0\n    return sum(numbers) / len(numbers)\n\n# Test your function:\nnums = [10, 20, 30]\navg = calculate_average(nums)\nprint(f"Average: {avg}")'
            },
            {
                'title': 'Fibonacci Number',
                'description': 'Write a function called "fibonacci" that takes a non-negative integer n and returns the nth Fibonacci number.\n\nThe Fibonacci sequence: F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2) for n>1.',
                'difficulty': 'Medium',
                'function_name': 'fibonacci',
                'test_cases': [
                    {'input': [0], 'expected': 0, 'description': 'F(0) = 0'},
                    {'input': [1], 'expected': 1, 'description': 'F(1) = 1'},
                    {'input': [2], 'expected': 1, 'description': 'F(2) = 1'},
                    {'input': [5], 'expected': 5, 'description': 'F(5) = 5'},
                    {'input': [10], 'expected': 55, 'description': 'F(10) = 55'}
                ],
                'example_code': '# Example (iterative approach):\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b\n\n# Test your function:\nfor i in range(6):\n    print(f"F({i}) = {fibonacci(i)}")'
            },
            {
                'title': 'Prime Number Checker',
                'description': 'Write a function called "is_prime" that takes a positive integer and returns True if it is prime, False otherwise.\n\nA prime number is greater than 1 and has no positive divisors other than 1 and itself.',
                'difficulty': 'Medium',
                'function_name': 'is_prime',
                'test_cases': [
                    {'input': [2], 'expected': True, 'description': '2 is prime'},
                    {'input': [3], 'expected': True, 'description': '3 is prime'},
                    {'input': [4], 'expected': False, 'description': '4 is not prime'},
                    {'input': [17], 'expected': True, 'description': '17 is prime'},
                    {'input': [25], 'expected': False, 'description': '25 is not prime'},
                    {'input': [1], 'expected': False, 'description': '1 is not prime'}
                ],
                'example_code': '# Example:\ndef is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\n# Test your function:\ntest_numbers = [2, 3, 4, 5, 17, 25]\nfor num in test_numbers:\n    print(f"{num} is prime: {is_prime(num)}")'
            },
            {
                'title': 'Palindrome Checker',
                'description': 'Write a function called "is_palindrome" that takes a string and returns True if it is a palindrome, False otherwise.\n\nIgnore case and spaces. A palindrome reads the same forwards and backwards.',
                'difficulty': 'Medium',
                'function_name': 'is_palindrome',
                'test_cases': [
                    {'input': ['racecar'], 'expected': True, 'description': 'Simple palindrome'},
                    {'input': ['A man a plan a canal Panama'], 'expected': True, 'description': 'Palindrome with spaces'},
                    {'input': ['hello'], 'expected': False, 'description': 'Not a palindrome'},
                    {'input': ['Madam'], 'expected': True, 'description': 'Case insensitive palindrome'},
                    {'input': [''], 'expected': True, 'description': 'Empty string is palindrome'}
                ],
                'example_code': '# Example:\ndef is_palindrome(s):\n    # Remove spaces and convert to lowercase\n    cleaned = s.replace(" ", "").lower()\n    return cleaned == cleaned[::-1]\n\n# Test your function:\ntest_strings = ["racecar", "hello", "Madam"]\nfor text in test_strings:\n    print(f"\\"{text}\\" is palindrome: {is_palindrome(text)}")'
            }
        ]
        
        for question_data in sample_questions:
            cursor.execute('''
                INSERT IGNORE INTO questions (title, description, difficulty, function_name, test_cases, example_code) 
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                question_data['title'],
                question_data['description'],
                question_data['difficulty'],
                question_data['function_name'],
                json.dumps(question_data['test_cases']),
                question_data['example_code']
            ))
        
        connection.commit()
        print("Database initialized successfully with sample data")
        
    except Error as e:
        print(f"Error initializing database: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

class User:
    @staticmethod
    def create(username, password, role='student'):
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cursor.execute(
                'INSERT INTO users (username, password, role) VALUES (%s, %s, %s)',
                (username, hashed_password, role)
            )
            connection.commit()
            return True
        except Error as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def authenticate(username, password):
        connection = get_db_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(dictionary=True)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cursor.execute(
                'SELECT * FROM users WHERE username = %s AND password = %s',
                (username, hashed_password)
            )
            user = cursor.fetchone()
            return user
        except Error as e:
            print(f"Error authenticating user: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def get_all():
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
            users = cursor.fetchall()
            return users
        except Error as e:
            print(f"Error getting users: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def delete(user_id):
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        try:
            cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
            connection.commit()
            return True
        except Error as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

class Question:
    @staticmethod
    def create(title, description, difficulty, function_name, test_cases, example_code):
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO questions (title, description, difficulty, function_name, test_cases, example_code) VALUES (%s, %s, %s, %s, %s, %s)',
                (title, description, difficulty, function_name, json.dumps(test_cases), example_code)
            )
            connection.commit()
            return True
        except Error as e:
            print(f"Error creating question: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def get_all():
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT * FROM questions ORDER BY created_at DESC')
            questions = cursor.fetchall()
            # Parse JSON test_cases
            for question in questions:
                if question['test_cases']:
                    question['test_cases'] = json.loads(question['test_cases'])
            return questions
        except Error as e:
            print(f"Error getting questions: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def get_by_id(question_id):
        connection = get_db_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT * FROM questions WHERE id = %s', (question_id,))
            question = cursor.fetchone()
            if question and question['test_cases']:
                question['test_cases'] = json.loads(question['test_cases'])
            return question
        except Error as e:
            print(f"Error getting question: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def delete(question_id):
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        try:
            cursor.execute('DELETE FROM questions WHERE id = %s', (question_id,))
            connection.commit()
            return True
        except Error as e:
            print(f"Error deleting question: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

class Submission:
    @staticmethod
    def create(user_id, question_id, code, test_results, passed_tests, total_tests, similarity_score=0):
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO submissions (user_id, question_id, code, test_results, passed_tests, total_tests, similarity_score) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (user_id, question_id, code, json.dumps(test_results), passed_tests, total_tests, similarity_score)
            )
            connection.commit()
            return True
        except Error as e:
            print(f"Error creating submission: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def get_all():
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT s.*, u.username, q.title as question_title 
                FROM submissions s 
                JOIN users u ON s.user_id = u.id 
                JOIN questions q ON s.question_id = q.id 
                ORDER BY s.submitted_at DESC
            ''')
            submissions = cursor.fetchall()
            # Parse JSON test_results
            for submission in submissions:
                if submission['test_results']:
                    submission['test_results'] = json.loads(submission['test_results'])
            return submissions
        except Error as e:
            print(f"Error getting submissions: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def get_by_user(user_id):
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT s.*, q.title as question_title 
                FROM submissions s 
                JOIN questions q ON s.question_id = q.id 
                WHERE s.user_id = %s 
                ORDER BY s.submitted_at DESC
            ''', (user_id,))
            submissions = cursor.fetchall()
            # Parse JSON test_results
            for submission in submissions:
                if submission['test_results']:
                    submission['test_results'] = json.loads(submission['test_results'])
            return submissions
        except Error as e:
            print(f"Error getting user submissions: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def get_by_question(question_id):
        connection = get_db_connection()
        if not connection:
            return []
        
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT s.*, u.username 
                FROM submissions s 
                JOIN users u ON s.user_id = u.id 
                WHERE s.question_id = %s 
                ORDER BY s.submitted_at DESC
            ''', (question_id,))
            submissions = cursor.fetchall()
            # Parse JSON test_results
            for submission in submissions:
                if submission['test_results']:
                    submission['test_results'] = json.loads(submission['test_results'])
            return submissions
        except Error as e:
            print(f"Error getting question submissions: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

class ExamSession:
    @staticmethod
    def create_or_update(user_id, question_id):
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO exam_sessions (user_id, question_id, camera_enabled) 
                VALUES (%s, %s, TRUE)
                ON DUPLICATE KEY UPDATE 
                session_start = CURRENT_TIMESTAMP,
                is_active = TRUE
            ''', (user_id, question_id))
            connection.commit()
            return True
        except Error as e:
            print(f"Error creating exam session: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def log_violation(user_id, question_id, violation_type):
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        try:
            if violation_type == 'tab_switch':
                cursor.execute('''
                    UPDATE exam_sessions 
                    SET tab_switches = tab_switches + 1 
                    WHERE user_id = %s AND question_id = %s AND is_active = TRUE
                ''', (user_id, question_id))
            elif violation_type == 'fullscreen_exit':
                cursor.execute('''
                    UPDATE exam_sessions 
                    SET fullscreen_exits = fullscreen_exits + 1 
                    WHERE user_id = %s AND question_id = %s AND is_active = TRUE
                ''', (user_id, question_id))
            
            connection.commit()
            return True
        except Error as e:
            print(f"Error logging violation: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def end_session(user_id, question_id):
        connection = get_db_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        try:
            cursor.execute('''
                UPDATE exam_sessions 
                SET is_active = FALSE 
                WHERE user_id = %s AND question_id = %s
            ''', (user_id, question_id))
            connection.commit()
            return True
        except Error as e:
            print(f"Error ending exam session: {e}")
            return False
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def get_session_stats(user_id, question_id):
        connection = get_db_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT * FROM exam_sessions 
                WHERE user_id = %s AND question_id = %s 
                ORDER BY session_start DESC LIMIT 1
            ''', (user_id, question_id))
            session = cursor.fetchone()
            return session
        except Error as e:
            print(f"Error getting session stats: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
