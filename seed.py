import sqlite3
from werkzeug.security import generate_password_hash

connection = sqlite3.connect("naposlusam.db")
cursor = connection.cursor()

shifts = [
("Opšta praksa I smena", "07:00", "14:00"),
("Opšta praksa II smena", "13:00", "20:00"),
("Opšta praksa vikend", "08:00", "18:00"),
("Pedijatrija I smena", "07:00", "14:00"),
("Pedijatrija II smena", "13:00", "20:00"),
("Pedijatrija subota", "08:00", "18:00"),
("Pedijatrija nedelja", "08:00", "18:00"),
("Specijalističke službe", "07:00", "15:00"),
("Zajedničke službe", "07:00", "15:00"),
("Stomatologija I smena", "07:00", "14:00"),
("Stomatologija II smena", "13:00", "20:00"),
("Stomatologija subota", "08:00", "16:00"),
("Ginekologija", "07:00", "14:00"),
("Ginekologija sreda", "07:00", "19:00"),
("Logoped", "07:00", "15:00"),
("Rendgen i ultrazvuk", "07:00", "13:00"),
("Laboratorija", "07:00", "13:00"),
("Laboratorija subota", "07:00", "14:00")
]

for shift in shifts:
    cursor.execute("INSERT INTO shifts (name, start_time, end_time) VALUES(?, ?, ?)", shift)

employees = [
    ("Bogdan Koroman", "Specijalističke službe", "Direktor", "1234"),
    ("Mina Marinkovic", "Opšta praksa", "Doktor", "5678"),
    ("Miljana Koroman", "Stomatologija", "Stomatolog", "0012")
]

for employee in employees:
    cursor.execute("INSERT INTO employees (name, department, position, pin) VALUES(?, ?, ?, ?)", employee)

cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", ("bogdankoroman", generate_password_hash("bogdan_koroman_123")))

cursor.execute("SELECT * FROM admins")
print(cursor.fetchall())

connection.commit()
connection.close()

print("Sve je dobro!")