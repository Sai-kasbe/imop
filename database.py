import sqlite3

def create_tables():
    conn = sqlite3.connect("election.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS parties (
        name TEXT PRIMARY KEY,
        votes INTEGER DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        username TEXT PRIMARY KEY,
        party TEXT
    )
    """)

    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect("election.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect("election.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

def add_party(party_name):
    conn = sqlite3.connect("election.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO parties (name, votes) VALUES (?, 0)", (party_name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_parties():
    conn = sqlite3.connect("election.db")
    c = conn.cursor()
    c.execute("SELECT name FROM parties")
    parties = [row[0] for row in c.fetchall()]
    conn.close()
    return parties

def cast_vote(username, party):
    conn = sqlite3.connect("election.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO votes (username, party) VALUES (?, ?)", (username, party))
        c.execute("UPDATE parties SET votes = votes + 1 WHERE name = ?", (party,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def has_voted(username):
    conn = sqlite3.connect("election.db")
    c = conn.cursor()
    c.execute("SELECT * FROM votes WHERE username = ?", (username,))
    voted = c.fetchone() is not None
    conn.close()
    return voted

def get_results():
    conn = sqlite3.connect("election.db")
    c = conn.cursor()
    c.execute("SELECT name, votes FROM parties")
    results = c.fetchall()
    conn.close()
    return results
