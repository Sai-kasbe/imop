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
    except sqlite3.IntegrityError as e:
        print(f"Error adding user: {e}")
    finally:
        conn.close()
