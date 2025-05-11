import sqlite3

DB_NAME = "election.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = get_connection()
    c = conn.cursor()

    # Drop old tables if needed (uncomment if you're fixing broken schemas)
    # c.execute("DROP TABLE IF EXISTS users")
    # c.execute("DROP TABLE IF EXISTS parties")

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            has_voted INTEGER DEFAULT 0
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS parties (
            name TEXT PRIMARY KEY,
            votes INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()

def register_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None

def has_user_voted(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT has_voted FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == 1

def set_user_voted(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET has_voted=1 WHERE username=?", (username,))
    conn.commit()
    conn.close()

def add_party(name):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO parties (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_parties():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM parties")
    parties = [row[0] for row in c.fetchall()]
    conn.close()
    return parties

def vote_for_party(party_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE parties SET votes = votes + 1 WHERE name=?", (party_name,))
    conn.commit()
    conn.close()

def get_results():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name, votes FROM parties ORDER BY votes DESC")
    results = c.fetchall()
    conn.close()
    return results
