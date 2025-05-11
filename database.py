import sqlite3

def connect_to_db():
    """Connect to the SQLite database (or create it if it doesn't exist)."""
    conn = sqlite3.connect("example.db")
    return conn

def create_tables():
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

def add_user(roll_no, name, password, email, phone, image):
    """Add a new user to the users table with all required fields."""
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (roll_no, name, password, email, phone, image)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (roll_no, name, password, email, phone, image))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    # Ensure the users table exists
    create_users_table()
    
    # Add example users
    try:
        add_user("12345", "John Doe", "hashed_password", "john@example.com", "1234567890", "path/to/image.jpg")
        add_user("67890", "Jane Doe", "hashed_password", "jane@example.com", "0987654321", "path/to/image.jpg")
    except TypeError as e:
        print(f"Function call error: {e}")
