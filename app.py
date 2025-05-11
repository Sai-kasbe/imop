import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# ===== APP CONFIGURATION =====
st.set_page_config(page_title="College Voting System", layout="centered")
st.markdown("<style>body { background-color: #0D1B2A; color: white; }</style>", unsafe_allow_html=True)

# ===== PASSWORD HASHING =====
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ===== DATABASE CONNECTION =====
def get_connection():
    conn = sqlite3.connect('voting_app.db', check_same_thread=False)
    return conn, conn.cursor()

# ===== TABLE CREATION =====
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
        candidate_name TEXT,
        roll_no TEXT PRIMARY KEY,
        department TEXT,
        year_sem TEXT,
        role TEXT,
        image TEXT,
        votes INTEGER DEFAULT 0
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS result_schedule (
        id INTEGER PRIMARY KEY,
        result_date TEXT,
        is_announced INTEGER DEFAULT 0
    )''')

    conn.commit()
    conn.close()

# ===== ADMIN CREDENTIALS =====
ADMIN_ID = "22QM1A6721"
ADMIN_PASS = hash_password("Sai7@99499")

# ===== USER AUTHENTICATION =====
def authenticate_user(roll_no, password):
    conn, cursor = get_connection()
    cursor.execute("SELECT * FROM users WHERE roll_no=? AND password=?", (roll_no, hash_password(password)))
    return cursor.fetchone()

# ===== UI SECTIONS =====
def show_admin_login():
    st.subheader("🔐 Admin Login")
    username = st.text_input("Admin ID")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == ADMIN_ID and hash_password(password) == ADMIN_PASS:
            st.success("Admin Logged In!")
            admin_dashboard()
        else:
            st.error("Invalid admin credentials!")

def admin_dashboard():
    st.header("📊 Admin Dashboard")

    tab1, tab2, tab3 = st.tabs(["➕ Add Candidate", "🧑‍💼 Registered Users", "📢 Result Settings"])

    with tab1:
        st.subheader("Add New Candidate (Party)")
        name = st.text_input("Candidate Name")
        roll_no = st.text_input("Roll No (Unique)")
        dept = st.text_input("Department")
        year_sem = st.text_input("Year/Sem")
        role = st.selectbox("Role", ["President", "Vice-President", "Secretary", "Treasurer"])
        image = st.text_input("Image URL (optional)")
        if st.button("Add Candidate"):
            conn, cursor = get_connection()
            try:
                cursor.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?, ?, 0)",
                               (name, roll_no, dept, year_sem, role, image))
                conn.commit()
                st.success("Candidate Added!")
            except sqlite3.IntegrityError:
                st.error("Candidate with this roll number already exists!")

    with tab2:
        conn, cursor = get_connection()
        st.subheader("All Registered Users")
        df = pd.read_sql("SELECT roll_no, name, email, phone, has_voted FROM users", conn)
        st.dataframe(df)

    with tab3:
        conn, cursor = get_connection()
        st.subheader("Schedule or Announce Result")
        new_date = st.date_input("Result Date")
        if st.button("Schedule Result"):
            cursor.execute("INSERT OR REPLACE INTO result_schedule (id, result_date, is_announced) VALUES (1, ?, 0)", (str(new_date),))
            conn.commit()
            st.success("Result Scheduled!")

        if st.button("Announce Now"):
            cursor.execute("UPDATE result_schedule SET is_announced=1 WHERE id=1")
            conn.commit()
            st.success("Result Announced!")

        result = cursor.execute("SELECT * FROM result_schedule").fetchone()
        if result:
            st.info(f"Scheduled Date: {result[1]} | Announced: {'Yes' if result[2] else 'No'}")

def show_user_login():
    st.subheader("🧑 User Login")
    roll_no = st.text_input("Roll Number")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate_user(roll_no, password)
        if user:
            st.success(f"Welcome {user[1]}!")
            user_dashboard(user)
        else:
            st.error("Invalid credentials!")

def user_dashboard(user):
    st.header("🗳️ Vote Dashboard")
    if user[6]:  # has_voted = 1
        st.info("Status: ✅ VOTED", icon="✅")
    else:
        st.warning("Status: ❌ NOT VOTED", icon="⚠️")
        conn, cursor = get_connection()
        candidates = pd.read_sql("SELECT * FROM candidates", conn)
        selected = st.radio("Choose your candidate:", candidates['candidate_name'])
        if st.button("Cast Vote"):
            cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE candidate_name=?", (selected,))
            cursor.execute("UPDATE users SET has_voted=1 WHERE roll_no=?", (user[0],))
            conn.commit()
            st.success("Vote Cast Successfully!")

def show_registration():
    st.subheader("📝 New User Registration")
    name = st.text_input("Full Name")
    roll_no = st.text_input("Roll Number (Unique)")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    password = st.text_input("Password", type="password")
    image = st.text_input("Image URL (optional)")

    if st.button("Register"):
        conn, cursor = get_connection()
        try:
            cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, 0)",
                           (roll_no, name, hash_password(password), email, phone, image))
            conn.commit()
            st.success("Registered successfully!")
        except sqlite3.IntegrityError:
            st.error("User with this roll number already exists!")

def show_forgot_password():
    st.subheader("🔑 Forgot Password")
    roll_no = st.text_input("Enter your registered Roll Number")
    email = st.text_input("Enter your registered Email")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Reset Password"):
        conn, cursor = get_connection()
        cursor.execute("SELECT * FROM users WHERE roll_no=? AND email=?", (roll_no, email))
        if cursor.fetchone():
            cursor.execute("UPDATE users SET password=? WHERE roll_no=?", (hash_password(new_pass), roll_no))
            conn.commit()
            st.success("Password updated successfully!")
        else:
            st.error("Invalid roll number or email!")

# ===== MAIN APP INTERFACE =====
def main():
    st.title("🏛️ College Voting System")
    create_tables()

    option = st.sidebar.radio("Navigation", ["User Login", "Admin Login", "Register", "Forgot Password"])

    if option == "Admin Login":
        show_admin_login()
    elif option == "User Login":
        show_user_login()
    elif option == "Register":
        show_registration()
    elif option == "Forgot Password":
        show_forgot_password()

if __name__ == "__main__":
    main()
