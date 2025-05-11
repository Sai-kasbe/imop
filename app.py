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
