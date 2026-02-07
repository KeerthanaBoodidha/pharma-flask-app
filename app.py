from flask import Flask, render_template, request, redirect, session
import mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = "Pharma_secret"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="MySQL@123",
    database="pharma"
)
cursor = db.cursor()

#------------- REGISTER ----------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "insert into users (username, password) values (%s, %s)"
        values = (username, password)
        cursor.execute(sql, values)
        db.commit()

        return redirect("login")
    return render_template("register.html")

#--------------------LOGIN ----------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "select * from users where username=%s and password=%s"
        values = (username, password)
        cursor.execute(sql, values)

        user = cursor.fetchone()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid username or password"
        
    return render_template("login.html")

#------------------- DASHBOARD -----------------------------------
@app.route("/dashboard")
def dashboard():
        if "user" in session:
             return render_template(
                  "dashboard.html",
                  username=session["user"]
             )
        else:
           return redirect("/login")
        
#------------------- MEDICINES ----------------------------------------
@app.route("/medicines")
def medicines():
    if "user" not in session:
        return redirect("/login")

    today = date.today()

    # ✅ Use REAL column names
    cursor.execute(
        "SELECT name, quantity, price, expiry FROM medicines"
    )
    rows = cursor.fetchall()

    medicines = []

    for name, quantity, price, expiry in rows:
        if expiry and expiry < today:
            status = "Expired"
        elif quantity == 0:
            status = "Out of Stock"
        else:
            status = "Available"

        medicines.append({
            "name": name,
            "quantity": quantity,
            "price": price,
            "expiry": expiry,
            "status": status
        })

    return render_template("medicines.html", medicines=medicines)

#------------------------- ADD MEDICINE -------------------------------


# ---------------- Add Medicine -------------------
@app.route("/add_medicine", methods=["GET", "POST"])
def add_medicine():
    if "user" not in session:
        return redirect("/Login")
    
    if request.method == "POST":
        name = request.form["name"]
        quantity = int(request.form["quantity"])
        price = float(request.form["price"])
        expiry = request.form["expiry"]  # format YYYY-MM-DD

        sql = "INSERT INTO medicines (name, quantity, price, expiry) VALUES (%s, %s, %s, %s)"
        values = (name, quantity, price, expiry)
        cursor.execute(sql, values)
        db.commit()

        return redirect("/medicines")  # go back to medicines list after adding

    return render_template("add_medicine.html")




#---------------------LOGUOT --------------------------------------
@app.route("/logout")
def logout():
     session.pop("user", None)
     return redirect("/login")



if __name__ == "__main__":
     app.run(debug=True)
