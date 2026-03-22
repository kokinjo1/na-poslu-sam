from flask import Flask, render_template, url_for, request, redirect

import sqlite3

from datetime import datetime

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

@app.route("/employee/<int:employee_id>/shift/<int:shift_id>", methods=["POST", "GET"])
def pin(employee_id, shift_id):
    connection = sqlite3.connect("naposlusam.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM employees WHERE id=?", (employee_id,))
    result_id = cursor.fetchone()
    cursor.execute("SELECT * FROM shifts WHERE id= ?", (shift_id,))
    result_shift = cursor.fetchone()
    cursor.execute("SELECT * FROM check_ins WHERE employee_id = ? AND check_out IS NULL", (employee_id,))
    result_check_out = cursor.fetchone()
    connection.close()
    if request.method == "POST":
        pin = request.form["pin"]
        if pin == result_id[4]:
            if result_check_out == None:
                connection = sqlite3.connect("naposlusam.db")
                cursor = connection.cursor()
                cursor.execute("INSERT INTO check_ins (employee_id, shift_id, check_in) VALUES(?, ?, ?)", (employee_id, shift_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                connection.commit()
                connection.close()
                shift_start = datetime.strptime(result_shift[2], "%H:%M")
                current_time = datetime.strptime(datetime.now().strftime("%H:%M"), "%H:%M")
                if shift_start < current_time:
                    return render_template("confirmation.html", message = "Uspešna prijava. Kašnjenje je zabeleženo i biće prosleđeno nadležnima.")
                else:
                    return render_template("confirmation.html", message = "Uspešna prijava. Prijavljeni ste na smenu.")
            else:
                connection = sqlite3.connect("naposlusam.db")
                cursor = connection.cursor()
                cursor.execute("UPDATE check_ins SET check_out = ? WHERE id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), result_check_out[0]))
                connection.commit()
                connection.close()
                return render_template("confirmation.html", message = "Uspešna odjava. Vaše radno vreme je zabeleženo.")
        else:
            return render_template("pin.html", result_shift=result_shift, result_id=result_id, error="Pogrešan PIN")
    else:
        return render_template("pin.html", result_shift=result_shift, result_id=result_id)



if __name__ == "__main__":
    app.run(debug=True)