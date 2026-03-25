import sqlite3
from flask import g
import os

DATABASE = os.path.join(os.path.dirname(__file__), 'nutriguide.db')

def get_db():
    from flask import current_app
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            email    TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS profiles (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER UNIQUE NOT NULL,
            age            INTEGER,
            gender         TEXT,
            height         REAL,
            weight         REAL,
            target_weight  REAL,
            diet_type      TEXT DEFAULT "veg",
            activity       TEXT DEFAULT "moderate",
            allergies      TEXT DEFAULT "",
            conditions     TEXT DEFAULT "",
            bmi            REAL,
            daily_calories INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS weight_logs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            weight       REAL NOT NULL,
            logged_date  TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS activities (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            activity_type   TEXT NOT NULL,
            duration_mins   INTEGER NOT NULL,
            steps           INTEGER DEFAULT 0,
            calories_burned INTEGER NOT NULL,
            activity_date   TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    db.commit()
    db.close()
