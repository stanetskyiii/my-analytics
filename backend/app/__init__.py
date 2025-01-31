import os
import psycopg2
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def get_db_connection():
    print("DB_CONFIG:", {k: v if k != 'password' else '****' for k, v in DB_CONFIG.items()})
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Успешное подключение к базе данных!")
        conn.close()
    except Exception as e:
        print("Ошибка подключения к базе данных:", e)

if __name__ == '__main__':
    get_db_connection()
