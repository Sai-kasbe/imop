import streamlit as st
import pandas as pd

init_db()

if "page" not in st.session_state:
    st.session_state["page"] = "home"
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

def home_page():
    st.title("Online Election System")
    if st.button("Login"):
        st.session_state["page"] = "login"
        st.experimental_rerun()
    if st.button("Register"):
        st.session_state["page"] = "register"
        st.experimental_rerun()

def register_page():
    st.title("Register")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")

    if st.button("Register"):
        if not username or not password:
            st.error("Both fields are required.")
        elif register_user(username, password):
            st.success("Registration successful. Please log in.")
            st.session_state["page"] = "login"
            st.experimental_rerun()
        else:
            st.error("Username already exists.")

    if st.button("Back"):
        st.session_state["page"] = "home"
        st.experimental_rerun()

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state["logged_in_user"] = username
            st.session_state["is_admin"] = (username == "admin")
            st.session_state["page"] = "admin" if username == "admin" else "user"
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

    if st.button("Back"):
        st.session_state["page"] = "home"
        st.experimental_rerun()

def admin_panel():
    st.title("Admin Panel")

    new_party = st.text_input("Add Party")
    if st.button("Add"):
        if new_party:
            if add_party(new_party):
                st.success(f"'{new_party}' added.")
            else:
                st.error("Party already exists.")

    st.subheader("Current Parties")
    st.write(get_parties())

    if st.button("Release Results"):
        release_results()
        st.success("Results released.")

    st.subheader("Results")
    results = get_results()
    if results:
        df = pd.DataFrame(results, columns=["Party", "Votes"])
        st.table(df)
    else:
        st.info("No votes yet.")

    if st.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()

def user_panel():
    st.title("User Panel")
    username = st.session_state["logged_in_user"]

    if user_has_voted(username):
        st.warning("You have already voted.")
    else:
        parties = get_parties()
        if parties:
            selected = st.selectbox("Choose Party", parties)
            if st.button("Vote"):
                vote_party(selected)
                set_user_voted(username)
                st.success("Vote recorded.")
                st.experimental_rerun()
        else:
            st.warning("No parties available.")

    if results_are_released():
        st.subheader("Election Results")
        df = pd.DataFrame(get_results(), columns=["Party", "Votes"])
        st.table(df)

    if st.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()

# Routing
if st.session_state["logged_in_user"] is None:
    if st.session_state["page"] == "home":
        home_page()
    elif st.session_state["page"] == "register":
        register_page()
    elif st.session_state["page"] == "login":
        login_page()
else:
    if st.session_state["is_admin"]:
        admin_panel()
    else:
        user_panel()
