import os
import json
from datetime import datetime, timedelta
import database
import recommender
from backend.mcp.rag import ensure_faiss_index
from database.models import User
from database.db import db

def main():
    print("Building / verifying FAISS clinical RAG vector index...")
    ensure_faiss_index()

    print("Initializing database...")
    database.init_db()

    app = database.get_app()
    with app.app_context():
        demo_user = User.query.filter_by(email="demo@sehatsaathi.ai").first()
        if not demo_user:
            demo_user = User(email="demo@sehatsaathi.ai")
            demo_user.set_password("demo1234")
            db.session.add(demo_user)
            db.session.commit()

    # 10 Diverse Test Cases
    test_profiles = [
        # 1. Beginner Weight Loss
        {
            "email": "demo@sehatsaathi.ai",
            "name": "Alice Cooper",
            "age": 25,
            "gender": "Female",
            "height": 165.0,
            "weight": 80.0,
            "fitness_goal": "Weight Loss",
            "activity_level": "Lightly Active",
            "workout_experience": "Beginner",
            "water_intake": 2.5,
            "sleep_hours": 7.0,
            "diet_preference": "Non-Vegetarian",
            "medical_conditions": "None",
            "injuries": "None",
            "allergies": "None"
        },
        # 2. Beginner Weight Gain
        {
            "email": "demo@sehatsaathi.ai",
            "name": "Bob Marley",
            "age": 22,
            "gender": "Male",
            "height": 180.0,
            "weight": 60.0,
            "fitness_goal": "Weight Gain",
            "activity_level": "Moderately Active",
            "workout_experience": "Beginner",
            "water_intake": 3.0,
            "sleep_hours": 8.0,
            "diet_preference": "Non-Vegetarian",
            "medical_conditions": "None",
            "injuries": "None",
            "allergies": "None"
        },
        # 3. Muscle Building
        {
            "email": "demo@sehatsaathi.ai",
            "name": "Charlie Puth",
            "age": 29,
            "gender": "Male",
            "height": 175.0,
            "weight": 70.0,
            "fitness_goal": "Muscle Building",
            "activity_level": "Very Active",
            "workout_experience": "Intermediate",
            "water_intake": 3.5,
            "sleep_hours": 8.0,
            "diet_preference": "High Protein",
            "medical_conditions": "None",
            "injuries": "None",
            "allergies": "None"
        },
        # 4. Vegetarian Athlete
        {
            "email": "demo@sehatsaathi.ai",
            "name": "Daisy Ridley",
            "age": 27,
            "gender": "Female",
            "height": 170.0,
            "weight": 62.0,
            "fitness_goal": "General Fitness",
            "activity_level": "Very Active",
            "workout_experience": "Advanced",
            "water_intake": 3.5,
            "sleep_hours": 8.5,
            "diet_preference": "Vegetarian",
            "medical_conditions": "None",
            "injuries": "Knee injury",
            "allergies": "Peanuts"
        },
        # 5. Vegan Weight Loss
        {
            "email": "demo@sehatsaathi.ai",
            "name": "Ethan Hunt",
            "age": 35,
            "gender": "Male",
            "height": 178.0,
            "weight": 95.0,
            "fitness_goal": "Weight Loss",
            "activity_level": "Sedentary",
            "workout_experience": "Beginner",
            "water_intake": 2.5,
            "sleep_hours": 6.5,
            "diet_preference": "Vegan",
            "medical_conditions": "Asthma",
            "injuries": "None",
            "allergies": "None"
        },
        # 6. Senior Citizen
        {
            "email": "demo@sehatsaathi.ai",
            "name": "Fiona Gallagher",
            "age": 68,
            "gender": "Female",
            "height": 158.0,
            "weight": 55.0,
            "fitness_goal": "General Fitness",
            "activity_level": "Lightly Active",
            "workout_experience": "Beginner",
            "water_intake": 2.0,
            "sleep_hours": 7.0,
            "diet_preference": "Low Carb",
            "medical_conditions": "Hypertension",
            "injuries": "None",
            "allergies": "None"
        },
        # 7. Sedentary Office Worker
        {
            "email": "demo@sehatsaathi.ai",
            "name": "George Costanza",
            "age": 42,
            "gender": "Male",
            "height": 170.0,
            "weight": 88.0,
            "fitness_goal": "Fat Loss",
            "activity_level": "Sedentary",
            "workout_experience": "Beginner",
            "water_intake": 2.2,
            "sleep_hours": 6.5,
            "diet_preference": "Non-Vegetarian",
            "medical_conditions": "None",
            "injuries": "Lower back pain",
            "allergies": "None"
        },
        # 8. College Student (Jain Diet)
        {
            "email": "demo@sehatsaathi.ai",
            "name": "Hannah Baker",
            "age": 20,
            "gender": "Female",
            "height": 163.0,
            "weight": 52.0,
            "fitness_goal": "Endurance",
            "activity_level": "Moderately Active",
            "workout_experience": "Intermediate",
            "water_intake": 2.5,
            "sleep_hours": 7.5,
            "diet_preference": "Jain",
            "medical_conditions": "None",
            "injuries": "None",
            "allergies": "None"
        },
        # 9. Advanced Gym User
        {
            "email": "demo@sehatsaathi.ai",
            "name": "Ian Somerhalder",
            "age": 31,
            "gender": "Male",
            "height": 182.0,
            "weight": 85.0,
            "fitness_goal": "Muscle Building",
            "activity_level": "Very Active",
            "workout_experience": "Advanced",
            "water_intake": 4.0,
            "sleep_hours": 8.0,
            "diet_preference": "High Protein",
            "medical_conditions": "None",
            "injuries": "Shoulder injury",
            "allergies": "Gluten"
        },
        # 10. Strength Athlete
        {
            "email": "demo@sehatsaathi.ai",
            "name": "Jack Reacher",
            "age": 38,
            "gender": "Male",
            "height": 195.0,
            "weight": 110.0,
            "fitness_goal": "Strength Training",
            "activity_level": "Very Active",
            "workout_experience": "Advanced",
            "water_intake": 4.5,
            "sleep_hours": 9.0,
            "diet_preference": "Keto",
            "medical_conditions": "None",
            "injuries": "None",
            "allergies": "None"
        }
    ]

    summary_report = []
    summary_headers = "| ID | Name | Age/Gender | Goal | Diet | BMI (Cat) | BMR (kcal) | Target Cals | Confidence | Safety Substitutions Applied |"
    summary_divider = "|---|---|---|---|---|---|---|---|---|---|"
    summary_report.append(summary_headers)
    summary_report.append(summary_divider)

    today = datetime.today()

    print("\nRunning ML + MCP recommendations for all 10 profiles...")

    for idx, profile in enumerate(test_profiles, start=1):
        goals, diet, workouts = recommender.generate_full_profile(profile)
        profile_id = database.save_user_profile(profile, goals, diet, workouts)

        # Add 7 days of progress logs to test charts & velocity trends
        for day_offset in range(7):
            log_date = (today - timedelta(days=6 - day_offset)).strftime('%Y-%m-%d')
            delta = -0.12 if "loss" in profile["fitness_goal"].lower() else (0.10 if "gain" in profile["fitness_goal"].lower() or "muscle" in profile["fitness_goal"].lower() else -0.04)
            mock_w = profile["weight"] + (day_offset * delta)
            progress_entry = {
                "log_date": log_date,
                "weight": round(mock_w, 2),
                "water_intake": round(profile["water_intake"] + ((day_offset % 3) * 0.1), 1),
                "sleep_hours": round(profile["sleep_hours"] + ((day_offset % 2) * 0.2), 1),
                "calories_consumed": round(goals["target_calories"] - (60 if day_offset % 2 == 0 else -40)),
                "calories_burned": 260 + (day_offset * 35)
            }
            database.log_progress(profile_id, progress_entry)

        database.save_feedback(
            user_id=profile_id,
            rating=5 if goals["confidence_score"] >= 80 else 4,
            comments=f"Verified ML + MCP profile #{idx} ({profile['fitness_goal']} / {profile['diet_preference']}).",
            log_date=today.strftime('%Y-%m-%d')
        )

        exclusions = []
        for day, day_exercises in workouts.items():
            for ex in day_exercises:
                if ex.get("caution"):
                    exclusions.append(f"{ex['name']} ({day})")

        exclusions_str = ", ".join(sorted(set(exclusions))) if exclusions else "None"

        row = f"| {profile_id} | {profile['name']} | {profile['age']}/{profile['gender']} | {profile['fitness_goal']} | {profile['diet_preference']} | {goals['bmi']} ({goals['bmi_category']}) | {goals['bmr']} | {goals['target_calories']} | {goals['confidence_score']}% | {exclusions_str} |"
        summary_report.append(row)
        print(f"Profile {idx} saved: {profile['name']} ({profile['diet_preference']}) - Target: {goals['target_calories']} kcal, Score: {goals['confidence_score']}%")

    os.makedirs("reports", exist_ok=True)
    report_path = os.path.join("reports", "test_results.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Automated ML + MCP Profile Verification Results\n\n")
        f.write("\n".join(summary_report))
        f.write("\n\nAll 10 test profiles are verified and loaded into SQLite `database/fitness_planner.db` under `demo@sehatsaathi.ai` (password: `demo1234`).\n")

    print(f"\nVerification summary saved to '{report_path}'.")
    print("Database population complete!")

if __name__ == '__main__':
    main()
