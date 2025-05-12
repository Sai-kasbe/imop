import sqlite3
from datetime import datetime
import hashlib

# Database Connection
conn = sqlite3.connect('voting.db', check_same_thread=False)
c = conn.cursor()

# === TABLES CREATION ===

# Users Table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    roll_no TEXT PRIMARY KEY,
    name TEXT,
    password TEXT,
    phone TEXT,
    image TEXT,
    has_voted INTEGER DEFAULT 0
)
''')

# Candidates Table
c.execute('''
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    roll_no TEXT UNIQUE,
    department TEXT,
    year_sem TEXT,
    role TEXT,
    image TEXT,
    votes INTEGER DEFAULT 0
)
''')

# Admin Table
c.execute('''
CREATE TABLE IF NOT EXISTS admin (
    username TEXT PRIMARY KEY,
    password TEXT
)
''')

# Result Schedule Table
c.execute('''
CREATE TABLE IF NOT EXISTS result_schedule (
    id INTEGER PRIMARY KEY,
    result_date TEXT,
    is_announced INTEGER DEFAULT 0
)
''')

# Blockchain Votes Table
c.execute('''
CREATE TABLE IF NOT EXISTS blockchain (
    vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT,
    candidate TEXT,
    vote_hash TEXT,
    timestamp TEXT
)
''')

conn.commit()

# === ADMIN ACCOUNT ===
def initialize_admin():
    c.execute("SELECT * FROM admin WHERE username = ?", ("22QM1A6721",))
    if not c.fetchone():
        hashed = hashlib.sha256("Sai7@99499".encode()).hexdigest()
        c.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("22QM1A6721", hashed))
        conn.commit()

# === USER FUNCTIONS ===
def register_user(roll_no, name, phone, password, image):
    c.execute("SELECT * FROM users WHERE roll_no=?", (roll_no,))
    if c.fetchone():
        return False  # Already exists
    c.execute('''
        INSERT INTO users (roll_no, name, phone, password, image, has_voted)
        VALUES (?, ?, ?, ?, ?, 0)
    ''', (roll_no, name, phone, password, image))
    conn.commit()
    return True

def login_user(roll_no, password):
    c.execute("SELECT * FROM users WHERE roll_no=? AND password=?", (roll_no, password))
    return c.fetchone()

def update_password(roll_no, new_password):
    c.execute("UPDATE users SET password=? WHERE roll_no=?", (new_password, roll_no))
    conn.commit()

def get_user(roll_no):
    c.execute("SELECT * FROM users WHERE roll_no=?", (roll_no,))
    return c.fetchone()

# === ADMIN FUNCTIONS ===
def login_admin(username, password):
    c.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
    return c.fetchone()

# === CANDIDATE FUNCTIONS ===
def add_candidate(name, roll_no, dept, year_sem, role, image):
    c.execute('''
        INSERT INTO candidates (name, roll_no, department, year_sem, role, image, votes)
        VALUES (?, ?, ?, ?, ?, ?, 0)
    ''', (name, roll_no, dept, year_sem, role, image))
    conn.commit()

def get_candidates():
    c.execute("SELECT * FROM candidates")
    return c.fetchall()

def get_candidates_by_role(role):
    c.execute("SELECT * FROM candidates WHERE role=?", (role,))
    return c.fetchall()

def vote(roll_no, candidate_roll_no):
    c.execute("UPDATE candidates SET votes = votes + 1 WHERE roll_no=?", (candidate_roll_no,))
    c.execute("UPDATE users SET has_voted=1 WHERE roll_no=?", (roll_no,))
    conn.commit()

# === RESULTS AND USERS ===
def get_all_users():
    c.execute("SELECT roll_no, name, phone, has_voted FROM users")
    return c.fetchall()

def get_results():
    c.execute("SELECT role, name, votes FROM candidates")
    return c.fetchall()

# === SCHEDULING RESULTS ===
def schedule_result(date):
    c.execute("INSERT OR REPLACE INTO result_schedule (id, result_date, is_announced) VALUES (1, ?, 0)", (date,))
    conn.commit()

def announce_result():
    c.execute("UPDATE result_schedule SET is_announced=1 WHERE id=1")
    conn.commit()

def get_result_schedule():
    c.execute("SELECT * FROM result_schedule WHERE id=1")
    return c.fetchone()

# === BLOCKCHAIN LOGGING ===
def record_vote_block(roll_no, candidate_name):
    vote_string = roll_no + candidate_name + datetime.now().isoformat()
    vote_hash = hashlib.sha256(vote_string.encode()).hexdigest()
    timestamp = datetime.now().isoformat()
    c.execute("INSERT INTO blockchain (roll_no, candidate, vote_hash, timestamp) VALUES (?, ?, ?, ?)",
              (roll_no, candidate_name, vote_hash, timestamp))
    conn.commit()

# Init
initialize_admin()
