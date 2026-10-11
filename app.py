from flask import Flask, jsonify, request

import os
import sqlite3

app = Flask(__name__)

DB_PATH = os.environ.get("ACEEST_DB", "aceest_fitness.db")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
