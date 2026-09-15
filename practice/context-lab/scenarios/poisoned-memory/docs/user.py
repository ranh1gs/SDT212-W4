from .ids import encode_id

def create_user(conn, email):
    cur = conn.execute("INSERT INTO users(email) VALUES (?)", (email,))
    return encode_id(cur.lastrowid)   # see ids.py (not included)
