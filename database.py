import sqlite3

# Connect to SQLite database (or create it if not exists)
conn = sqlite3.connect('voting_app.db', check_same_thread=False)
cursor = conn.cursor()

# Create necessary tables
def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            has_voted INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parties (
            name TEXT PRIMARY KEY,
            votes INTEGER DEFAULT 0
        )
    ''')
    conn.commit()

# Add a new user
def add_user(username, password):
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Authenticate a user
def authenticate_user(username, password):
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    return cursor.fetchone() is not None

# Add a political party
def add_party(name):
    try:
        cursor.execute('INSERT INTO parties (name) VALUES (?)', (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Get all party names
def get_parties():
    cursor.execute('SELECT name FROM parties')
    return [row[0] for row in cursor.fetchall()]

# Cast a vote
def cast_vote(username, party_name):
    cursor.execute('SELECT has_voted FROM users WHERE username=?', (username,))
    result = cursor.fetchone()
    if result and result[0] == 1:
        return False
    cursor.execute('UPDATE parties SET votes = votes + 1 WHERE name=?', (party_name,))
    cursor.execute('UPDATE users SET has_voted = 1 WHERE username=?', (username,))
    conn.commit()
    return True

# Check if user has voted
def has_voted(username):
    cursor.execute('SELECT has_voted FROM users WHERE username=?', (username,))
    result = cursor.fetchone()
    return result and result[0] == 1

# Get voting results
def get_results():
    cursor.execute('SELECT name, votes FROM parties ORDER BY votes DESC')
    return cursor.fetchall()
