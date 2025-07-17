from flask import render_template, request
from app import app
import joblib
import os
import sqlite3

# Load model and vectorizer
model = joblib.load(os.path.join("app", "ml_model", "ticket_classifier.pkl"))
vectorizer = joblib.load(os.path.join("app", "ml_model", "ticket_vectorizer.pkl"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/classify", methods=["GET", "POST"])
def classify_ticket():
    if request.method == "POST":
        ticket = request.form["ticket"]
        pred = model.predict(vectorizer.transform([ticket]))[0]
        return render_template("classify_ticket.html", prediction=pred, ticket=ticket)
    return render_template("classify_ticket.html")

@app.route("/checkin", methods=["GET", "POST"])
def checkin():
    if request.method == "POST":
        name = request.form["name"]
        contact = request.form["contact"]
        visiting = request.form["visiting"]

        # Save to database
        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO checkins (name, contact, visiting) VALUES (?, ?, ?)", (name, contact, visiting))
        conn.commit()
        conn.close()

        return render_template("checkin.html", success=True, name=name)
    return render_template("checkin.html")

@app.route("/schedule", methods=["GET", "POST"])
def schedule():
    if request.method == "POST":
        staff_name = request.form["staff_name"]
        visitor_name = request.form["visitor_name"]
        date = request.form["date"]
        time = request.form["time"]

        # Save to database
        conn = sqlite3.connect("app/database.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO appointments (staff_name, visitor_name, date, time) VALUES (?, ?, ?, ?)",
            (staff_name, visitor_name, date, time)
        )
        conn.commit()
        conn.close()

        return render_template("schedule.html", success=True, visitor_name=visitor_name)
    return render_template("schedule.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")
