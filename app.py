import streamlit as st
import pandas as pd
# Initialize session state
if "users" not in st.session_state:
    st.session_state["users"] = {"admin": "admin123"}  # Default admin
if "voting_data" not in st.session_state:
    st.session_state["voting_data"] = {}
if "voted_users" not in st.session_state:
    st.session_state["voted_users"] = []
if "results_released" not in st.session_state:
    st.session_state["results_released"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "home"

# Function: Home Page
def home_page():
    st.title("Online Election System")
    st.write("Welcome! Please choose an option:")
    if st.button("Login"):
        st.session_state["page"] = "login"
        st.stop()
    if st.button("Register"):
        st.session_state["page"] = "register"
        st.stop()

# Function: Registration Page
def register_page():
    st.title("Register")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")

    if st.button("Register"):
        if username in st.session_state["users"]:
            st.error("Username already exists. Try a different one.")
        elif not username or not password:
            st.error("Both fields are required.")
        else:
            st.session_state["users"][username] = password
            st.success("Registration successful! Please proceed to login.")
            st.session_state["page"] = "login"
            st.stop()

    if st.button("Back to Home"):
        st.session_state["page"] = "home"
        st.stop()

# Function: Login Page
def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state["logged_in_user"] = username
            st.session_state["is_admin"] = (username == "admin")
            st.session_state["page"] = "admin" if username == "admin" else "user"
            st.success(f"Welcome, {username}!")
            st.stop()
        else:
            st.error("Invalid username or password")

    if st.button("Back to Home"):
        st.session_state["page"] = "home"
        st.stop()

# Function: Admin Panel
def admin_panel():
    st.title("Admin Panel")

    st.subheader("Add Parties")
    new_party = st.text_input("Enter Party Name")
    if st.button("Add Party"):
        if new_party:
            if new_party not in st.session_state["voting_data"]:
                st.session_state["voting_data"][new_party] = 0
                st.success(f"Party '{new_party}' added successfully!")
            else:
                st.error("Party already exists")
        else:
            st.error("Party name cannot be empty")

    st.write("### Current Parties:")
    if st.session_state["voting_data"]:
        st.write(list(st.session_state["voting_data"].keys()))
    else:
        st.write("No parties added yet.")

    if st.button("Release Results to Users"):
        st.session_state["results_released"] = True
        st.success("Results released to users.")

    st.subheader("Results")
    if st.session_state["voting_data"]:
        results = pd.DataFrame(list(st.session_state["voting_data"].items()), columns=["Party", "Votes"])
        st.table(results)
    else:
        st.write("No voting data available.")

    if st.button("Logout"):
        st.session_state.pop("logged_in_user", None)
        st.session_state.pop("is_admin", None)
        st.session_state["page"] = "home"
        st.stop()

# Function: User Panel
def user_panel():
    st.title("User Panel")

    if st.session_state["logged_in_user"] in st.session_state["voted_users"]:
        st.warning("You have already cast your vote.")
    else:
        st.subheader("Cast Your Vote")
        parties = list(st.session_state["voting_data"].keys())
        if parties:
            selected_party = st.selectbox("Select a Party", parties)
            if st.button("Vote"):
                st.session_state["voting_data"][selected_party] += 1
                st.session_state["voted_users"].append(st.session_state["logged_in_user"])
                st.success("Your vote has been successfully recorded.")
        else:
            st.warning("No parties available for voting.")

    if st.session_state["results_released"]:
        st.subheader("Election Results")
        results = pd.DataFrame(list(st.session_state["voting_data"].items()), columns=["Party", "Votes"])
        st.table(results)

    if st.button("Logout"):
        st.session_state.pop("logged_in_user", None)
        st.session_state.pop("is_admin", None)
        st.session_state["page"] = "home"
        st.stop()

# Route to the correct page
if "logged_in_user" not in st.session_state:
    if st.session_state["page"] == "home":
        home_page()
    elif st.session_state["page"] == "login":
        login_page()
    elif st.session_state["page"] == "register":
        register_page()
else:
    if st.session_state.get("is_admin", False):
        admin_panel()
    else:
        user_panel()
