
import sqlite3
from datetime import datetime

def connect():
    return sqlite3.connect("clinic.db")

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
            name TEXT NOT NULL UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor TEXT,
            service TEXT,
            time TEXT
        )
    """)

    con.commit()
    con.close()


def get_doctors():
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT * FROM doctors")
    r = cur.fetchall()
    con.close()
    return r


def get_services():
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT name FROM services")
    r = [x[0] for x in cur.fetchall()]
    con.close()
    return r


def create_appointment(doc, srv, time):
    con = connect()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO appointments (doctor, service, time) VALUES (?, ?, ?)",
        (doc, srv, time)
    )
    con.commit()
    con.close()


def get_appointments_today():
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT doctor, service, time FROM appointments")
    r = cur.fetchall()
    con.close()
    return r
