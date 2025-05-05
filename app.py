import streamlit as st 
import pandas as pd

Initialize session state if not already initialized

if "users" not in st.session_state: st.session_state["users"] = {"admin": "admin123"}  # Default admin if "voting_data" not in st.session_state: st.session_state["voting_data"] = {} if "voted_users" not in st.session_state: st.session_state["voted_users"] = [] if "results_released" not in st.session_state: st.session_state["results_released"] = False

Function to display login page

def login_page(): st.title("Online Election System") st.subheader("Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if username in st.session_state["users"] and st.session_state["users"][username] == password:
        st.session_state["logged_in_user"] = username
        st.session_state["is_admin"] = (username == "admin")
        st.experimental_rerun()
    else:
        st.error("Invalid username or password")

Function for admin panel

def admin_panel(): st.title("Admin Panel")

# Option to add parties
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

# Display current parties
st.write("### Current Parties:")
if st.session_state["voting_data"]:
    st.write(list(st.session_state["voting_data"].keys()))
else:
    st.write("No parties added yet.")

# Release results to users
if st.button("Release Results to Users"):
    st.session_state["results_released"] = True
    st.success("Results released to users.")

# View results
st.subheader("Results")
if st.session_state["voting_data"]:
    results = pd.DataFrame(
        list(st.session_state["voting_data"].items()), columns=["Party", "Votes"]
    )
    st.table(results)
else:
    st.write("No voting data available.")

if st.button("Logout"):
    st.session_state.pop("logged_in_user", None)
    st.session_state.pop("is_admin", None)
    st.experimental_rerun()

Function for user panel

def user_panel(): st.title("User Panel")

if st.session_state["logged_in_user"] in st.session_state["voted_users"]:
    st.warning("You have already cast your vote.")
else:
    # Voting section
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

# Display results if released
if st.session_state["results_released"]:
    st.subheader("Election Results")
    results = pd.DataFrame(
        list(st.session_state["voting_data"].items()), columns=["Party", "Votes"]
    )
    st.table(results)

if st.button("Logout"):
    st.session_state.pop("logged_in_user", None)
    st.session_state.pop("is_admin", None)
    st.experimental_rerun()

Main application logic

if "logged_in_user" not in st.session_state: login_page() else: if st.session_state.get("is_admin", False): admin_panel() else: user_panel()
