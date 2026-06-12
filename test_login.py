import sqlite3
from werkzeug.security import check_password_hash

con = sqlite3.connect('leafcare.db')
con.row_factory = sqlite3.Row
cur = con.cursor()
cur.execute("SELECT id, email, password_hash FROM users WHERE email = 'leafcare@example.com'")
user = cur.fetchone()

if user:
    print("User found:", dict(user))
    print("Hash length:", len(user["password_hash"]))
    match = check_password_hash(user["password_hash"], "leaf123")
    print("Password Match:", match)
else:
    print("User not found.")
