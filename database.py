# ============================
#        DATABASE.PY
# ============================

import sqlite3

DB = "clinic.db"


def get_conn():
    return sqlite3.connect(DB)


def create_tables():
    con = get_conn()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS doctors(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS services(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments(
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


# -------- DOCTORS --------

def add_doctor(name, specialty):
    con = get_conn()
    cur = con.cursor()
    cur.execute("INSERT INTO doctors (name, specialty) VALUES (?, ?)", (name, specialty))
    con.commit()
    con.close()


def get_doctors():
    con = get_conn()
    cur = con.cursor()
    cur.execute("SELECT * FROM doctors")
    data = cur.fetchall()
    con.close()
    return data


# -------- SERVICES --------

def add_service(name):
    con = get_conn()
    cur = con.cursor()
    cur.execute("INSERT INTO services (name) VALUES (?)", (name,))
    con.commit()
    con.close()


def get_services():
    con = get_conn()
    cur = con.cursor()
    cur.execute("SELECT name FROM services")
    rows = cur.fetchall()
    con.close()
    return [r[0] for r in rows]


# ---- APPOINTMENTS ----

def add_appointment(user_id, full_name, doctor, service, date_greg, date_jalali, time):
    con = get_conn()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO appointments (user_id, full_name, doctor, service, date_greg, date_jalali, time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, full_name, doctor, service, date_greg, date_jalali, time))
    con.commit()
    con.close()


def get_appointments_today(jalali_date):
    con = get_conn()
    cur = con.cursor()
    cur.execute("SELECT * FROM appointments WHERE date_jalali = ?", (jalali_date,))
    data = cur.fetchall()
    con.close()
    return data
