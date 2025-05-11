import streamlit as st
import pandas as pd
import sqlite3

# ===== DATABASE CONNECTION =====
def get_connection():
    conn = sqlite3.connect('voting_app.db', check_same_thread=False)
    return conn, conn.cursor()

# ===== TABLE CREATION =====
def create_tables():
    conn, cursor = get_connection()
    try:
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
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

create_tables()

# ===== DATABASE OPERATIONS =====
def add_user(roll_no, name, password, email, phone, image):
    conn, cursor = get_connection()
    try:
        cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, 0)', (roll_no, name, password, email, phone, image))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(roll_no, password):
    conn, cursor = get_connection()
    try:
        cursor.execute('SELECT * FROM users WHERE roll_no=? AND password=?', (roll_no, password))
        return cursor.fetchone() is not None
    finally:
        conn.close()

def add_candidate(candidate_name, roll_no, dept, year_sem, role, image):
    conn, cursor = get_connection()
    try:
        cursor.execute('INSERT INTO candidates VALUES (?, ?, ?, ?, ?, ?, 0)', (candidate_name, roll_no, dept, year_sem, role, image))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_candidates_by_role(role):
    conn, cursor = get_connection()
    try:
        cursor.execute('SELECT candidate_name FROM candidates WHERE role=?', (role,))
        return [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()

def cast_vote(roll_no, candidate_name):
    conn, cursor = get_connection()
    try:
        cursor.execute('SELECT has_voted FROM users WHERE roll_no=?', (roll_no,))
        result = cursor.fetchone()
        if result and result[0] == 1:
            return False
        cursor.execute('UPDATE candidates SET votes = votes + 1 WHERE candidate_name=?', (candidate_name,))
        cursor.execute('UPDATE users SET has_voted = 1 WHERE roll_no=?', (roll_no,))
        conn.commit()
        return True
    finally:
        conn.close()

def has_voted(roll_no):
    conn, cursor = get_connection()
    try:
        cursor.execute('SELECT has_voted FROM users WHERE roll_no=?', (roll_no,))
        result = cursor.fetchone()
        return result and result[0] == 1
    finally:
        conn.close()

def get_results():
    conn, cursor = get_connection()
    try:
        cursor.execute('SELECT candidate_name, role, votes FROM candidates ORDER BY role, votes DESC')
        return cursor.fetchall()
    finally:
        conn.close()

def get_all_users():
    conn, cursor = get_connection()
    try:
        cursor.execute('SELECT roll_no, name, has_voted FROM users')
        return cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

# ===== STREAMLIT STATE =====
st.session_state.setdefault("page", "home")
st.session_state.setdefault("logged_in_user", None)
st.session_state.setdefault("is_admin", False)
st.session_state.setdefault("results_released", False)
st.session_state.setdefault("result_date", "")

# ===== UI STYLE =====
st.markdown("""
    <style>
        body { background-color: #001f3f; color: white; }
        .title { color: #FFDC00; font-size: 36px; text-align: center; }
        .subtitle { color: #7FDBFF; font-size: 24px; text-align: center; }
        .status-red { color: red; font-weight: bold; }
        .status-green { color: lightgreen; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ===== PAGES =====
def home_page():
    st.markdown("<h1 class='title'>🗳️ College Voting Portal</h1>", unsafe_allow_html=True)
    if st.button("Admin Login"):
        st.session_state["page"] = "login_admin"
    if st.button("User Login"):
        st.session_state["page"] = "login_user"
    if st.button("Register User"):
        st.session_state["page"] = "register"

def register_user():
    st.header("User Registration")
    name = st.text_input("Name")
    roll_no = st.text_input("Roll No (Unique)")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    password = st.text_input("Password", type="password")
    image = st.text_input("Image URL (optional)")
    if st.button("Register"):
        if all([name, roll_no, email, phone, password]):
            if add_user(roll_no, name, password, email, phone, image):
                st.success("Registered successfully!")
                st.session_state["page"] = "login_user"
            else:
                st.error("Roll No already exists.")
        else:
            st.warning("All fields are required.")

def admin_panel():
    st.header("Admin Dashboard")
    st.subheader("📊 Election Results")
    
    if st.button("Release Results"):
        st.session_state["results_released"] = True
        st.success("Results released!")

    if st.session_state["results_released"]:
        df = pd.DataFrame(get_results(), columns=["Candidate", "Role", "Votes"])
        st.dataframe(df)

    st.subheader("👥 Registered Users")
    users = get_all_users()
    df_users = pd.DataFrame(users, columns=["Roll No", "Name", "Status"])
    df_users["Status"] = df_users["Status"].apply(lambda x: "✅ Voted" if x else "❌ Not Voted")
    st.dataframe(df_users)

# ===== ROUTING =====
page_mapping = {
    "home": home_page,
    "register": register_user,
    "login_admin": login_admin,
    "admin": admin_panel
}

page_mapping.get(st.session_state["page"], home_page)()
