# --- app.py ---
import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime
import os

# CONFIG
st.set_page_config(page_title="KGRCET Online Voting System", layout="wide")

# CSS
st.markdown("""
<style>
body {
    background-color: #0D1B2A;
    color: white;
}
.stButton>button {
    background-color: #1B263B;
    color: white;
    border-radius: 10px;
    padding: 0.5rem 1.5rem;
    margin-top: 10px;
}
h1, h2, h3, h4 {
    color: #E0E1DD;
}
</style>
""", unsafe_allow_html=True)

# PASSWORD HASHING
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# DB CONNECTION
def get_connection():
    conn = sqlite3.connect("voting.db", check_same_thread=False)
    return conn, conn.cursor()

# TABLES
def create_tables():
    conn, cursor = get_connection()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        roll_no TEXT PRIMARY KEY,
        name TEXT,
        password TEXT,
        email TEXT,
        phone TEXT,
        image TEXT,
        has_voted INTEGER DEFAULT 0
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS candidates (
        candidate_name TEXT,
        roll_no TEXT PRIMARY KEY,
        department TEXT,
        year_sem TEXT,
        role TEXT,
        image TEXT,
        votes INTEGER DEFAULT 0
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS result_schedule (
        id INTEGER PRIMARY KEY,
        result_date TEXT,
        is_announced INTEGER DEFAULT 0
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS blockchain (
        vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT,
        candidate TEXT,
        vote_hash TEXT,
        timestamp TEXT
    )""")
    conn.commit()
    conn.close()

# AUTH
def authenticate_user(roll_no, password):
    conn, cursor = get_connection()
    cursor.execute("SELECT * FROM users WHERE roll_no=? AND password=?", (roll_no, hash_password(password)))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "roll_no": row[0],
            "name": row[1],
            "email": row[3],
            "phone": row[4],
            "image": row[5],
            "has_voted": row[6]
        }
    return None

def add_user(roll_no, name, password, email, phone, image_path):
    conn, cursor = get_connection()
    try:
        cursor.execute("INSERT INTO users (roll_no, name, password, email, phone, image) VALUES (?, ?, ?, ?, ?, ?)",
                       (roll_no, name, hash_password(password), email, phone, image_path))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# VOTE HASH
def record_vote_hash(roll_no, candidate):
    vote_string = roll_no + candidate + datetime.now().isoformat()
    vote_hash = hashlib.sha256(vote_string.encode()).hexdigest()
    conn, cursor = get_connection()
    cursor.execute("INSERT INTO blockchain (roll_no, candidate, vote_hash, timestamp) VALUES (?, ?, ?, ?)",
                   (roll_no, candidate, vote_hash, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# ADMIN CREDENTIALS
ADMIN_ID = "22QM1A6721"
ADMIN_PASS = hash_password("Sai7@99499")

# USER LOGIN
def user_login():
    st.subheader("👨‍🎓 User Login")
    roll_no = st.text_input("Roll Number")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if not roll_no or not password:
            st.warning("Please enter both Roll Number and Password.")
            return
        user = authenticate_user(roll_no, password)
        if user:
            st.success(f"Welcome, {user['name']}!")
            st.session_state.page = "user_dashboard"
            st.session_state.user_data = user
            st.rerun()
        else:
            st.error("Invalid credentials.")

def user_dashboard():
    user = st.session_state.user_data
    st.header("🗳️ Voting Dashboard")
    st.info(f"Name: {user['name']} | Roll No: {user['roll_no']}")
    if user['has_voted']:
        st.success("Status: ✅ Voted")
    else:
        conn, cursor = get_connection()
        candidates = pd.read_sql("SELECT * FROM candidates", conn)
        selected = st.radio("Select your candidate:", candidates['candidate_name'])
        if st.button("Cast Vote"):
            cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE candidate_name=?", (selected,))
            cursor.execute("UPDATE users SET has_voted = 1 WHERE roll_no=?", (user['roll_no'],))
            conn.commit()
            record_vote_hash(user['roll_no'], selected)
            st.success("Vote cast successfully!")
            st.session_state.user_data['has_voted'] = 1
            st.rerun()

# ADMIN LOGIN
def admin_login():
    st.subheader("🔐 Admin Login")
    username = st.text_input("Admin ID")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == ADMIN_ID and hash_password(password) == ADMIN_PASS:
            st.session_state.page = "admin_dashboard"
            st.success("Admin logged in!")
            st.rerun()
        else:
            st.error("Invalid admin credentials.")

def admin_dashboard():
    st.header("📊 Admin Dashboard")
    tab1, tab2, tab3 = st.tabs(["➕ Add Candidate", "🧑‍💼 Users", "📢 Results"])

    with tab1:
        name = st.text_input("Candidate Name")
        roll = st.text_input("Roll Number")
        dept = st.text_input("Department")
        year = st.text_input("Year/Sem")
        role = st.selectbox("Role", ["President", "Vice-President", "Secretary", "Treasurer"])
        image = st.file_uploader("Image", type=["jpg", "png", "jpeg"])
        if st.button("Add Candidate"):
            if not all([name, roll, dept, year, role, image]):
                st.error("All fields required!")
            else:
                os.makedirs("images", exist_ok=True)
                path = f"images/{image.name}"
                with open(path, "wb") as f:
                    f.write(image.getbuffer())
                conn, cursor = get_connection()
                try:
                    cursor.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?, ?, 0)", 
                        (name, roll, dept, year, role, path))
                    conn.commit()
                    st.success("Candidate added!")
                except sqlite3.IntegrityError:
                    st.error("Duplicate roll number!")

    with tab2:
        conn, _ = get_connection()
        st.dataframe(pd.read_sql("SELECT roll_no, name, email, phone, has_voted FROM users", conn))

    with tab3:
        conn, cursor = get_connection()
        date = st.date_input("Result Date")
        if st.button("Schedule Result"):
            cursor.execute("INSERT OR REPLACE INTO result_schedule (id, result_date, is_announced) VALUES (1, ?, 0)", (str(date),))
            conn.commit()
            st.success("Scheduled!")
        if st.button("Announce Now"):
            cursor.execute("UPDATE result_schedule SET is_announced=1 WHERE id=1")
            conn.commit()
            st.success("Announced!")
        result = cursor.execute("SELECT * FROM result_schedule").fetchone()
        if result:
            st.info(f"Result Date: {result[1]} | Announced: {'Yes' if result[2] else 'No'}")

# REGISTRATION
def user_registration():
    st.subheader("📝 User Registration")
    name = st.text_input("Name")
    roll = st.text_input("Roll No")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    password = st.text_input("Password", type="password")
    image = st.file_uploader("Upload Image")

    if st.button("Register"):
        if not all([name, roll, email, phone, password, image]):
            st.error("All fields required.")
            return
        path = f"images/{image.name}"
        os.makedirs("images", exist_ok=True)
        with open(path, "wb") as f:
            f.write(image.getbuffer())
        if add_user(roll, name, password, email, phone, path):
            st.success("Registration successful!")
        else:
            st.error("User already exists!")

# FORGOT PASSWORD
def forgot_password():
    st.subheader("🔑 Forgot Password")
    roll = st.text_input("Roll No")
    email = st.text_input("Email")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Reset Password"):
        conn, cursor = get_connection()
        cursor.execute("SELECT * FROM users WHERE roll_no=? AND email=?", (roll, email))
        if cursor.fetchone():
            cursor.execute("UPDATE users SET password=? WHERE roll_no=?", (hash_password(new_pass), roll))
            conn.commit()
            st.success("Password updated.")
        else:
            st.error("Invalid roll/email.")

# MAIN
def main():
    create_tables()
    st.title("🏫 KGRCET ONLINE VOTING SYSTEM")

    if "page" not in st.session_state:
        st.session_state.page = "home"

    if st.session_state.page == "user_dashboard":
        user_dashboard()
        if st.button("Logout"):
            st.session_state.page = "home"
            st.rerun()

    elif st.session_state.page == "admin_dashboard":
        admin_dashboard()
        if st.button("Logout"):
            st.session_state.page = "home"
            st.rerun()

    else:
        option = st.sidebar.radio("Navigate", ["Home", "User Login", "Admin Login", "Register", "Forgot Password"])
        if option == "User Login":
            user_login()
        elif option == "Admin Login":
            admin_login()
        elif option == "Register":
            user_registration()
        elif option == "Forgot Password":
            forgot_password()
        else:
            st.markdown("Welcome to KGRCET’s secure, blockchain-based online election system.")

if __name__ == "__main__":
    main()
