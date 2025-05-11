import sqlite3
from datetime import datetime
import hashlib
import os

# ✅ Delete old database file if exists (only for development/testing)
if os.path.exists("database.py"):
    os.remove("database.py")

# ✅ Connect to the new database
conn = sqlite3.connect('voting_app.db', check_same_thread=False)
cursor = conn.cursor()

# ✅ Create necessary tables
def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            roll_no TEXT PRIMARY KEY,
            name TEXT,
            password TEXT,
            email TEXT,
            phone TEXT,
            image TEXT,
            has_voted INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            candidate_name TEXT,
            roll_no TEXT PRIMARY KEY,
            department TEXT,
            year_sem TEXT,
            role TEXT,
            image TEXT,
            votes INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS result_schedule (
            id INTEGER PRIMARY KEY,
            result_date TEXT,
            is_announced INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blockchain (
            vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT,
            candidate TEXT,
            vote_hash TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()

# ✅ Call create_tables at startup
create_tables()

# ✅ Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ✅ Add a new user
def add_user(roll_no, name, password, email, phone, image_path):
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, 0)", 
                       (roll_no, name, hash_password(password), email, phone, image_path))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# ✅ Authenticate user
def authenticate_user(roll_no, password):
    cursor.execute("SELECT * FROM users WHERE roll_no=? AND password=?", 
                   (roll_no, hash_password(password)))
    row = cursor.fetchone()
    return row

# ✅ Check if user has voted
def has_voted(roll_no):
    cursor.execute("SELECT has_voted FROM users WHERE roll_no=?", (roll_no,))
    result = cursor.fetchone()
    return result and result[0] == 1

# ✅ Record vote
def cast_vote(roll_no, candidate_name):
    if has_voted(roll_no):
        return False
    cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE candidate_name=?", (candidate_name,))
    cursor.execute("UPDATE users SET has_voted = 1 WHERE roll_no=?", (roll_no,))
    conn.commit()
    return True

# ✅ Add candidate
def add_candidate(candidate_name, roll_no, department, year_sem, role, image_path):
    try:
        cursor.execute('''INSERT INTO candidates 
            (candidate_name, roll_no, department, year_sem, role, image, votes)
            VALUES (?, ?, ?, ?, ?, ?, 0)''',
            (candidate_name, roll_no, department, year_sem, role, image_path))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# ✅ Get all candidates
def get_candidates():
    cursor.execute("SELECT * FROM candidates")
    return cursor.fetchall()

# ✅ Record blockchain vote hash
def record_vote_hash(roll_no, candidate):
    vote_string = roll_no + candidate + datetime.now().isoformat()
    vote_hash = hashlib.sha256(vote_string.encode()).hexdigest()
    cursor.execute('''INSERT INTO blockchain (roll_no, candidate, vote_hash, timestamp)
                      VALUES (?, ?, ?, ?)''',
                   (roll_no, candidate, vote_hash, datetime.now().isoformat()))
    conn.commit()

# ✅ Get results
def get_results():
    cursor.execute("SELECT candidate_name, votes FROM candidates ORDER BY votes DESC")
    return cursor.fetchall()

# ✅ Get all users
def get_all_users():
    cursor.execute("SELECT roll_no, name, email, phone, has_voted FROM users")
    return cursor.fetchall()
