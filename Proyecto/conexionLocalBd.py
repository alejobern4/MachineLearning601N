import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

db_url = os.getenv("DB_URL")

def get_render_connection():
    try:
        return psycopg2.connect(db_url)
    except Exception as e:
        raise RuntimeError(f"Error al conectar a la base de datos: {e}")
