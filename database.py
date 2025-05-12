import sqlite3
from datetime import datetime
import hashlib
import os

# =================== DATABASE CONNECTION ===================
def get_connection():
    conn = sqlite3.connect("voting_app.db", check_same_thread=False)
    cursor = conn.cursor()
    return conn, cursor

# =================== HASHING FUNCTION ===================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =================== CREATE TABLES ===================
def create_tables():
    conn, cursor = get_connection()

    # Drop existing users table (ONLY for development/reset)
    cursor.execute("DROP TABLE IF EXISTS users")

    # Create fresh users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            roll_no TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            image TEXT,
            has_voted INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            candidate_name TEXT,
            roll_no TEXT PRIMARY KEY,
            department TEXT,
            year_sem TEXT,
            role TEXT,
            image TEXT,
            votes INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS result_schedule (
            id INTEGER PRIMARY KEY,
            result_date TEXT,
            is_announced INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blockchain (
            vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT,
            candidate TEXT,
            vote_hash TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()

# =================== USER OPERATIONS ===================
def add_user(roll_no, name, password, email, phone, image_path):
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            INSERT INTO users (roll_no, name, password, email, phone, image)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (roll_no, name, hash_password(password), email, phone, image_path))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(roll_no, password):
    conn, cursor = get_connection()
    cursor.execute("SELECT * FROM users WHERE roll_no=? AND password=?", 
                   (roll_no, hash_password(password)))
    row = cursor.fetchone()
    conn.close()
    return row

def has_voted(roll_no):
    conn, cursor = get_connection()
    cursor.execute("SELECT has_voted FROM users WHERE roll_no=?", (roll_no,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1

# =================== VOTING ===================
def cast_vote(roll_no, candidate_name):
    if has_voted(roll_no):
        return False
    conn, cursor = get_connection()
    cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE candidate_name=?", (candidate_name,))
    cursor.execute("UPDATE users SET has_voted = 1 WHERE roll_no=?", (roll_no,))
    conn.commit()
    conn.close()
    record_vote_hash(roll_no, candidate_name)
    return True

# =================== CANDIDATE ===================
def add_candidate(candidate_name, roll_no, department, year_sem, role, image_path):
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            INSERT INTO candidates (candidate_name, roll_no, department, year_sem, role, image, votes)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (candidate_name, roll_no, department, year_sem, role, image_path))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_candidates():
    conn, cursor = get_connection()
    cursor.execute("SELECT * FROM candidates")
    results = cursor.fetchall()
    conn.close()
    return results

# =================== BLOCKCHAIN ===================
def record_vote_hash(roll_no, candidate):
    vote_string = roll_no + candidate + datetime.now().isoformat()
    vote_hash = hashlib.sha256(vote_string.encode()).hexdigest()
    conn, cursor = get_connection()
    cursor.execute("INSERT INTO blockchain (roll_no, candidate, vote_hash, timestamp) VALUES (?, ?, ?, ?)",
                   (roll_no, candidate, vote_hash, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# =================== RESULTS ===================
def get_results():
    conn, cursor = get_connection()
    cursor.execute("SELECT candidate_name, votes FROM candidates ORDER BY votes DESC")
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_users():
    conn, cursor = ge
