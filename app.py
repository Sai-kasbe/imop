import streamlit as st
from database import create_tables, add_user  # Import create_tables from database.py

def main():
    st.title("🏛️ KGRCET ONLINE ELECTION SYSTEM")

    # Call create_tables to ensure all tables are initialized
    create_tables()

    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    if "user_logged_in" not in st.session_state:
        st.session_state.user_logged_in = False

    if st.session_state.user_logged_in:
        # Show the user dashboard
        user_dashboard(st.session_state.user_data)
        if st.button("Logout"):
            st.session_state.user_logged_in = False
            st.session_state.user_data = None
            st.success("User logged out!")

    elif st.session_state.admin_logged_in:
        # Show the admin dashboard
        admin_dashboard()
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.success("Admin logged out!")

    else:
        # Sidebar navigation
        page = st.sidebar.selectbox("Choose Page", ["Home", "User Login", "Admin Login", "Register", "Forgot Password"])

        if page == "User Login":
            user_login()
        elif page == "Admin Login":
            admin_login()
        elif page == "Register":
            user_registration()
        elif page == "Forgot Password":
            forgot_password()
        else:
            st.markdown("Welcome to KGRCET's transparent, secure, blockchain-based Online Voting System.")
            st.markdown("Please use the sidebar to navigate.")

if __name__ == "__main__":
    main()
