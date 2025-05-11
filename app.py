import streamlit as st
import pandas as pd
from database import (
    create_tables,
    add_user,
    authenticate_user,
    add_party,
    get_parties,
    cast_vote,
    has_voted,
    get_results,
    get_all_users
)

# Initialize database
create_tables()

# Initialize session state
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

# Home Page
def home_page():
    st.title("Online Election System")
    if st.button("Login"):
        st.session_state["page"] = "login"
        st.rerun()
    if st.button("Register"):
        st.session_state["page"] = "register"
        st.rerun()

# Register
def register_page():
    st.title("Register")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")

    if st.button("Register"):
        if not username or not password:
            st.error("Both fields are required.")
        elif add_user(username, password):
            st.success("Registration successful! Please login.")
            st.session_state["page"] = "login"
            st.rerun()
        else:
            st.error("Username already exists.")

    if st.button("Back to Home"):
        st.session_state["page"] = "home"
        st.rerun()

# Login
def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "22QM1A6721" and password == "Sai7@99499":
            st.session_state["logged_in_user"] = username
            st.session_state["is_admin"] = True
            st.session_state["page"] = "admin"
            st.success(f"Welcome Admin {username}!")
            st.rerun()
        elif authenticate_user(username, password):
            st.session_state["logged_in_user"] = username
            st.session_state["is_admin"] = False
            st.session_state["page"] = "user"
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password")

    if st.button("Back to Home"):
        st.session_state["page"] = "home"
        st.rerun()

# Admin Panel
def admin_panel():
    st.title("Admin Panel")

    st.subheader("Add Parties")
    new_party = st.text_input("Enter Party Name")
    if st.button("Add Party"):
        if new_party:
            if add_party(new_party):
                st.success(f"Party '{new_party}' added successfully!")
            else:
                st.error("Party already exists.")
        else:
            st.error("Party name cannot be empty")

    st.write("### Current Parties:")
    st.write(get_parties())

    st.subheader("Users Registered")
    users = get_all_users()
    st.write(pd.DataFrame(users, columns=["Username", "Voted? (1 = Yes, 0 = No)"]))

    st.subheader("Control Result Announcement")
    result_date = st.text_input("Enter result announcement date (YYYY-MM-DD)", st.session_state["result_date"])
    if st.button("Schedule Result Date"):
        st.session_state["result_date"] = result_date
        st.success(f"Results will be announced on {result_date}")
    if st.button("Release Results Now"):
        st.session_state["results_released"] = True
        st.success("Results released to users.")

    st.subheader("Live Results")
    results = get_results()
    if results:
        df = pd.DataFrame(results, columns=["Party", "Votes"])
        st.table(df)
    else:
        st.write("No voting data available.")

    if st.button("Logout"):
        st.session_state["logged_in_user"] = None
        st.session_state["is_admin"] = False
        st.session_state["page"] = "home"
        st.rerun()

# User Panel
def user_panel():
    st.title("User Panel")
    username = st.session_state["logged_in_user"]

    voted = has_voted(username)
    status_color = "green" if voted else "red"
    st.markdown(f"**Status:** <span style='color:{status_color}'>{'Voted' if voted else 'Not Voted'}</span>", unsafe_allow_html=True)

    if not voted:
        st.subheader("Cast Your Vote")
        parties = get_parties()
        if parties:
            selected_party = st.selectbox("Select a Party", parties)
            if st.button("Vote"):
                if cast_vote(username, selected_party):
                    st.success("Your vote has been successfully recorded.")
                    st.rerun()
                else:
                    st.error("You have already voted.")
        else:
            st.warning("No parties available for voting.")

    if st.session_state["results_released"]:
        st.subheader("Election Results")
        results = get_results()
        df = pd.DataFrame(results, columns=["Party", "Votes"])
        st.table(df)
    elif st.session_state["result_date"]:
        st.info(f"Results will be announced on: {st.session_state['result_date']}")

    if st.button("Logout"):
        st.session_state["logged_in_user"] = None
        st.session_state["is_admin"] = False
        st.session_state["page"] = "home"
        st.rerun()

# Router
if st.session_state["logged_in_user"] is None:
    if st.session_state["page"] == "home":
        home_page()
    elif st.session_state["page"] == "login":
        login_page()
    elif st.session_state["page"] == "register":
        register_page()
else:
    if st.session_state["is_admin"]:
        admin_panel()
    else:
        user_panel()
