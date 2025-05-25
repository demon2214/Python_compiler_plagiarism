from database import app, get_db_connection

def test_connection():
    with app.app_context():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            print("Tables in database:", cursor.fetchall())
            cursor.close()
            conn.close()
            print("Database connection successful!")
        except Exception as e:
            print(f"Connection failed: {str(e)}")

if __name__ == '__main__':
    test_connection()