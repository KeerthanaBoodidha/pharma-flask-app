from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "Pharma_secret"

# ---------------- DATABASE ----------------
db = sqlite3.connect("pharma.db", check_same_thread=False)
cursor = db.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    quantity INTEGER,
    price REAL,
    expiry TEXT
)
''')

db.commit()

# ---------------- HOME ROUTE ----------------
@app.route("/")
def home():
    return redirect("/login")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "INSERT INTO users (username, password) VALUES (?, ?)"
        cursor.execute(sql, (username, password))
        db.commit()

        return redirect("/login")
    
    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT * FROM users WHERE username=? AND password=?"
        cursor.execute(sql, (username, password))
        user = cursor.fetchone()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid username or password"
    
    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", username=session["user"])
    else:
        return redirect("/login")

# ---------------- MEDICINES ----------------
@app.route("/medicines")
def medicines():
    if "user" not in session:
        return redirect("/login")

    today = date.today()

    cursor.execute("SELECT name, quantity, price, expiry FROM medicines")
    rows = cursor.fetchall()

    medicines = []

    for name, quantity, price, expiry in rows:
        if expiry and expiry < str(today):
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

# ---------------- ADD MEDICINE ----------------
@app.route("/add_medicine", methods=["GET", "POST"])
def add_medicine():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        quantity = int(request.form["quantity"])
        price = float(request.form["price"])
        expiry = request.form["expiry"]

        sql = "INSERT INTO medicines (name, quantity, price, expiry) VALUES (?, ?, ?, ?)"
        cursor.execute(sql, (name, quantity, price, expiry))
        db.commit()

        return redirect("/medicines")

    return render_template("add_medicine.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
