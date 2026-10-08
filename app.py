from flask import Flask, jsonify
app = Flask(__name__)

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

@app.route("/")
def home():
    return jsonify(message="Welcome to ACEest Fitness & Gym"), 200

 @app.route("/programs", methods=["GET"])
 def list_programs():
     return jsonify(PROGRAMS), 200


 @app.route("/programs/<program_id>", methods=["GET"])
 def get_program(program_id):
     program = PROGRAMS.get(program_id)
     if not program:
         return jsonify(error="Program not found"), 404
     return jsonify(program), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
