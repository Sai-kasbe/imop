import streamlit as st
import sqlite3
import database as db
from PIL import Image
import random
import smtplib
import os
import pandas as pd

# Session State Initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# Set page config
st.set_page_config(page_title="College Voting System", layout="centered")

def send_otp(email):
    otp = str(random.randint(100000, 999999))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("youremail@example.com", "yourapppassword")  # Use app-specific password
    message = f"Your OTP for password reset is: {otp}"
    server.sendmail("youremail@example.com", email, message)
    server.quit()
    return otp

def admin_login():
    st.subheader("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        if username == "22QM1A6721" and password == "Sai7@99499":
            st.session_state.admin_logged_in = True
            st.success("Logged in as Admin")
        else:
            st.error("Invalid admin credentials")

def admin_panel():
    st.title("Admin Dashboard")

    menu = ["Add Candidate", "Schedule/Announce Results", "View Voters", "Logout"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Candidate":
        st.subheader("Add Candidate")
        name = st.text_input("Candidate Name")
        role = st.selectbox("Position", ["President", "Vice President", "Secretary"])
        image = st.file_uploader("Upload Candidate Image", type=["png", "jpg", "jpeg"])
        if st.button("Add Candidate"):
            if name and image:
                img_path = os.path.join("uploads", image.name)
                with open(img_path, "wb") as f:
                    f.write(image.read())
                db.add_candidate(name, role, img_path)
                st.success("Candidate Added Successfully!")
            else:
                st.error("Name and Image are required.")

    elif choice == "Schedule/Announce Results":
        st.subheader("Voting Results")
        role = st.selectbox("Select Role", ["President", "Vice President", "Secretary"])
        if st.button("Show Results"):
            results = db.get_results(role)
            if results.empty:
                st.warning("No votes recorded for this role yet.")
            else:
                st.bar_chart(data=results.set_index("candidate_name")["vote_count"])

    elif choice == "View Voters":
        st.subheader("Registered Voters")
        voters = db.get_all_voters()
        st.dataframe(voters)

    elif choice == "Logout":
        st.session_state.admin_logged_in = False
        st.success("Logged out successfully.")

def user_registration():
    st.subheader("User Registration")
    roll_no = st.text_input("Roll Number")
    name = st.text_input("Full Name")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    image = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"])

    if st.button("Register"):
        if roll_no and name and password and email and phone and image:
            img_path = os.path.join("uploads", image.name)
            with open(img_path, "wb") as f:
                f.write(image.read())
            if db.register_user(roll_no, name, password, email, phone, img_path):
                st.success("Registration successful! Please log in.")
            else:
                st.warning("User already exists!")
        else:
            st.error("All fields are required.")

def user_login():
    st.subheader("User Login")
    roll_no = st.text_input("Roll Number")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = db.validate_user(roll_no, password)
        if user:
            st.session_state.user = user
            st.success(f"Welcome, {user[1]}!")
        else:
            st.error("Invalid credentials")

def forgot_password():
    st.subheader("Forgot Password")
    roll_no = st.text_input("Enter your Roll Number")
    user = db.get_user_by_roll(roll_no)
    if user:
        email = user[3]
        if st.button("Send OTP"):
            otp = send_otp(email)
            user_otp = st.text_input("Enter the OTP sent to your email")
            new_pass = st.text_input("Enter New Password", type="password")
            if st.button("Reset Password"):
                if user_otp == otp:
                    db.update_password(roll_no, new_pass)
                    st.success("Password reset successfully")
                else:
                    st.error("Invalid OTP")
    else:
        st.warning("Roll number not found.")

def user_dashboard():
    st.title("User Dashboard")
    user = st.session_state.user
    st.image(user[6], width=150)
    st.write(f"**Name:** {user[1]}")
    st.write(f"**Roll Number:** {user[0]}")
    st.write(f"**Phone:** {user[4]}")

    if not db.has_user_voted(user[0]):
        st.subheader("Cast Your Vote")
        role = st.selectbox("Select Role to Vote", ["President", "Vice President", "Secretary"])
        candidates = db.get_candidates(role)
        if not candidates.empty:
            selected = st.radio("Select your candidate:", candidates['candidate_name'].tolist())
            if st.button("Vote"):
                candidate_id = candidates[candidates['candidate_name'] == selected].iloc[0]['id']
                db.cast_vote(candidate_id, user[0])
                st.success("Your vote has been recorded.")
        else:
            st.info("No candidates found for this role.")
    else:
        st.success("You have already voted.")

    if st.button("Logout"):
        st.session_state.user = None
        st.success("Logged out successfully")

def main():
    st.title("🗳️ College Voting System")

    menu = ["Home", "Admin", "User Login", "Register", "Forgot Password"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Home":
        st.markdown("Welcome to the secure and fair **College Voting System**. Cast your votes safely and make your voice count!")

    elif choice == "Admin":
        if st.session_state.admin_logged_in:
            admin_panel()
        else:
            admin_login()

    elif choice == "User Login":
        if st.session_state.user:
            user_dashboard()
        else:
            user_login()

    elif choice == "Register":
        user_registration()

    elif choice == "Forgot Password":
        forgot_password()

if __name__ == "__main__":
    main()
