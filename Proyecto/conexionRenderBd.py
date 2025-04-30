import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

def get_render_connection():
    
    try:
        return psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port or 5432,
            sslmode="require"
        )
    except Exception as e:
        raise RuntimeError(f"Error al conectar a la base de datos: {e}")
