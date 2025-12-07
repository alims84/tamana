# ============================
#        DATABASE.PY
# ============================

import sqlite3
from contextlib import closing

DB = "clinic.db"

def create_tables():
    with closing(sqlite3.connect(DB)) as con:
        cur = con.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialty TEXT NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                full_name TEXT,
                doctor TEXT,
                service TEXT,
                date_greg TEXT,
                date_jalali TEXT,
                time TEXT
            )
        """)

        con.commit()


def add_doctor(name, specialty):
    with closing(sqlite3.connect(DB)) as con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO doctors (name, specialty) VALUES (?, ?)",
            (name, specialty)
        )
        con.commit()


def get_doctors():
    with closing(sqlite3.connect(DB)) as con:
        return con.cursor().execute("SELECT * FROM doctors").fetchall()


def add_service(name):
    with closing(sqlite3.connect(DB)) as con:
        cur = con.cursor()
        cur.execute("INSERT OR IGNORE INTO services (name) VALUES (?)", (name,))
        con.commit()


def get_services():
    with closing(sqlite3.connect(DB)) as con:
        return [row[0] for row in con.cursor().execute("SELECT name FROM services")]


def create_appointment(data: dict):
    with closing(sqlite3.connect(DB)) as con:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO appointments 
            (user_id, full_name, doctor, service, date_greg, date_jalali, time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["user_id"], data["full_name"], data["doctor"],
                data["service"], data["date_greg"], data["date_jalali"], data["time"]
            )
        )
        con.commit()


def get_appointments_today():
    with closing(sqlite3.connect(DB)) as con:
        cur = con.cursor()
        from datetime import datetime
        today = datetime.now().date()
        return cur.execute(
            "SELECT * FROM appointments WHERE date_greg = ?", (str(today),)
        ).fetchall()
