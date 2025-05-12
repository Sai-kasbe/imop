import streamlit as st
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
import random
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'login'  # Default page

# Page functions (replace with your actual page functions)
def home_page():
    st.title("Home Page")
    st.write("Welcome to the College Voting System!")
    
def login_page():
    st.title("Login")
    # Login form
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    
    if st.button("Login"):
        user = authenticate_user(username, password)
        if user:
            st.session_state.page = 'dashboard'
        else:
            st.error("Invalid credentials, please try again.")

def dashboard_page():
    st.title("User Dashboard")
    st.write(f"Welcome, {st.session_state.user_name}!")
    st.button("Logout", on_click=logout)

def logout():
    del st.session_state.page  # This will reset the session and go to the login page

def authenticate_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user[1], password):  # Assuming password is stored in the second column
        st.session_state.user_name = user[0]  # Store the user name
        return True
    return False

# OTP Email Functionality
def send_otp_email(to_email):
    otp = random.randint(100000, 999999)
    subject = "Your OTP for College Voting System"
    body = f"Your OTP is {otp}"
    
    # Send email
    sender_email = "your_email@example.com"
    password = "your_password"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        return otp
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return None

# Image upload function
def save_uploaded_image(uploaded_file):
    if uploaded_file is not None:
        file_path = os.path.join("images", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

# Main App Logic
pages = {
    'login': login_page,
    'home': home_page,
    'dashboard': dashboard_page,
}

# Routing page based on session state
if st.session_state.page in pages:
    pages[st.session_state.page]()
else:
    st.error("Page not found!")

