import sqlite3

def get_connection():
    return sqlite3.connect("election.db", check_same_thread=False)

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        voted INTEGER DEFAULT 0
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS parties (
        party_name TEXT PRIMARY KEY,
        votes INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cur.fetchone()
    conn.close()
    return result

def user_has_voted(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT voted FROM users WHERE username=?", (username,))
    result = cur.fetchone()
    conn.close()
    return result[0] == 1 if result else False

def set_user_voted(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET voted = 1 WHERE username=?", (username,))
    conn.commit()
    conn.close()

def add_party(party_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO parties (party_name, votes) VALUES (?, 0)", (party_name,))
    conn.commit()
    conn.close()

def get_parties():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT party_name FROM parties")
    parties = [row[0] for row in cur.fetchall()]
    conn.close()
    return parties

def vote_party(party_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE parties SET votes = votes + 1 WHERE party_name=?", (party_name,))
    conn.commit()
    conn.close()

def get_results():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM parties ORDER BY votes DESC")
    result = cur.fetchall()
    conn.close()
    return result
