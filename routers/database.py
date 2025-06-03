import pymysql
from fastapi import HTTPException


# ตัวอย่าง config ของ database
DB_CONFIG = {
    "host": "localhost",
    "user": "test",
    "password": "1234",
    "database": "web_tbrc",
    "cursorclass": pymysql.cursors.DictCursor  # ใช้ DictCursor เพื่อให้ผลลัพธ์เป็น dictionary
}

def get_cursor():
    try:
        # Establish database connection
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        return connection, cursor  # คืนทั้ง connection และ cursor
        
    except pymysql.MySQLError as e:
        # Handle database-specific errors
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
