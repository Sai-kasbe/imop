import streamlit as st
import hashlib
import os
from datetime import datetime
import database as db

st.set_page_config(page_title="KGRCET Voting System", layout="wide")

# ==== STYLE ====
st.markdown("""
    <style>
    body { background-color: #0D1B2A; color: white; }
    .stButton>button { background-color: #1B263B; color: white; border-radius: 10px; }
    h1, h2, h3, h4 { color: #E0E1DD; }
    </style>
""", unsafe_allow_html=True)

# ==== HELPERS ====
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==== USER DASHBOARD ====
def user_dashboard(user):
    st.header("🧑‍🎓 My Profile")
    st.success(f"Welcome, {user[1]} ({user[0]})")
    st.write(f"**Name:** {user[1]}")
    st.write(f"**Roll No:** {user[0]}")
    st.write(f"**Phone:** {user[2]}")
    st.write(f"**Status:** {'✅ VOTED' if user[5] else '❌ NOT VOTED'}")

    if user[5]:
        st.info("You have already voted. Thank you!")
        return

    roles = ["President", "Vice-President", "Secretary", "Treasurer"]
    for role in roles:
        st.subheader(f"🗳️ Vote for {role}")
        candidates = db.get_candidates_by_role(role)
        if candidates:
            options = [f"{c[1]} ({c[2]})" for c in candidates]
            choice = st.radio(f"Select {role}", options, key=role)
            if st.button(f"Cast Vote for {role}", key=role+"_btn"):
                candidate = next(c for c in candidates if f"{c[1]} ({c[2]})" == choice)
                db.vote(user[0], candidate[2])
                db.record_vote_block(user[0], candidate[1])
                st.success(f"Your vote for {role} has been recorded!")
                st.experimental_rerun()
        else:
            st.warning(f"No candidates available for {role} yet.")

# ==== USER LOGIN ====
def user_login():
    st.subheader("User Login")
    name = st.text_input("Enter Name")
    roll_no = st.text_input("Enter Roll No")
    if st.button("Login"):
        user = db.get_user(roll_no)
        if user and user[1] == name:
            st.session_state.user = user
            st.session_state.page = "user"
            st.experimental_rerun()
        else:
            st.error("Invalid credentials!")

# ==== ADMIN LOGIN ====
def admin_login():
    st.subheader("Admin Login")
    username = st.text_input("Admin ID")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if db.login_admin(username, hash_pass(password)):
            st.session_state.page = "admin"
            st.success("Admin logged in")
            st.experimental_rerun()
        else:
            st.error("Invalid admin credentials!")

# ==== REGISTRATION ====
def register():
    st.subheader("User Registration")
    name = st.text_input("Full Name")
    roll_no = st.text_input("Roll Number")
    phone = st.text_input("Phone")
    password = st.text_input("Password", type="password")
    image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

    if st.button("Register"):
        if not all([name, roll_no, phone, password, image]):
            st.warning("All fields are required.")
            return
        image_path = f"images/{image.name}"
        os.makedirs("images", exist_ok=True)
        with open(image_path, "wb") as f:
            f.write(image.getbuffer())
        success = db.register_user(roll_no, name, phone, hash_pass(password), image_path)
        if success:
            st.success("Registered successfully!")
        else:
            st.error("User already exists!")

# ==== PASSWORD RESET ====
def forgot_password():
    st.subheader("Reset Password")
    roll_no = st.text_input("Registered Roll No")
    phone = st.text_input("Registered Phone")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Update Password"):
        user = db.get_user(roll_no)
        if user and user[2] == phone:
            db.update_password(roll_no, hash_pass(new_pass))
            st.success("Password updated.")
        else:
            st.error("Invalid Roll No or Phone.")

# ==== ADMIN DASHBOARD ====
def admin_dashboard():
    st.title("📊 Admin Dashboard")
    tab1, tab2, tab3 = st.tabs(["Add Candidate", "View Users", "Results"])

    with tab1:
        st.subheader("Add Candidate")
        name = st.text_input("Name")
        roll_no = st.text_input("Roll No")
        dept = st.text_input("Department")
        year_sem = st.text_input("Year/Sem")
        role = st.selectbox("Role", ["President", "Vice-President", "Secretary", "Treasurer"])
        image = st.file_uploader("Image", type=["jpg", "png", "jpeg"])

        if st.button("Add"):
            if not all([name, roll_no, dept, year_sem, role, image]):
                st.warning("All fields required.")
            else:
                path = f"images/{image.name}"
                with open(path, "wb") as f:
                    f.write(image.getbuffer())
                try:
                    db.add_candidate(name, roll_no, dept, year_sem, role, path)
                    st.success("Candidate added.")
                except:
                    st.error("Candidate already exists.")

    with tab2:
        st.subheader("Registered Users")
        users = db.get_all_users()
        for u in users:
            st.write(f"{u[1]} ({u[0]}) - Phone: {u[2]} - {'✅' if u[3] else '❌'}")

    with tab3:
        st.subheader("Schedule / Announce Results")
        date = st.date_input("Result Date")
        if st.button("Schedule"):
            db.schedule_result(str(date))
            st.success("Result scheduled.")
        if st.button("Announce Now"):
            db.announce_result()
            st.success("Results announced.")
        status = db.get_result_schedule()
        if status:
            st.info(f"Scheduled Date: {status[1]} | Announced: {'✅' if status[2] else '❌'}")

# ==== MAIN ====
def main():
    st.title("🏫 KGRCET Voting System")

    if "page" not in st.session_state:
        st.session_state.page = "home"

    if st.session_state.page == "user":
        user_dashboard(st.session_state.user)
        if st.button("Logout"):
            st.session_state.clear()
            st.success("Logged out")
            st.experimental_rerun()

    elif st.session_state.page == "admin":
        admin_dashboard()
        if st.button("Logout"):
            st.session_state.clear()
            st.success("Admin logged out")
            st.experimental_rerun()

    else:
        menu = st.sidebar.radio("Navigate", ["Home", "User Login", "Register", "Forgot Password", "Admin Login"])
        if menu == "User Login":
            user_login()
        elif menu == "Register":
            register()
        elif menu == "Forgot Password":
            forgot_password()
        elif menu == "Admin Login":
            admin_login()
        else:
            st.markdown("Welcome to **KGRCET Online Voting System** — secure, simple, and transparent.")

if __name__ == "__main__":
    main()
