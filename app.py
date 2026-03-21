from flask import Flask, render_template, url_for

import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    connection = sqlite3.connect("naposlusam.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM employees ORDER BY department")
    result = cursor.fetchall()
    employees_by_departments = {}
    for employee in result:
       if employee[2] in employees_by_departments:
           employees_by_departments[employee[2]].append( (employee[0], employee[1]) )
       else:
           employees_by_departments[employee[2]] = [(employee[0], employee[1])]
    connection.close()
    return render_template("index.html", list_of_employees = employees_by_departments)

@app.route("/employee/<int:employee_id>")
def employee(employee_id):
    connection = sqlite3.connect("naposlusam.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM employees WHERE id=?", (employee_id,))
    result_id = cursor.fetchone()
    cursor.execute("SELECT * FROM shifts")
    result_shifts = cursor.fetchall()
    connection.close()
    return render_template("shift.html", result_id=result_id, result_shifts=result_shifts)



if __name__ == "__main__":
    app.run(debug=True)