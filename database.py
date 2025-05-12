import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('voting_app.db', check_same_thread=False)
cursor = conn.cursor()

# === Create Tables ===
def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            roll_no TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT,
            email TEXT,
            phone TEXT,
            image TEXT,
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

# === User Management ===
def add_user(roll_no, password, name, email, phone, image_path):
    try:
        cursor.execute('''
            INSERT INTO users (roll_no, password, name, email, phone, image)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (roll_no, password, name, email, phone, image_path))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(roll_no, password):
    cursor.execute('SELECT * FROM users WHERE roll_no=? AND password=?', (roll_no, password))
    return cursor.fetchone() is not None

def update_password_by_email(email, new_password):
    cursor.execute('UPDATE users SET password=? WHERE email=?', (new_password, email))
    conn.commit()

# === Voting Functionality ===
def add_party(name):
    try:
        cursor.execute('INSERT INTO parties (name) VALUES (?)', (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_parties():
    cursor.execute('SELECT name FROM parties')
    return [row[0] for row in cursor.fetchall()]

def cast_vote(roll_no, party_name):
    cursor.execute('SELECT has_voted FROM users WHERE roll_no=?', (roll_no,))
    result = cursor.fetchone()
    if result and result[0] == 1:
        return False  # Already voted
    cursor.execute('UPDATE parties SET votes = votes + 1 WHERE name=?', (party_name,))
    cursor.execute('UPDATE users SET has_voted = 1 WHERE roll_no=?', (roll_no,))
    conn.commit()
    return True

def has_voted(roll_no):
    cursor.execute('SELECT has_voted FROM users WHERE roll_no=?', (roll_no,))
    result = cursor.fetchone()
    return result and result[0] == 1

def get_results():
    cursor.execute('SELECT name, votes FROM parties ORDER BY votes DESC')
    return cursor.fetchall()

def get_all_users():
    cursor.execute('SELECT roll_no, has_voted FROM users')
    return cursor.fetchall()
