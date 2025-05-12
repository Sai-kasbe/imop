import sqlite3
import os

DB_NAME = "voting.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    return conn, cursor

def create_tables():
    conn, cursor = get_connection()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        roll_no TEXT PRIMARY KEY,
        name TEXT,
        password TEXT,
        email TEXT,
        phone TEXT,
        image TEXT,
        has_voted INTEGER DEFAULT 0
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        role TEXT,
        image TEXT,
        votes INTEGER DEFAULT 0
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        declared INTEGER DEFAULT 0
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS vote_hashes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT,
        candidate TEXT,
        hash TEXT
    )''')

    conn.commit()
    conn.close()

def add_user(roll_no, name, password, email, phone, image):
    conn, cursor = get_connection()
    cursor.execute("INSERT INTO users (roll_no, name, password, email, phone, image) VALUES (?, ?, ?, ?, ?, ?)",
                   (roll_no, name, password, email, phone, image))
    conn.commit()
    conn.close()

def get_user(roll_no, password):
    conn, cursor = get_connection()
    cursor.execute("SELECT * FROM users WHERE roll_no=? AND password=?", (roll_no, password))
    user = cursor.fetchone()
    conn.close()
    return user

def add_candidate(name, role, image):
    conn, cursor = get_connection()
    cursor.execute("INSERT INTO candidates (name, role, image) VALUES (?, ?, ?)", (name, role, image))
    conn.commit()
    conn.close()

def get_all_candidates():
    conn, cursor = get_connection()
    cursor.execute("SELECT * FROM candidates")
    rows = cursor.fetchall()
    conn.close()
    return rows

def record_vote_hash(roll_no, candidate, hash):
    conn, cursor = get_connection()
    cursor.execute("INSERT INTO vote_hashes (roll_no, candidate, hash) VALUES (?, ?, ?)", (roll_no, candidate, hash))
    conn.commit()
    conn.close()
