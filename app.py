import streamlit as st
import pandas as pd
import os
from database import *
from otp_utils import generate_otp, send_otp_email

# Create required directories
os.makedirs("images", exist_ok=True)

# Initialize DB
create_tables()

# Session State Setup
for key, default in {
    "page": "home",
    "logged_in_user": None,
    "is_admin": False,
    "results_released": False,
    "otp_code": "",
    "result_date": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# === Styling ===
st.markdown("""
<style>
.title { text-align:center; color:#f0f0f0; font-size:40px; }
body { background-color: #0f1117; }
.block { background: #263238; padding: 20px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# === Home Page ===
def home_page():
    st.markdown("<h1 class='title'>🗳️ College Voting System</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🛡️ Admin Login"):
            st.session_state.page = "admin_login"
    with col2:
        if st.button("👤 User Login"):
            st.session_state.page = "login"
    with col3:
        if st.button("📝 Register"):
            st.session_state.page = "register"

# === Registration with OTP ===
def register_page():
    st.markdown("### 🔐 User Registration")
    name = st.text_input("Full Name")
    roll_no = st.text_input("Roll Number (Username)")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    image = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"])

    if st.button("Send OTP"):
        if name and roll_no and password and email and phone and image:
            otp = generate_otp()
            st.session_state.otp_code = otp
            st.session_state.temp_user = {
                "roll_no": roll_no, "name": name, "password": password,
                "email": email, "phone": phone, "image": image
            }
            result = send_otp_email(email, otp)
            if result is True:
                st.success("OTP sent to your email.")
            else:
                st.error(f"Error sending email: {result}")
        else:
            st.warning("Fill all fields before requesting OTP.")

    entered = st.text_input("Enter OTP to complete registration")
    if st.button("Verify & Register"):
        if entered == st.session_state.otp_code:
            data = st.session_state.temp_user
            image_path = f"images/{data['roll_no']}.jpg"
            with open(image_path, "wb") as f:
                f.write(data["image"].getbuffer())
            if add_user(data["roll_no"], data["password"], data["name"], data["email"], data["phone"], image_path):
                st.success("User registered successfully!")
                st.session_state.page = "login"
            else:
                st.error("User already exists.")
        else:
            st.error("Invalid OTP.")

    if st.button("⬅ Back"):
        st.session_state.page = "home"

# === Login Page ===
def login_page():
    st.subheader("User Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.logged_in_user = username
            st.session_state.is_admin = False
            st.session_state.page = "user"
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

    if st.button("Forgot Password?"):
        st.session_state.page = "forgot_password"

    if st.button("⬅ Back"):
        st.session_state.page = "home"

# === Admin Login ===
def admin_login():
    st.subheader("Admin Login")
    username = st.text_input("Admin ID")
    password = st.text_input("Admin Password", type="password")

    if st.button("Login"):
        if username == "22QM1A6721" and password == "Sai7@99499":
            st.session_state.logged_in_user = username
            st.session_state.is_admin = True
            st.session_state.page = "admin"
            st.success("Admin login successful")
        else:
            st.error("Invalid admin credentials")

    if st.button("⬅ Back"):
        st.session_state.page = "home"

# === Forgot Password with OTP ===
def forgot_password_page():
    st.subheader("Forgot Password")
    email = st.text_input("Enter registered email")

    if st.button("Send OTP"):
        otp = generate_otp()
        st.session_state.otp_code = otp
        st.session_state.reset_email = email
        result = send_otp_email(email, otp)
        if result is True:
            st.success("OTP sent.")
        else:
            st.error(f"Email error: {result}")

    entered = st.text_input("Enter OTP")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Reset Password"):
        if entered == st.session_state.otp_code:
            update_password_by_email(st.session_state.reset_email, new_pass)
            st.success("Password updated.")
            st.session_state.page = "login"
        else:
            st.error("Incorrect OTP")

# === Admin Panel ===
def admin_panel():
    st.subheader("Admin Dashboard")
    party = st.text_input("Add New Party Name")
    if st.button("Add Party"):
        if add_party(party):
            st.success("Party added.")
        else:
            st.warning("Already exists.")

    st.write("### All Users")
    users = get_all_users()
    df = pd.DataFrame(users, columns=["Roll No", "Has Voted"])
    df["Has Voted"] = df["Has Voted"].apply(lambda x: "✅" if x else "❌")
    st.dataframe(df)

    st.write("### Voting Results")
    if st.button("Release Results"):
        st.session_state.results_released = True
    if st.session_state.results_released:
        st.dataframe(pd.DataFrame(get_results(), columns=["Party", "Votes"]))

    if st.button("Logout"):
        st.session_state.logged_in_user = None
        st.session_state.page = "home"

# === User Panel ===
def user_panel():
    st.subheader("Welcome Voter")
    user = st.session_state.logged_in_user
    voted = has_voted(user)
    st.markdown(f"**Voting Status:** {'✅ Voted' if voted else '❌ Not Voted'}", unsafe_allow_html=True)

    if not voted:
        options = get_parties()
        choice = st.selectbox("Choose a Party", options)
        if st.button("Vote"):
            if cast_vote(user, choice):
                st.success("Vote casted!")
            else:
                st.warning("Already voted")

    if st.session_state.results_released:
        st.dataframe(pd.DataFrame(get_results(), columns=["Party", "Votes"]))

    if st.button("Logout"):
        st.session_state.logged_in_user = None
        st.session_state.page = "home"

# === Routing ===
if st.session_state.logged_in_user is None:
    pages = {
        "home": home_page,
        "login": login_page,
        "admin_login": admin_login,
        "register": register_page,
        "forgot_password": forgot_password_page
    }
    pages[st.session_state.page]()
else:
    admin_panel() if st.session_state.is_admin else user_panel()
