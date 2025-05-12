import sqlite3

def connect_to_db():
    """Connect to the SQLite database (or create it if it doesn't exist)."""
    return sqlite3.connect("example.db")

def create_tables():
    """Create the users table with all required fields."""
    conn = connect_to_db()
    cursor = conn.cursor()

    # Create the users table with all required columns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            image TEXT
        )
    """)
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
    except sqlite3.IntegrityError as e:
        print(f"Error inserting user: {e}")
        return False
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    create_tables()
    # Add example users
    success1 = add_user("12345", "John Doe", "hashed_password", "john@example.com", "1234567890", "path/to/image.jpg")
    success2 = add_user("67890", "Jane Doe", "hashed_password", "jane@example.com", "0987654321", "path/to/image.jpg")
    if success1 and success2:
        print("Users added successfully.")
    else:
        print("Error adding one or more users.")
