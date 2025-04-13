import sqlite3
import os

# Set up data directory and database path
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DATA_FOLDER, "reminders.db")

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            description TEXT,
            deadline TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def add_reminder_to_db(user_id, desc, deadline_str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO reminders (user_id, description, deadline) VALUES (?, ?, ?)",
        (user_id, desc, deadline_str)
    )
    reminder_id = c.lastrowid
    conn.commit()
    conn.close()
    return reminder_id

def delete_reminder_from_db(reminder_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()

def delete_all_reminders_for_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM reminders WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_reminders_by_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, description, deadline FROM reminders WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows
