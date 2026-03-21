import sqlite3

connection = sqlite3.connect("naposlusam.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        position TEXT NOT NULL,
        pin TEXT NOT NULL   
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS shifts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS check_ins(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        shift_id INTEGER NOT NULL,
        check_in TEXT NOT NULL,
        check_out TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(id),
        FOREIGN KEY(shift_id) REFERENCES shifts(id)
    )
""")

connection.commit()
connection.close()

print("Database added successfully!")