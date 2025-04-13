import sqlite3

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    """Create a table in the database."""
    try:
        sql_create_table = """CREATE TABLE IF NOT EXISTS records (
                                id integer PRIMARY KEY,
                                name text NOT NULL,
                                value text
                            );"""
        cursor = conn.cursor()
        cursor.execute(sql_create_table)
    except sqlite3.Error as e:
        print(e)

def insert_record(conn, name, value):
    """Insert a new record into the records table."""
    sql = '''INSERT INTO records(name, value) VALUES(?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, (name, value))
    conn.commit()
    return cur.lastrowid

def retrieve_records(conn):
    """Retrieve all records from the records table."""
    cur = conn.cursor()
    cur.execute("SELECT * FROM records")
    return cur.fetchall()

def update_record(conn, record_id, name, value):
    """Update a record in the records table."""
    sql = '''UPDATE records SET name = ?, value = ? WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, (name, value, record_id))
    conn.commit()

def delete_record(conn, record_id):
    """Delete a record from the records table."""
    sql = 'DELETE FROM records WHERE id = ?'
    cur = conn.cursor()
    cur.execute(sql, (record_id,))
    conn.commit()