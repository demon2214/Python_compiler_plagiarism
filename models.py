from database import get_db_connection
from datetime import datetime
import MySQLdb

class User:
    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()
        return user

class Question:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM questions")
        questions = cursor.fetchall()
        conn.close()
        return questions

    @staticmethod
    def get_by_id(question_id):
        conn = get_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM questions WHERE id = %s", (question_id,))
        question = cursor.fetchone()
        conn.close()
        return question

class Submission:
    @staticmethod
    def create(submission_id, user_id, question_id, code, output):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO submissions (id, user_id, question_id, code, output)
            VALUES (%s, %s, %s, %s, %s)
        """, (submission_id, user_id, question_id, code, output))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_by_question(question_id):
        conn = get_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT s.*, u.username 
            FROM submissions s
            JOIN users u ON s.user_id = u.id
            WHERE s.question_id = %s
            ORDER BY s.submitted_at DESC
        """, (question_id,))
        submissions = cursor.fetchall()
        conn.close()
        return submissions

class SimilarityGroup:
    @staticmethod
    def create(question_id, submission_ids, avg_similarity):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Insert similarity group
            cursor.execute("""
                INSERT INTO similarity_groups (question_id, avg_similarity)
                VALUES (%s, %s)
            """, (question_id, avg_similarity))
            group_id = cursor.lastrowid
            
            # Insert group members
            for sub_id in submission_ids:
                cursor.execute("""
                    INSERT INTO group_members (group_id, submission_id)
                    VALUES (%s, %s)
                """, (group_id, sub_id))
            
            conn.commit()
            return group_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_by_question(question_id):
        conn = get_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        try:
            # Get groups
            cursor.execute("""
                SELECT g.id, g.question_id, g.avg_similarity, g.created_at,
                       COUNT(m.submission_id) as member_count
                FROM similarity_groups g
                JOIN group_members m ON g.id = m.group_id
                WHERE g.question_id = %s
                GROUP BY g.id
                ORDER BY g.avg_similarity DESC
            """, (question_id,))
            groups = cursor.fetchall()
            
            # Get members for each group
            result = []
            for group in groups:
                cursor.execute("""
                    SELECT s.*, u.username
                    FROM submissions s
                    JOIN users u ON s.user_id = u.id
                    JOIN group_members m ON s.id = m.submission_id
                    WHERE m.group_id = %s
                """, (group['id'],))
                submissions = cursor.fetchall()
                
                group['submissions'] = submissions
                result.append(group)
            
            return result
        finally:
            conn.close()