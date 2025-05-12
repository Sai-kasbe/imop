import streamlit as st
import pandas as pd
import hashlib
import os
from database import create_tables, add_user, get_user, add_candidate, get_all_candidates, record_vote_hash, get_connection

create_tables()

def hash_vote(roll_no, candidate_name):
    return hashlib.sha256(f"{roll_no}-{candidate_name}".encode()).hexdigest()

def save_image(uploaded_file):
    if uploaded_file is not None:
        os.makedirs("images", exist_ok=True)
        file_path = os.path.join("images", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return ""

def admin_login():
    st.subheader("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "22QM1A6721" and password == "Sai7@99499":
            st.session_state.admin_logged_in = True
            st.success("Logged in as Admin")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

def admin_dashboard():
    st.title("Admin Dashboard")

    menu = ["Add Candidate", "View Voters", "Schedule/Announce Results", "Logout"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Candidate":
        st.subheader("Add Candidate")
        name = st.text_input("Candidate Name")
        role = st.text_input("Role")
        image = st.file_uploader("Upload Candidate Image", type=["jpg", "jpeg", "png"])
        if st.button("Add Candidate"):
            image_path = save_image(image)
            add_candidate(name, role, image_path)
            st.success("Candidate added successfully")

    elif choice == "View Voters":
        conn, cursor = get_connection()
        cursor.execute("SELECT roll_no, name, has_voted FROM users")
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=["Roll No", "Name", "Has Voted"])
        st.dataframe(df)

    elif choice == "Schedule/Announce Results":
        conn, cursor = get_connection()
        cursor.execute("SELECT name, votes FROM candidates ORDER BY votes DESC")
        results = cursor.fetchall()
        if results:
            df = pd.DataFrame(results, columns=["Candidate", "Votes"])
            st.bar_chart(df.set_index("Candidate"))
        else:
            st.warning("No results to show")

    elif choice == "Logout":
        st.session_state.admin_logged_in = False
        st.experimental_rerun()

def user_register():
    st.subheader("Register")
    name = st.text_input("Name")
    roll_no = st.text_input("Roll Number")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    password = st.text_input("Password", type="password")
    image = st.file_uploader("Upload Your Image", type=["jpg", "jpeg", "png"])
    if st.button("Register"):
        image_path = save_image(image)
        try:
            add_user(roll_no, name, password, email, phone, image_path)
            st.success("Registered successfully. Please login.")
        except Exception as e:
            st.error("User already exists or error occurred.")

def user_login():
    st.subheader("User Login")
    roll_no = st.text_input("Roll Number")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = get_user(roll_no, password)
        if user:
            st.session_state.user_logged_in = True
            st.session_state.user_data = {
                "roll_no": user[0],
                "name": user[1],
                "has_voted": user[6]
            }
            st.success(f"Welcome, {user[1]}")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

def user_dashboard():
    st.title("User Dashboard")
    user = st.session_state.user_data
    st.info(f"Logged in as {user['name']} ({user['roll_no']})")

    if user['has_voted']:
        st.success("You have already voted. Thank you!")
    else:
        candidates = pd.DataFrame(get_all_candidates(), columns=["id", "name", "role", "image", "votes"])
        if candidates.empty:
            st.warning("No candidates found.")
        else:
            selected = st.radio("Select your candidate:", candidates["name"])
            if st.button("Cast Vote"):
                conn, cursor = get_connection()
                cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE name=?", (selected,))
                cursor.execute("UPDATE users SET has_voted = 1 WHERE roll_no=?", (user['roll_no'],))
                conn.commit()
                hash_val = hash_vote(user['roll_no'], selected)
                record_vote_hash(user['roll_no'], selected, hash_val)
                st.success("Vote cast successfully!")
                st.session_state.user_data['has_voted'] = 1
                st.experimental_rerun()

    if st.button("Logout"):
        st.session_state.user_logged_in = False
        st.session_state.user_data = None
        st.experimental_rerun()

def main():
    st.set_page_config(page_title="College Voting System", layout="wide")

    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    if "user_logged_in" not in st.session_state:
        st.session_state.user_logged_in = False
    if "user_data" not in st.session_state:
        st.session_state.user_data = None

    st.title("Online College Voting System")

    menu = ["Home", "Admin", "User Register", "User Login"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.image("https://img.freepik.com/free-vector/election-day-concept-illustration_114360-5844.jpg", use_column_width=True)

    elif choice == "Admin":
        if st.session_state.admin_logged_in:
            admin_dashboard()
        else:
            admin_login()

    elif choice == "User Register":
        user_register()

    elif choice == "User Login":
        if st.session_state.user_logged_in:
            user_dashboard()
        else:
            user_login()

if __name__ == "__main__":
    main()
