import sqlite3

from decouple import config, Csv

DATABASE_NAME = config("DATABASE_NAME", default="astu_co_bot.db")
SUPERADMINS = config("SUPERADMINS", cast=Csv())

# connect the database
link = sqlite3.connect(DATABASE_NAME)

cursor = link.cursor()


def create_tables():
    """Define / create database tables"""

    USER_SQL = """CREATE TABLE IF NOT EXISTS user (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT,
            is_admin INTEGER DEFAULT 0,
            date_registerd DATETIME DEFAULT CURRENT_TIMESTAMP
        );"""
    SCHOOL_SQL = """CREATE TABLE IF NOT EXISTS school (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            short_name TEXT NOT NULL UNIQUE
        );
        """
    DEPARTMENT_SQL = """CREATE TABLE IF NOT EXISTS department (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT NOT NULL,
            short_name TEXT NOT NULL UNIQUE,
            num_sem INTEGER NOT NULL,
            school_id INTEGER,
            FOREIGN KEY (school_id) REFERENCES school(id)
        );
        """
    COURSE_OUTLINE_SQL = """CREATE TABLE IF NOT EXISTS course_outline (
            course_code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            semester INTEGER NOT NULL,
            file_id TEXT NOT NULL,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES department(id)
        );"""

    cursor.execute(USER_SQL)
    cursor.execute(SCHOOL_SQL)
    cursor.execute(DEPARTMENT_SQL)
    cursor.execute(COURSE_OUTLINE_SQL)


def register_user(user):
    """The function that register users."""
    user_id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    cursor.execute(
        "INSERT INTO user (id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
        (user_id, username, first_name, last_name),
    )
    link.commit()


def is_superadmin(user):
    """Checks if the user is superadmin."""
    return user.id in SUPERADMINS or user.username in SUPERADMINS


def is_admin(user):
    """Checks if the user is admin."""
    if is_superadmin(user):
        return True
    result = cursor.execute("SELECT is_admin FROM user WHERE id = ?", (user.id,))
    return result.fetchone()[0]


# call the function to create tables
create_tables()
