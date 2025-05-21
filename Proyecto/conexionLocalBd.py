import mysql.connector

def get_local_connection():
    try:
        return mysql.connector.connect(
        host="localhost",
        user="root",
        password="", 
        database="bd_ml601n",
        port=3306
    )
    except Exception as e:
        return f"Error: {e}"
