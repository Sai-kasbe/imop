import streamlit as st
import pandas as pd
import sqlite3

# === DATABASE FUNCTIONS ===

conn = sqlite3.connect('voting_app.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables
def create_tables():
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, has_voted INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS parties (name TEXT PRIMARY KEY, votes INTEGER DEFAULT 0)''')
    conn.commit()

def add_user(username, password):
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username, password):
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    return cursor.fetchone() is not None

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

def cast_vote(username, party_name):
    cursor.execute('SELECT has_voted FROM users WHERE username=?', (username,))
    result = cursor.fetchone()
    if result and result[0] == 1:
        return False
    cursor.execute('UPDATE parties SET votes = votes + 1 WHERE name=?', (party_name,))
    cursor.execute('UPDATE users SET has_voted = 1 WHERE username=?', (username,))
    conn.commit()
    return True

def has_voted(username):
    cursor.execute('SELECT has_voted FROM users WHERE username=?', (username,))
    result = cursor.fetchone()
    return result and result[0] == 1

def get_results():
    cursor.execute('SELECT name, votes FROM parties ORDER BY votes DESC')
    return cursor.fetchall()

def get_all_users():
    cursor.execute('SELECT username, has_voted FROM users')
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
        body { background-color: #f0f2f6; }
        .main { background-color: white; border-radius: 10px; padding: 30px; }
        .title { color: #4B8BBE; font-size: 36px; }
        .subtitle { color: #306998; font-size: 24px; }
        .button { background-color: #4CAF50; color: white; border: none; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# Pages
def home_page():
    st.markdown("<h1 class='title'>🗳️ Online College Election Portal</h1>", unsafe_allow_html=True)
    st.info("Welcome to the secure and transparent voting system.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Login"):
            st.session_state["page"] = "login"
            st.rerun()
    with col2:
        if st.button("📝 Register"):
            st.session_state["page"] = "register"
            st.rerun()

def register_page():
    st.markdown("<h2 class='subtitle'>New User Registration</h2>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        if not username or not password:
            st.warning("Please fill all fields.")
        elif add_user(username, password):
            st.success("Registration successful. Please login.")
            st.session_state["page"] = "login"
            st.rerun()
        else:
            st.error("Username already taken.")
    if st.button("⬅ Back"):
        st.session_state["page"] = "home"
        st.rerun()

def login_page():
    st.markdown("<h2 class='subtitle'>User/Admin Login</h2>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "22QM1A6721" and password == "Sai7@99499":
            st.session_state["logged_in_user"] = username
            st.session_state["is_admin"] = True
            st.session_state["page"] = "admin"
            st.success("Welcome Admin!")
            st.rerun()
        elif authenticate_user(username, password):
            st.session_state["logged_in_user"] = username
            st.session_state["is_admin"] = False
            st.session_state["page"] = "user"
            st.success("Login successful.")
            st.rerun()
        else:
            st.error("Invalid credentials.")
    if st.button("⬅ Back"):
        st.session_state["page"] = "home"
        st.rerun()

def admin_panel():
    st.markdown("<h2 class='subtitle'>Admin Dashboard</h2>", unsafe_allow_html=True)
    new_party = st.text_input("Add Party Name")
    if st.button("Add Party"):
        if add_party(new_party):
            st.success(f"'{new_party}' added.")
        else:
            st.warning("Party already exists.")
    st.write("### Registered Parties:")
    st.write(get_parties())
    st.write("### Registered Users:")
    df = pd.DataFrame(get_all_users(), columns=["Username", "Voted"])
    st.dataframe(df)
    st.text_input("Set Result Date (YYYY-MM-DD)", value=st.session_state["result_date"], key="result_date")
    if st.button("Release Results"):
        st.session_state["results_released"] = True
        st.success("Results made public.")
    if st.session_state["results_released"]:
        st.write("### Voting Results")
        results = get_results()
        if results:
            st.dataframe(pd.DataFrame(results, columns=["Party", "Votes"]))
    if st.button("Logout"):
        st.session_state["page"] = "home"
        st.session_state["logged_in_user"] = None
        st.session_state["is_admin"] = False
        st.rerun()

def user_panel():
    st.markdown("<h2 class='subtitle'>Voter Panel</h2>", unsafe_allow_html=True)
    username = st.session_state["logged_in_user"]
    voted = has_voted(username)
    status = "✅ Voted" if voted else "❌ Not Voted"
    color = "green" if voted else "red"
    st.markdown(f"**Status:** <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
    if not voted:
        options = get_parties()
        if options:
            choice = st.selectbox("Select Party to Vote", options)
            if st.button("Submit Vote"):
                if cast_vote(username, choice):
                    st.success("Vote Recorded!")
                    st.rerun()
        else:
            st.warning("No parties available.")
    if st.session_state["results_released"]:
        st.write("### Live Results")
        st.dataframe(pd.DataFrame(get_results(), columns=["Party", "Votes"]))
    elif st.session_state["result_date"]:
        st.info(f"Results scheduled for {st.session_state['result_date']}")
    if st.button("Logout"):
        st.session_state["page"] = "home"
        st.session_state["logged_in_user"] = None
        st.session_state["is_admin"] = False
        st.rerun()

# Routing
if st.session_state["logged_in_user"] is None:
    if st.session_state["page"] == "home":
        home_page()
    elif st.session_state["page"] == "login":
        login_page()
    elif st.session_state["page"] == "register":
        register_page()
else:
    if st.session_state["is_admin"]:
        admin_panel()
    else:
        user_panel()
