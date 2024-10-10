import sqlite3
import logging

LOGGER = logging.getLogger(__name__)

def get_db_connection():
    try:
        conn = sqlite3.connect('bot_db.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        LOGGER.error(f"Ошибка подключения к базе данных: {e}")
        raise

def create_table():
    conn = get_db_connection()
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS bot_db (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER UNIQUE
                    )''')
        conn.commit()
    except sqlite3.Error as e:
        LOGGER.error(f"Ошибка создания таблицы: {e}")
    finally:
        conn.close()

def add_subscriber(user_id):
    conn = get_db_connection()
    try:
        conn.execute('INSERT OR IGNORE INTO bot_db (user_id) VALUES (?)', (user_id,))
        conn.commit()
        LOGGER.info(f"Пользователь {user_id} добавлен в базу данных подписчиков.")
    except sqlite3.Error as e:
        LOGGER.error(f"Ошибка добавления пользователя {user_id}: {e}")
    finally:
        conn.close()

def get_all_bot_db():
    conn = get_db_connection()
    try:
        bot_db = conn.execute('SELECT user_id FROM bot_db').fetchall()
        return [row['user_id'] for row in bot_db]
    except sqlite3.Error as e:
        LOGGER.error(f"Ошибка при получении подписчиков: {e}")
        return []
    finally:
        conn.close()

# Инициализация таблицы
create_table()
