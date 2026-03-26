from flask import Flask, render_template, url_for, request, redirect

import sqlite3

from flask import session

from werkzeug.security import check_password_hash

from datetime import datetime

app = Flask(__name__)
app.secret_key = "domzdravlja_tajni_kljuc"

@app.route("/")
def index():
    connection = sqlite3.connect("naposlusam.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM employees WHERE active = 1 ORDER BY department")
    result = cursor.fetchall()
    message = request.args.get("message")
    employees_by_departments = {}
    for employee in result:
       if employee[2] in employees_by_departments:
           employees_by_departments[employee[2]].append( (employee[0], employee[1]) )
       else:
           employees_by_departments[employee[2]] = [(employee[0], employee[1])]
    connection.close()
    return render_template("index.html", list_of_employees = employees_by_departments, message=message)

@app.route("/admin")
def admin():
    username=session.get("name")
    if username:
        return render_template("admin.html")
    else:
        return redirect(url_for('admin_login'))
    
@app.route("/admin/attendance")
def admin_attendance():
    username = session.get("name")
    if not username:
        return redirect(url_for('admin_login'))
    date = request.args.get("date")
    if date:
        connection = sqlite3.connect("naposlusam.db")
        cursor = connection.cursor()
        date_pattern = date + "%"
        cursor.execute("""
            SELECT check_ins.id, employees.name, employees.department, employees.position, shifts.name, check_ins.check_in, check_ins.check_out
            FROM check_ins
            JOIN employees ON check_ins.employee_id = employees.id
            JOIN shifts ON check_ins.shift_id = shifts.id
            WHERE check_ins.check_in LIKE ?
        """, (date_pattern,))
        table = cursor.fetchall()
        connection.close()
        return render_template("attendance.html", table=table, date_pattern=date_pattern)
    else:
        return render_template("attendance.html")    

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
                shift_start = datetime.strptime(result_shift[2], "%H:%M").time()
                current_time = datetime.now().time()
                if shift_start < current_time:
                    return redirect(url_for("index", message="Uspešna prijava. Kašnjenje je zabeleženo i biće prosleđeno nadležnim licima."))
                else:
                    return redirect(url_for("index", message="Uspešna prijava. Prijavili ste se za vašu smenu!"))
            else:
                connection = sqlite3.connect("naposlusam.db")
                cursor = connection.cursor()
                cursor.execute("UPDATE check_ins SET check_out = ? WHERE id = ?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), result_check_out[0]))
                connection.commit()
                connection.close()
                return redirect(url_for("index", message= "Uspešna odjava. Vaše radno vreme je zabeleženo."))
        else:
            return render_template("pin.html", result_shift=result_shift, result_id=result_id, error="Pogrešan PIN")
    else:
        return render_template("pin.html", result_shift=result_shift, result_id=result_id)
    
@app.route("/admin/login", methods=["POST", "GET"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        connection = sqlite3.connect("naposlusam.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM admins WHERE username= ?", (username,))
        admin = cursor.fetchone()
        connection.close()
        if admin:
            password_check = check_password_hash(admin[2], password)
            if password_check == True:
                session['name'] = username
                return redirect(url_for('admin'))
            else:
                return render_template("login.html", error="Pogrešna lozinka. Pokušajte ponovo!")
        else:
            return render_template("login.html", error="Ne postoji admin pod unetim korisničkim imenom. Unesite tačno korisničko ime!")
    else:
        return render_template("login.html")
    
@app.route("/admin/logout")
def admin_logout():
    session.pop('name', None)
    return redirect(url_for('admin_login'))

@app.route("/admin/employees", methods=["POST", "GET"])
def admin_employees():
    username=session.get("name")
    if not username:
        return redirect(url_for('admin_login'))
    connection = sqlite3.connect("naposlusam.db")
    cursor = connection.cursor()
    if request.method == "POST":
        name = request.form["name"]
        department = request.form["department"]
        position = request.form["position"]
        pin = request.form["pin"]
        cursor.execute("INSERT INTO employees (name, department, position, pin) VALUES(?, ?, ?, ?)", (name, department, position, pin))
        connection.commit()
        connection.close()
        return redirect(url_for('admin_employees'))
    else:
        cursor.execute("SELECT * FROM employees WHERE active = 1 ORDER BY department")
        employees = cursor.fetchall()
        message = request.args.get("message")
        employees_by_departments = {}
        for employee in employees:
            if employee[2] in employees_by_departments:
                employees_by_departments[employee[2]].append( (employee[0], employee[1], employee[3]))
            else:
                employees_by_departments[employee[2]] = [(employee[0], employee[1], employee[3])]
        connection.close()
        return render_template("employees.html", employees_by_departments=employees_by_departments, message=message)

@app.route("/admin/employees/delete/<int:employee_id>", methods=["POST"])
def admin_employees_delete(employee_id):
    username=session.get("name")
    if not username:
        return redirect(url_for('admin_login'))
    connection = sqlite3.connect("naposlusam.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE employees SET active = 0 WHERE ID = ?", (employee_id,))
    connection.commit()
    connection.close()
    return redirect(url_for('admin_employees'))

@app.route("/admin/employees/edit/<int:employee_id>", methods=["POST", "GET"])
def admin_employees_edit(employee_id):
    username = session.get("name")
    if not username:
        return redirect(url_for('admin_login'))
    connection = sqlite3.connect("naposlusam.db")
    cursor = connection.cursor()
    if request.method == "GET":
        cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
        employee = cursor.fetchone()
        connection.close()
        return render_template("edit_employee.html", employee=employee)
    else:
        name = request.form["name"]
        department = request.form["department"]
        position = request.form["position"]
        pin = request.form["pin"]
        cursor.execute("UPDATE employees SET name = ?, department = ?, position = ?, pin = ? WHERE id = ?", (name, department, position, pin, employee_id))
        connection.commit()
        connection.close()
        return redirect(url_for('admin_employees', message="Uspešno ste ažurirali podatke zaposlenog."))
    

@app.route("/admin/attendance/edit/<int:check_ins_id>", methods=["POST", "GET"])
def admin_attendance_edit(check_ins_id):
    username=session.get("name")
    if not username:
            return redirect(url_for('admin_login'))
    if request.method == "GET":
        connection = sqlite3.connect("naposlusam.db")
        cursor = connection.cursor()
        cursor.execute("""
            SELECT employees.name, employees.department, shifts.name, check_in, check_out, check_ins.id
            FROM check_ins
            JOIN employees ON check_ins.employee_id = employees.id
            JOIN shifts ON check_ins.shift_id = shifts.id
            WHERE check_ins.id = ?
        """, (check_ins_id,))
        check_in_row=cursor.fetchone()
        connection.close()
        return render_template("attendance_edit.html", check_in_row=check_in_row)
    else:
        check_in=request.form["check_in"]
        check_out=request.form["check_out"]
        connection = sqlite3.connect("naposlusam.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE check_ins SET check_in = ?, check_out= ? WHERE id= ?", (check_in, check_out, check_ins_id))
        connection.commit()
        connection.close()
        return redirect(url_for('admin_attendance', message="Uspešno ste ažurirali evidenciju zaposlenog."))

if __name__ == "__main__":
    app.run(debug=True)

