from flask import Flask, jsonify, request

import os
import sqlite3

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify(message="Welcome to ACEest Fitness & Gym"), 200

DB_PATH = os.environ.get("ACEEST_DB", "aceest_fitness.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        # Client profiles
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                age INTEGER,
                height REAL,
                weight REAL,
                program TEXT,
                calories INTEGER
            )
        """)

        # Weekly progress tracking
        conn.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                week TEXT NOT NULL,
                adherence INTEGER NOT NULL
            )
        """)

        # Workout session logging
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                date TEXT NOT NULL,
                workout_type TEXT NOT NULL,
                duration_min INTEGER NOT NULL,
                notes TEXT
            )
        """)

        # Add membership expiry to existing client records
        columns = [
            row[1]
            for row in conn.execute("PRAGMA table_info(clients)")
        ]

        if "membership_expiry" not in columns:
            conn.execute(
                "ALTER TABLE clients ADD COLUMN membership_expiry TEXT"
            )

PROGRAMS = {
    "fat_loss": {
        "name": "Fat Loss (FL)",
        "workout": "Mon: 5x5 Back Squat + AMRAP; Tue: EMOM 20min Assault Bike; "
                   "Wed: Bench Press + 21-15-9; Thu: 10RFT Deadlifts/Box Jumps; "
                   "Fri: 30min Active Recovery",
        "diet": "B: 3 Egg Whites + Oats Idli; L: Grilled Chicken + Brown Rice; "
                "D: Fish Curry + Millet Roti; Target: 2000 kcal",
        "calorie_factor": 22,
    },
    "muscle_gain": {
        "name": "Muscle Gain (MG)",
        "workout": "Mon: Squat 5x5; Tue: Bench 5x5; Wed: Deadlift 4x6; "
                   "Thu: Front Squat 4x8; Fri: Incline Press 4x10; Sat: Barbell Rows 4x10",
        "diet": "B: 4 Eggs + PB Oats; L: Chicken Biryani (250g Chicken); "
                "D: Mutton Curry + Jeera Rice; Target: 3200 kcal",
        "calorie_factor": 35,
    },
    "beginner": {
        "name": "Beginner (BG)",
        "workout": "Circuit Training: Air Squats, Ring Rows, Push-ups. "
                   "Focus: Technique Mastery & Form (90% Threshold)",
        "diet": "Balanced meals: Idli-Sambar, Rice-Dal, Chapati. Protein: 120g/day",
        "calorie_factor": 26,
    },
}

@app.route("/programs", methods=["GET"])
def list_programs():
    return jsonify(PROGRAMS), 200


@app.route("/programs/<program_id>", methods=["GET"])
def get_program(program_id):
    program = PROGRAMS.get(program_id)

    if not program:
        return jsonify(error="Program not found"), 404

    return jsonify(program), 200

@app.route("/clients", methods=["POST"])
def create_client():
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    age = data.get("age")
    weight = data.get("weight")
    program = data.get("program")

    if not isinstance(name, str) or not name.strip():
        return jsonify(error="Client name is required"), 400

    if program not in PROGRAMS:
        return jsonify(error="Invalid fitness program"), 400

    try:
        age = int(age)
        weight = float(weight)
        if age <= 0 or weight <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify(error="Valid age and weight are required"), 400

    calories = int(weight * PROGRAMS[program]["calorie_factor"])

    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute(
                """
                INSERT INTO clients (name, age, weight, program, calories)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name.strip(), age, weight, program, calories)
            )
        except sqlite3.IntegrityError:
            return jsonify(error="Client already exists"), 409

    return jsonify(
        name=name.strip(),
        age=age,
        weight=weight,
        program=program,
        calories=calories
    ), 201

@app.route("/clients/<name>/progress", methods=["POST"])
def save_progress(name):
    data = request.get_json(silent=True) or {}

    week = data.get("week")
    adherence = data.get("adherence")

    if not isinstance(week, str) or not week.strip():
        return jsonify(error="Valid week is required"), 400

    if type(adherence) is not int or not 0 <= adherence <= 100:
        return jsonify(error="Adherence must be between 0 and 100"), 400

    with sqlite3.connect(DB_PATH) as conn:
        client = conn.execute(
            "SELECT id FROM clients WHERE name = ?", (name,)
        ).fetchone()

        if client is None:
            return jsonify(error="Client not found"), 404

        conn.execute(
            """
            INSERT INTO progress (client_name, week, adherence)
            VALUES (?, ?, ?)
            """,
            (name, week.strip(), adherence)
        )

    return jsonify(
        client_name=name,
        week=week.strip(),
        adherence=adherence
    ), 201

@app.route("/workouts", methods=["POST"])
def add_workout():
    data = request.get_json(silent=True) or {}

    name = data.get("client_name")
    workout_date = data.get("date")
    workout_type = data.get("workout_type")
    duration = data.get("duration_min")
    notes = data.get("notes", "")

    if not all(isinstance(x, str) and x.strip()
               for x in [name, workout_date, workout_type]):
        return jsonify(error="Client, date and workout type are required"), 400

    try:
        from datetime import date
        date.fromisoformat(workout_date)
    except ValueError:
        return jsonify(error="Date must be YYYY-MM-DD"), 400

    if type(duration) is not int or duration <= 0:
        return jsonify(error="Duration must be a positive integer"), 400

    if not isinstance(notes, str):
        return jsonify(error="Notes must be text"), 400

    with sqlite3.connect(DB_PATH) as conn:
        client = conn.execute(
            "SELECT id FROM clients WHERE name = ?", (name,)
        ).fetchone()

        if client is None:
            return jsonify(error="Client not found"), 404

        cursor = conn.execute(
            """
            INSERT INTO workouts
            (client_name, date, workout_type, duration_min, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, workout_date, workout_type, duration, notes)
        )

        workout_id = cursor.lastrowid

    return jsonify(
        id=workout_id,
        client_name=name,
        date=workout_date,
        workout_type=workout_type,
        duration_min=duration,
        notes=notes
    ), 201

from datetime import date

@app.route("/clients/<name>/membership", methods=["PUT", "GET"])
def membership(name):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        client = conn.execute(
            "SELECT * FROM clients WHERE name = ?", (name,)
        ).fetchone()

        if client is None:
            return jsonify(error="Client not found"), 404

        if request.method == "PUT":
            data = request.get_json(silent=True) or {}
            expiry = data.get("membership_expiry")

            try:
                date.fromisoformat(expiry)
            except (ValueError, TypeError):
                return jsonify(error="Use YYYY-MM-DD date format"), 400

            conn.execute(
                "UPDATE clients SET membership_expiry = ? WHERE name = ?",
                (expiry, name)
            )
        else:
            expiry = client["membership_expiry"]

    status = (
        "Active" if expiry and date.fromisoformat(expiry) >= date.today()
        else "Expired" if expiry else "Not Set"
    )

    return jsonify(
        client_name=name,
        membership_expiry=expiry,
        status=status
    ), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
