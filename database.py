from flask import Flask
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'code_similarity_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def init_db():
    """Initialize database tables"""
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            
            # Create users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create questions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL,
                    test_cases TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create submissions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS submissions (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id INT NOT NULL,
                    question_id INT NOT NULL,
                    code TEXT NOT NULL,
                    output TEXT,
                    similarity_checked BOOLEAN DEFAULT FALSE,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (question_id) REFERENCES questions(id)
                )
            """)
            
            # Create similarity_groups table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS similarity_groups (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    question_id INT NOT NULL,
                    avg_similarity FLOAT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (question_id) REFERENCES questions(id)
                )
            """)
            
            # Create group_members table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS group_members (
                    group_id INT NOT NULL,
                    submission_id VARCHAR(36) NOT NULL,
                    FOREIGN KEY (group_id) REFERENCES similarity_groups(id),
                    FOREIGN KEY (submission_id) REFERENCES submissions(id),
                    PRIMARY KEY (group_id, submission_id)
                )
            """)
            
            mysql.connection.commit()
            print("Database tables created successfully")
            
    except Exception as e:
        print(f"Error initializing database: {str(e)}")

def get_db_connection():
    """Get MySQL database connection"""
    return mysql.connection

# Initialize the database when this module is imported
init_db()