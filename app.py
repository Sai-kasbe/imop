# KGRCET ONLINE ELECTION SYSTEM - Streamlit App
            st.success("Result Scheduled!")
        if st.button("Announce Now"):
            cursor.execute("UPDATE result_schedule SET is_announced=1 WHERE id=1")
            conn.commit()
            st.success("Result Announced!")
        result = cursor.execute("SELECT * FROM result_schedule").fetchone()
        if result:
            st.info(f"Scheduled Date: {result[1]} | Announced: {'Yes' if result[2] else 'No'}")

# ====== REGISTRATION ======
def user_registration():
    st.subheader("📝 New User Registration")
    name = st.text_input("Full Name")
    roll_no = st.text_input("Roll Number (Unique)")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    password = st.text_input("Password", type="password")
    image = st.file_uploader("Upload Image")
    if st.button("Register"):
        image_path = "images/" + image.name if image else ""
        if image:
            os.makedirs("images", exist_ok=True)
            with open(image_path, "wb") as f:
                f.write(image.getbuffer())
        conn, cursor = get_connection()
        try:
            cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, 0)",
                           (roll_no, name, hash_password(password), email, phone, image_path))
            conn.commit()
            st.success("Registered successfully!")
        except sqlite3.IntegrityError:
            st.error("User with this roll number already exists!")

# ====== FORGOT PASSWORD ======
def forgot_password():
    st.subheader("🔑 Forgot Password")
    roll_no = st.text_input("Enter your registered Roll Number")
    email = st.text_input("Enter your registered Email")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Reset Password"):
        conn, cursor = get_connection()
        cursor.execute("SELECT * FROM users WHERE roll_no=? AND email=?", (roll_no, email))
        if cursor.fetchone():
            cursor.execute("UPDATE users SET password=? WHERE roll_no=?", (hash_password(new_pass), roll_no))
            conn.commit()
            st.success("Password updated successfully!")
        else:
            st.error("Invalid roll number or email!")

# ====== MAIN ======
def main():
    st.title("🏛️ KGRCET ONLINE ELECTION SYSTEM")
    create_tables()
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
