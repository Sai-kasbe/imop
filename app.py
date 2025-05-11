import streamlit as st
import pandas as pd
import sqlite3

# ===== DATABASE CONNECTION =====
conn = sqlite3.connect('voting_app.db', check_same_thread=False)
cursor = conn.cursor()

# ===== TABLE CREATION =====
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
    conn.commit()

create_tables()

# ===== DATABASE OPERATIONS =====
def add_user(roll_no, name, password, email, phone, image):
    try:
        cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, 0)', (roll_no, name, password, email, phone, image))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(roll_no, password):
    cursor.execute('SELECT * FROM users WHERE roll_no=? AND password=?', (roll_no, password))
    return cursor.fetchone() is not None

def add_candidate(candidate_name, roll_no, dept, year_sem, role, image):
    try:
        cursor.execute('INSERT INTO candidates VALUES (?, ?, ?, ?, ?, ?, 0)', (candidate_name, roll_no, dept, year_sem, role, image))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_candidates_by_role(role):
    cursor.execute('SELECT candidate_name FROM candidates WHERE role=?', (role,))
    return [row[0] for row in cursor.fetchall()]

def cast_vote(roll_no, candidate_name):
    cursor.execute('SELECT has_voted FROM users WHERE roll_no=?', (roll_no,))
    if cursor.fetchone()[0] == 1:
        return False
    cursor.execute('UPDATE candidates SET votes = votes + 1 WHERE candidate_name=?', (candidate_name,))
    cursor.execute('UPDATE users SET has_voted = 1 WHERE roll_no=?', (roll_no,))
    conn.commit()
    return True

def has_voted(roll_no):
    cursor.execute('SELECT has_voted FROM users WHERE roll_no=?', (roll_no,))
    return cursor.fetchone()[0] == 1

def get_results():
    cursor.execute('SELECT candidate_name, role, votes FROM candidates ORDER BY role, votes DESC')
    return cursor.fetchall()

def get_all_users():
    cursor.execute('SELECT roll_no, name, has_voted FROM users')
    return cursor.fetchall()

# ===== STREAMLIT STATE =====
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

def login_admin():
    st.header("Admin Login")
    username = st.text_input("Admin ID")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "22QM1A6721" and password == "Sai7@99499":
            st.session_state["logged_in_user"] = username
            st.session_state["is_admin"] = True
            st.session_state["page"] = "admin"
        else:
            st.error("Invalid admin credentials.")

def login_user():
    st.header("User Login")
    roll_no = st.text_input("Roll Number")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate_user(roll_no, password):
            st.session_state["logged_in_user"] = roll_no
            st.session_state["is_admin"] = False
            st.session_state["page"] = "user"
        else:
            st.error("Invalid credentials.")

def admin_panel():
    st.header("Admin Dashboard")
    with st.expander("📥 Add Candidate"):
        cname = st.text_input("Candidate Name")
        roll = st.text_input("Roll No")
        dept = st.text_input("Department")
        year = st.text_input("Year/Semester")
        role = st.selectbox("Role", ["President", "Vice-President", "Secretary", "Treasury"])
        image = st.text_input("Image URL")
        if st.button("Add Candidate"):
            if add_candidate(cname, roll, dept, year, role, image):
                st.success("Candidate added.")
            else:
                st.error("Candidate already exists.")

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

    if st.button("Logout"):
        st.session_state["page"] = "home"
        st.session_state["logged_in_user"] = None
        st.session_state["is_admin"] = False

def user_panel():
    st.header("User Dashboard")
    roll = st.session_state["logged_in_user"]
    voted = has_voted(roll)
    status = "✅ Voted" if voted else "❌ Not Voted"
    color_class = "status-green" if voted else "status-red"
    st.markdown(f"<p class='{color_class}'>Status: {status}</p>", unsafe_allow_html=True)

    if not voted:
        role = st.selectbox("Choose Role to Vote", ["President", "Vice-President", "Secretary", "Treasury"])
        options = get_candidates_by_role(role)
        if options:
            candidate = st.selectbox("Select Candidate", options)
            if st.button("Cast Vote"):
                if cast_vote(roll, candidate):
                    st.success("Vote recorded!")
                    st.rerun()
                else:
                    st.error("You have already voted.")
        else:
            st.info("No candidates for selected role.")
    else:
        st.info("You have already voted.")

    if st.session_state["results_released"]:
        st.subheader("🗳️ Results")
        results = pd.DataFrame(get_results(), columns=["Candidate", "Role", "Votes"])
        st.dataframe(results)

    if st.button("Logout"):
        st.session_state["page"] = "home"
        st.session_state["logged_in_user"] = None

# ===== ROUTING =====
if st.session_state["page"] == "home":
    home_page()
elif st.session_state["page"] == "register":
    register_user()
elif st.session_state["page"] == "login_admin":
    login_admin()
elif st.session_state["page"] == "login_user":
    login_user()
elif st.session_state["page"] == "admin":
    admin_panel()
elif st.session_state["page"] == "user":
    user_panel()
