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
    cursor.execute("SELECT * FROM employees ORDER BY department")
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

if __name__ == "__main__":
    app.run(debug=True)
