import streamlit as st
import pandas as pd
import sqlite3

# === DATABASE FUNCTIONS ===

conn = sqlite3.connect('voting_app.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables

def create_tables():
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
        candidate_name TEXT,
        roll_no TEXT PRIMARY KEY,
        department TEXT,
        year_sem TEXT,
        role TEXT,
        image TEXT,
        votes INTEGER DEFAULT 0
    )''')
    conn.commit()

def add_user(roll_no, name, password, email, phone, image):
    try:
        cursor.execute('''INSERT INTO users (roll_no, name, password, email, phone, image) 
                          VALUES (?, ?, ?, ?, ?, ?)''', (roll_no, name, password, email, phone, image))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(roll_no, password):
    cursor.execute('SELECT * FROM users WHERE roll_no=? AND password=?', (roll_no, password))
    return cursor.fetchone() is not None

def add_candidate(candidate_name, roll_no, department, year_sem, role, image):
    try:
        cursor.execute('''INSERT INTO candidates (candidate_name, roll_no, department, year_sem, role, image) 
                          VALUES (?, ?, ?, ?, ?, ?)''', 
                       (candidate_name, roll_no, department, year_sem, role, image))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_candidates_by_role(role):
    cursor.execute('SELECT candidate_name FROM candidates WHERE role=?', (role,))
    return [row[0] for row in cursor.fetchall()]

def cast_vote(roll_no, candidate_name):
    cursor.execute('SELECT has_voted FROM users WHERE roll_no=?', (roll_no,))
    result = cursor.fetchone()
    if result and result[0] == 1:
        return False
    cursor.execute('UPDATE candidates SET votes = votes + 1 WHERE candidate_name=?', (candidate_name,))
    cursor.execute('UPDATE users SET has_voted = 1 WHERE roll_no=?', (roll_no,))
    conn.commit()
    return True

def has_voted(roll_no):
    cursor.execute('SELECT has_voted FROM users WHERE roll_no=?', (roll_no,))
    result = cursor.fetchone()
    return result and result[0] == 1

def get_results():
    cursor.execute('SELECT candidate_name, role, votes FROM candidates ORDER BY role, votes DESC')
    return cursor.fetchall()

def get_all_users():
    cursor.execute('SELECT roll_no, name, has_voted FROM users')
    return cursor.fetchall()

# === STREAMLIT INTERFACE ===

create_tables()

if "page" not in st.session_state:
    st.session_state["page"] = "home"
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "results_released" not in st.session_state:
    st.session_state["results_released"] = False
if "result_date" not in st.session_state:
    st.session_state["result_date"] = ""

st.markdown("""
    <style>
        body { background-color: #001f3f; color: white; }
        .title { color: #FFDC00; font-size: 36px; text-align: center; }
        .subtitle { color: #7FDBFF; font-size: 24px; text-align: center; }
        .status-red { color: red; font-weight: bold; }
        .status-green { color: lightgreen; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# You can now continue with UI logic using updated fields and buttons...
# Use st.file_uploader for images, st.date_input for result scheduling, etc.
# Send password recovery emails with SMTP setup (not included in this snippet).
# You may request the next part (admin panel, user panel, or forgot password flow).
