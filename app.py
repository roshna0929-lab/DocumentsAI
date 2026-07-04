from flask import Flask, request, jsonify
import sqlite3
import hashlib
from datetime import datetime

app = Flask(__name__)

DATABASE = "land_registration.db"


# -------------------------
# Database
# -------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS registrations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reg_username TEXT UNIQUE,
        reg_password TEXT,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS owner_details(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reg_username TEXT,

        owner_name TEXT,
        spouse_name TEXT,
        parent_name TEXT,
        child_name TEXT,

        land_address TEXT,

        aadhar TEXT,
        pan TEXT,
        other_id TEXT,

        phone1 TEXT,
        phone2 TEXT,
        email TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# -------------------------
# SHA256
# -------------------------

def encrypt(password):
    return hashlib.sha256(password.encode()).hexdigest()


# -------------------------
# Login
# -------------------------

@app.route("/login", methods=["POST"])
def login():

    data = request.json

    username = data["username"]
    password = encrypt(data["password"])

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    ).fetchone()

    conn.close()

    if user:
        return jsonify(success=True)

    return jsonify(success=False)


# -------------------------
# Register Portal User
# -------------------------

@app.route("/register-user", methods=["POST"])
def register_user():

    data = request.json

    username = data["username"]
    password = encrypt(data["password"])

    conn = get_db()

    try:

        conn.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )

        conn.commit()

        return jsonify(success=True)

    except:

        return jsonify(success=False,
                       message="Username already exists")

    finally:
        conn.close()


# -------------------------
# Registration Login
# -------------------------

@app.route("/registration-login", methods=["POST"])
def registration_login():

    data = request.json

    username = data["username"]
    password = encrypt(data["password"])

    conn = get_db()

    try:

        conn.execute("""
        INSERT INTO registrations
        (reg_username,reg_password,created_at)
        VALUES(?,?,?)
        """,
        (
            username,
            password,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()

        return jsonify(success=True)

    except:

        return jsonify(success=False,
                       message="Registration username already exists")

    finally:
        conn.close()


# -------------------------
# Save Owner Details
# -------------------------

@app.route("/owner-details", methods=["POST"])
def owner():

    data = request.json

    conn = get_db()

    conn.execute("""
    INSERT INTO owner_details(

    reg_username,

    owner_name,
    spouse_name,
    parent_name,
    child_name,

    land_address,

    aadhar,
    pan,
    other_id,

    phone1,
    phone2,
    email

    )

    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
    """,

    (

    data["reg_username"],

    data["owner_name"],
    data["spouse_name"],
    data["parent_name"],
    data["child_name"],

    data["land_address"],

    data["aadhar"],
    data["pan"],
    data["other_id"],

    data["phone1"],
    data["phone2"],
    data["email"]

    ))

    conn.commit()

    conn.close()

    return jsonify(success=True)


# -------------------------
# Review Documents
# -------------------------

@app.route("/documents/<username>")
def documents(username):

    conn = get_db()

    rows = conn.execute("""

    SELECT *

    FROM owner_details

    WHERE reg_username=?

    """,

    (username,)

    ).fetchall()

    conn.close()

    return jsonify([dict(r) for r in rows])


# -------------------------
# Get Single Record
# -------------------------

@app.route("/document/<int:id>")
def document(id):

    conn = get_db()

    row = conn.execute("""

    SELECT *

    FROM owner_details

    WHERE id=?

    """,

    (id,)

    ).fetchone()

    conn.close()

    if row:
        return jsonify(dict(row))

    return jsonify(message="Not Found")


# -------------------------
# Run
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)
