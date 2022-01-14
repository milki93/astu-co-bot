import sqlite3
from threading import current_thread

from decouple import Csv, config

DATABASE_NAME = config("DATABASE_NAME", default="astu_co_bot.db")
SUPERADMINS = [
    int(item) if item.isdigit() else item.lower()
    for item in config("SUPERADMINS", cast=Csv())
]

# connect the database
link = sqlite3.connect(DATABASE_NAME, check_same_thread=False)

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
            school_id INTEGER,
            FOREIGN KEY (school_id) REFERENCES school(id)
        );
        """
    COURSE_OUTLINE_SQL = """CREATE TABLE IF NOT EXISTS course_outline (
            course_code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            semester INTEGER NOT NULL,
            file_id TEXT NOT NULL,
            year INTEGER NOT NULL,
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
    username = user.username or ""
    first_name = user.first_name
    last_name = user.last_name
    cursor.execute(
        "INSERT OR IGNORE INTO user (id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
        (user_id, username.lower(), first_name, last_name),
    )
    link.commit()


def is_superadmin(user):
    """Checks if the user is superadmin."""
    return (
        user.id in SUPERADMINS
        or user.username.lower() in SUPERADMINS
        or "@" + user.username.lower() in SUPERADMINS
    )


def is_admin(user):
    """Checks if the user is admin."""
    if is_superadmin(user):
        return True
    result = cursor.execute("SELECT is_admin FROM user WHERE id = ?", (user.id,))
    return result.fetchone()[0]


def list_admins():
    result = cursor.execute("SELECT first_name, username FROM user WHERE is_admin=1")
    return result.fetchall()


def add_admin(user):
    user = user.lstrip("@")
    result = cursor.execute("SELECT * FROM user WHERE username=? OR id=?", (user.lower(), user))
    if result.fetchall() == []:
        return False
    cursor.execute(
        "UPDATE user SET is_admin=1 WHERE username=? OR id=?", (user.lower(), user)
    )
    link.commit()
    return True


def remove_admin(user):
    user = user.lstrip("@")
    cursor.execute(
        "UPDATE user SET is_admin=0 WHERE username=? OR id=?", (user.lower(), user)
    )
    link.commit()


def add_school(school_name, school_short_name):
    cursor.execute(
        "INSERT OR IGNORE INTO school (name, short_name) VALUES (?, ?)",
        (school_name, school_short_name),
    )
    link.commit()


def add_department(department_name, dept_short_name ,school_id):
    cursor.execute(
        "INSERT OR IGNORE INTO department (name, short_name, school_id) VALUES (?,  ?, ?)",
        (department_name, dept_short_name ,school_id),
    )
    link.commit()
# def remove_school(school_id):
#     cursor.execute("DELETE FROM school WHERE id=?" ,(school_id))
#     link.commit()

def list_schools():
    result = cursor.execute("SELECT id, short_name FROM school")
    return result.fetchall()


def list_departments(sch_id):
    result = cursor.execute(
        "SELECT id,short_name FROM department WHERE school_id=?", (sch_id,)
    )
    return result.fetchall()
def list_year(dept_id):
    result = cursor.execute(
        "SELECT year FROM course_outline WHERE department_id =?", (dept_id,)
    )
    return result.fetchall()

def add_course(course_code, course_name, sem, file_id, year, dept_id):
    cursor.execute(
        "INSERT OR IGNORE INTO course_outline (course_code, name, semester, file_id, year, department_id) VALUES (?, ?, ?, ?, ?, ?)",
        (course_code, course_name, sem, file_id, year, dept_id),
    )
    link.commit()
def list_sem(year):
    result = cursor.execute(
        "SELECT  semester FROM course_outline WHERE year=?", (year,)
    )
    return result.fetchall()
def list_course(dept_id, year, semes):
    result = cursor.execute(
        "SELECT course_code, name FROM course_outline WHERE department_id =? AND year=? AND semester=? ", (dept_id,year,semes)
    )
    return result.fetchall()

def get_file_id(cid):
    result = cursor.execute(
        "SELECT file_id FROM course_outline WHERE course_code=?", (cid,)
    )
    return result.fetchone()

# call the function to create tables
create_tables()
