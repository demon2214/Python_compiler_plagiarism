from flask_mysqldb import MySQL
from config import Config
import logging

mysql = MySQL()

def init_app(app):
    """Initialize database with app"""
    app.config.from_object(Config)
    mysql.init_app(app)
    
    with app.app_context():
        init_db()
        create_default_data()

def init_db():
    """Initialize database tables"""
    try:
        conn = mysql.connection
        cur = conn.cursor()
        
        # Enable foreign key constraints
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Create tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                test_cases JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id VARCHAR(36) PRIMARY KEY,
                user_id INT NOT NULL,
                question_id INT NOT NULL,
                code LONGTEXT NOT NULL,
                output LONGTEXT,
                similarity_checked BOOLEAN DEFAULT FALSE,
                similarity_score FLOAT DEFAULT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS similarity_groups (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question_id INT NOT NULL,
                avg_similarity FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS group_members (
                group_id INT NOT NULL,
                submission_id VARCHAR(36) NOT NULL,
                similarity_score FLOAT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES similarity_groups(id) ON DELETE CASCADE,
                FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
                PRIMARY KEY (group_id, submission_id)
            )
            """
        ]
        
        for table in tables:
            cur.execute(table)
        
        # Re-enable foreign key constraints
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        logging.info("Database tables initialized successfully")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Database initialization failed: {str(e)}")
        raise

def create_default_data():
    """Create default admin user and sample questions"""
    try:
        conn = mysql.connection
        cur = conn.cursor()
        
        # Add default users
        cur.execute("""
            INSERT IGNORE INTO users (username, password, is_admin)
            VALUES (%s, %s, %s)
        """, ('admin', 'admin123', True))
        
        cur.execute("""
            INSERT IGNORE INTO users (username, password, is_admin)
            VALUES (%s, %s, %s)
        """, ('student', 'student123', False))
        
        # Add sample questions if none exist
        cur.execute("SELECT COUNT(*) as count FROM questions")
        if cur.fetchone()['count'] == 0:
            sample_questions = [
                (1, 'Factorial Calculation', 'Write a function to calculate the factorial of a number.',
                 '{"test_cases": [{"input": "5", "output": "120"}, {"input": "0", "output": "1"}]}'),
                (2, 'Fibonacci Sequence', 'Write a function to generate the nth Fibonacci number.',
                 '{"test_cases": [{"input": "5", "output": "5"}, {"input": "8", "output": "21"}]}')
            ]
            cur.executemany("""
                INSERT INTO questions (id, title, description, test_cases)
                VALUES (%s, %s, %s, %s)
            """, sample_questions)
        
        conn.commit()
        logging.info("Default data created successfully")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Failed to create default data: {str(e)}")
        raise