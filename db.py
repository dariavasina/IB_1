import sqlite3
from flask import g
from markupsafe import escape

DATABASE = "app.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db = get_db()
    db.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )"""
    )
    db.commit()


def get_user_by_login(login):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchone()


def get_all_users():
    db = get_db()
    users = db.execute("SELECT id, login FROM users").fetchall()
    return [{"id": u["id"], "login": escape(u["login"])} for u in users]
