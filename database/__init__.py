from database.db import db
from database.models import (
    User, Profile, FitnessGoals, WorkoutPlans, DietPlans,
    ProgressTracking, Feedback, Recommendations, HydrationRecords,
    WeatherHistory, HealthMetrics, NutritionLogs, MCPLogs
)
import json
from datetime import datetime

_app = None

def get_app():
    global _app
    if _app is None:
        from backend import create_app
        _app = create_app()
    return _app

def init_db():
    app = get_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database initialized (all tables dropped and recreated).")

def save_user_profile(profile, goals, diet, workouts):
    app = get_app()
    with app.app_context():
        email = profile.get('email') or f"{profile['name'].lower().replace(' ', '_')}@example.com"
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email)
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

        new_profile = Profile(
            user_id=user.id,
            name=profile['name'],
            age=profile['age'],
            gender=profile['gender'],
            height=profile['height'],
            weight=profile['weight'],
            fitness_goal=profile['fitness_goal'],
            activity_level=profile['activity_level'],
            diet_preference=profile['diet_preference'],
            water_intake=profile['water_intake'],
            sleep_hours=profile['sleep_hours'],
            workout_experience=profile['workout_experience'],
            medical_conditions=profile.get('medical_conditions', 'None'),
            injuries=profile.get('injuries', 'None'),
            allergies=profile.get('allergies', 'None')
        )
        db.session.add(new_profile)
        db.session.commit()

        # Save FitnessGoals
        fg = FitnessGoals(
            profile_id=new_profile.id,
            bmi=goals['bmi'],
            bmi_category=goals['bmi_category'],
            bmr=goals['bmr'],
            tdee=goals['tdee'],
            target_calories=goals['target_calories'],
            target_protein=goals['target_protein'],
            target_carbs=goals['target_carbs'],
            target_fat=goals['target_fat'],
            confidence_score=goals['confidence_score'],
            advisory_notes=json.dumps(goals['advisory_notes'])
        )
        db.session.add(fg)

        # Save WorkoutPlans
        for day, exercises in workouts.items():
            db.session.add(WorkoutPlans(
                profile_id=new_profile.id,
                day_of_week=day,
                exercises=json.dumps(exercises)
            ))

        # Save DietPlans
        for meal in diet:
            db.session.add(DietPlans(
                profile_id=new_profile.id,
                meal_type=meal['meal_type'],
                food_items=json.dumps(meal['food_items']),
                calories=meal['calories'],
                protein=meal['protein'],
                carbohydrates=meal['carbohydrates'],
                fats=meal['fats']
            ))

        today_str = datetime.today().strftime('%Y-%m-%d')

        # Save default Hydration Record
        hydration_target = goals.get('hydration_target_l', profile['water_intake'])
        db.session.add(HydrationRecords(
            profile_id=new_profile.id,
            log_date=today_str,
            target_l=hydration_target,
            consumed_l=profile['water_intake']
        ))

        # Save initial HealthMetrics
        meds = (profile.get('medical_conditions') or 'None').lower()
        bp = "138/88" if "hypertension" in meds else "118/76"
        sugar = 132.0 if "diabetes" in meds else 92.0
        db.session.add(HealthMetrics(
            profile_id=new_profile.id,
            log_date=today_str,
            blood_pressure=bp,
            heart_rate=72,
            blood_sugar=sugar,
            notes="Initial clinical screening vitals"
        ))

        # Save initial NutritionLog from first meal
        if diet and diet[0].get('food_items'):
            first_food = diet[0]['food_items'][0]
            db.session.add(NutritionLogs(
                profile_id=new_profile.id,
                log_date=today_str,
                food_name=first_food.get('name', 'Oats'),
                quantity_g=float(first_food.get('serving_g', 100.0)),
                calories=diet[0]['calories'],
                protein=diet[0]['protein'],
                carbs=diet[0]['carbohydrates'],
                fat=diet[0]['fats']
            ))

        # Save Recommendations & MCP audit log
        rec_outputs = {
            "predicted_goal": goals.get("predicted_goal", profile["fitness_goal"]),
            "goal_confidence": goals.get("goal_confidence", 0.92),
            "predicted_risks": goals.get("predicted_risks", {
                "obesity_risk": "Low Risk",
                "sedentary_risk": "Low Risk",
                "metabolic_risk": "Low Risk"
            }),
            "diet_knn_suggestion": goals.get("diet_knn_suggestion", {"suggested_preference": profile["diet_preference"]}),
            "weather_context": goals.get("weather_context"),
            "hydration_target_l": hydration_target
        }
        db.session.add(Recommendations(
            profile_id=new_profile.id,
            model_name="XGBoost + RF + DecisionTree + KNN Pipeline",
            inputs=json.dumps(profile),
            outputs=json.dumps(rec_outputs),
            score=goals['confidence_score']
        ))

        db.session.add(MCPLogs(
            profile_id=new_profile.id,
            mcp_name="Profile & Plan Orchestrator MCP",
            tool_name="generate_full_profile",
            input_params=json.dumps({"goal": profile['fitness_goal'], "diet": profile['diet_preference']}),
            output_data=json.dumps({"target_calories": goals['target_calories'], "confidence": goals['confidence_score']})
        ))

        db.session.commit()
        return new_profile.id

def log_progress(profile_id, progress_entry):
    app = get_app()
    with app.app_context():
        log_entry = ProgressTracking(
            profile_id=profile_id,
            log_date=progress_entry['log_date'],
            weight=progress_entry['weight'],
            water_intake=progress_entry['water_intake'],
            sleep_hours=progress_entry['sleep_hours'],
            calories_consumed=progress_entry.get('calories_consumed', 0.0),
            calories_burned=progress_entry.get('calories_burned', 0.0)
        )
        db.session.add(log_entry)
        db.session.commit()

def save_feedback(user_id, rating, comments, log_date):
    app = get_app()
    with app.app_context():
        fb = Feedback(
            profile_id=user_id,
            rating=rating,
            comments=comments,
            log_date=log_date
        )
        db.session.add(fb)
        db.session.commit()
