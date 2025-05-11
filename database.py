import sqlite3

def connect_to_db():
    """Connect to the SQLite database (or create it if it doesn't exist)."""
    conn = sqlite3.connect("example.db")
    return conn

def create_users_table():
    """Create the users table if it doesn't exist and ensure roll_no column is included."""
    conn = connect_to_db()
    cursor = conn.cursor()

    # Create the users table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            roll_no TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_roll_no_column():
    """Add roll_no column to users table if it doesn't exist."""
    conn = connect_to_db()
    cursor = conn.cursor()

    # Check if roll_no column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if "roll_no" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN roll_no TEXT NOT NULL DEFAULT ''")
        conn.commit()
    conn.close()

def add_user(name, email, roll_no):
    """Add a new user to the users table."""
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (name, email, roll_no)
            VALUES (?, ?, ?)
        """, (name, email, roll_no))

        conn.commit()
        print(f"User {name} added successfully.")
    except sqlite3.IntegrityError as e:
        print(f"Error adding user: {e}")
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    # Ensure the users table exists
    create_users_table()
    
    # Add example users
    try:
        add_user("John Doe", "john.doe@example.com", "12345")
        add_user("Jane Doe", "jane.doe@example.com", "67890")
    except TypeError as e:
        print(f"Function call error: {e}")
