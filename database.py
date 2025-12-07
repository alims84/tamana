import sqlite3

DB = "clinic.db"


def connect():
    return sqlite3.connect(DB, check_same_thread=False)


def create_tables():
    con = connect()
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
        name TEXT NOT NULL
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
    con.close()


def add_doctor(name, specialty):
    con = connect()
    cur = con.cursor()
    cur.execute("INSERT INTO doctors (name, specialty) VALUES (?, ?)", (name, specialty))
    con.commit()
    con.close()


def add_service(name):
    con = connect()
    cur = con.cursor()
    cur.execute("INSERT INTO services (name) VALUES (?)", (name,))
    con.commit()
    con.close()


def get_doctors():
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT id, name, specialty FROM doctors")
    rows = cur.fetchall()
    con.close()
    return rows


def get_services():
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT name FROM services")
    rows = [r[0] for r in cur.fetchall()]
    con.close()
    return rows


def create_appointment(user_id, full_name, doctor, service, date_greg, date_jalali, time):
    con = connect()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO appointments (user_id, full_name, doctor, service, date_greg, date_jalali, time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, full_name, doctor, service, date_greg, date_jalali, time))
    con.commit()
    con.close()


def get_appointments_today():
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    con = connect()
    cur = con.cursor()
    cur.execute("SELECT doctor, service, time FROM appointments WHERE date_greg=?", (today,))
    rows = cur.fetchall()
    con.close()
    return rows
