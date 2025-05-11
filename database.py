import sqlite3

def init_db():
    conn = sqlite3.connect("election.db")
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            voted INTEGER DEFAULT 0
        )
    """)

    # Parties table
    c.execute("""
        CREATE TABLE IF NOT EXISTS parties (
            name TEXT PRIMARY KEY,
            votes INTEGER DEFAULT 0
        )
    """)

    # Global flags
    c.execute("""
        CREATE TABLE IF NOT EXISTS flags (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Add default admin user if not exists
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))

    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect("election.db")
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
    conn = sqlite3.connect("election.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None

def add_party(name):
    conn = sqlite3.connect("election.db")
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
    conn = sqlite3.connect("election.db")
    c = conn.cursor()
    c.execute("SELECT name FROM parties")
    parties = [row[0] for row in c.fetchall()]
    conn.close()
    return parties

def vote_party(name):
    conn = sqlite3.connect("election.db")
    c = conn.cursor()
    c.execute("UPDATE parties SET votes = votes + 1 WHERE name=?", (name,))
    conn.commit()
    conn.close()

def set_user_voted(username):
    conn = sqlite3.connect("election.db")
    c = conn.cursor()
    c.execute("UPDATE users SET voted=1 WHERE username=?", (username,))
    conn.commit()
    conn.close()

def user_has_voted(username):
    conn = sqlite3.connect("election.db")
    c = conn.cursor()
    c.execute("SELECT voted FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == 1

def get_results():
    conn = sqlite3.connect("election.db")
    c = conn.cursor()
    c.execute("SELECT name, votes FROM parties")
    results = c.fetchall()
    conn.close()
    return results

def release_results():
    conn = sqlite3.connect("election.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO flags (key, value) VALUES ('results_released', '1')")
    conn.commit()
    conn.close()

def results_are_released():
    conn = sqlite3.connect("election.db")
    c = conn.cursor()
    c.execute("SELECT value FROM flags WHERE key='results_released'")
    row = c.fetchone()
    conn.close()
    return row and row[0] == '1'
