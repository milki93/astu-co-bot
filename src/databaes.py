import sqlite3

from decouple import config

DATABASE_NAME = config("DATABASE_NAME", default="co_bot.db")
# connect the database
link = sqlite3.connect(DATABASE_NAME)

cursor = link.cursor()


def create_tables():
    """Define / create database tables"""

    USER_SQL = """CREATE TABLE IF NOT EXISTS department (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name  TEXT NOT NULL,
        short_name TEXT NOT NULL UNIQUE,
        num_sem INTEGER NOT NULL,
        school_id INTEGER,
        FOREIGN KEY (school_id) REFERENCES school(id)
    );
    """
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


# call the function to create tables
create_tables()
