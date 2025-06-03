import pymysql
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()  # โหลดค่าจาก .env

# ตัวอย่าง config ของ database
DB_CONFIG = {
    "host": os.getenv("PMA_HOST"),
    "user": os.getenv("PMA_USER"),
    "password": os.getenv("PMA_PASSWORD"),
    "database": os.getenv("PMA_DATABASE"),
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
