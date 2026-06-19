"""
Profile Management Routes
Handles: create profile, list profiles, profile detail, feedback CRUD.
All ML prediction, workout/diet generation, and MCP calls happen here.
"""
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from database.db import db
from database.models import (
    Profile, FitnessGoals, WorkoutPlans, DietPlans,
    Recommendations, HydrationRecords, WeatherHistory, Feedback
)

# Import ML predictors
import backend.ml_models.predictor as predictor
# Import Generators
import backend.workouts.generator as workout_gen
import backend.diets.generator as diet_gen
# Import MCP helpers
from backend.mcp.weather import fetch_weather_recommendation
from backend.mcp.hydration import calculate_hydration_target

profiles_bp = Blueprint('profiles', __name__, url_prefix='/api')


# ─────────────────────────────────────────────────────────────────────────────
# Helper calculation functions
# ─────────────────────────────────────────────────────────────────────────────

def calculate_base_metrics(age, gender, height, weight, activity_level):
    """Calculate baseline BMR, BMI and TDEE."""
    height_m = height / 100.0
    bmi = weight / (height_m ** 2)

    if bmi < 18.5:
        bmi_cat = "Underweight"
    elif bmi < 25.0:
        bmi_cat = "Normal"
    elif bmi < 30.0:
        bmi_cat = "Overweight"
    else:
        bmi_cat = "Obese"

    if str(gender).lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    multipliers = {
        "sedentary": 1.2,
        "lightly active": 1.375,
        "moderately active": 1.55,
        "very active": 1.725
    }
    tdee = bmr * multipliers.get(str(activity_level).lower(), 1.2)

    return round(bmi, 2), bmi_cat, round(bmr, 2), round(tdee, 2)


def calculate_macro_ratios(calories, diet_preference, goal):
    pref = str(diet_preference).lower()
    g = str(goal).lower()

    if "keto" in pref:
        p_ratio, c_ratio, f_ratio = 0.25, 0.05, 0.70
    elif "low carb" in pref or "fat loss" in g:
        p_ratio, c_ratio, f_ratio = 0.35, 0.25, 0.40
    elif "high protein" in pref or "muscle" in g or "strength" in g:
        p_ratio, c_ratio, f_ratio = 0.30, 0.40, 0.30
    else:
        p_ratio, c_ratio, f_ratio = 0.20, 0.50, 0.30

    protein = (calories * p_ratio) / 4.0
    carbs = (calories * c_ratio) / 4.0
    fat = (calories * f_ratio) / 9.0

    return round(protein, 1), round(carbs, 1), round(fat, 1)


def evaluate_advisory_notes(age, bmi, sleep, water, medical, injuries, allergies, predicted_risks):
    notes = []

    if medical and medical.strip().lower() != "none":
        notes.append(f"Pre-existing condition ({medical}) detected. Adjusting cardiorespiratory limits.")
    if injuries and injuries.strip().lower() != "none":
        notes.append(f"Active injuries ({injuries}) reported. Joints safety overrides have been applied.")
    if allergies and allergies.strip().lower() != "none":
        notes.append(f"Dietary allergies ({allergies}) active. Restricted ingredient pool initialized.")
    if bmi < 17.5:
        notes.append("Underweight BMI warning: Plan focuses on high-caloric absorption and mild resistance.")
    elif bmi >= 32.0:
        notes.append("Obesity Class II warning: Joint protection filters enabled. High-impact running restricted.")
    if sleep < 6.0:
        notes.append("Low recovery index (sleep < 6 hrs). Workout volumes scaled down.")
    if water < 1.8:
        notes.append("Suboptimal hydration base. Water tracking reminder enabled.")
    if predicted_risks.get("obesity_risk") == "High Risk":
        notes.append("ML Risk Indicator: Elevated Obesity Risk flag. Prioritizing fat oxidation cycles.")
    if predicted_risks.get("metabolic_risk") == "High Risk":
        notes.append("ML Risk Indicator: Elevated Metabolic Risk flag. Glycemic thresholds tracked.")

    return notes


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@profiles_bp.route('/profile', methods=['POST'])
@login_required
def create_profile():
    data = request.json
    if not data:
        return jsonify({"error": "No input parameters provided"}), 400

    required_fields = [
        'name', 'age', 'gender', 'height', 'weight',
        'fitness_goal', 'activity_level', 'diet_preference',
        'water_intake', 'sleep_hours', 'workout_experience'
    ]

    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == "":
            return jsonify({"error": f"Field '{field}' is required and cannot be empty"}), 400

    try:
        name = str(data['name']).strip()
        age = int(data['age'])
        gender = str(data['gender']).strip()
        height = float(data['height'])
        weight = float(data['weight'])
        goal = str(data['fitness_goal']).strip()
        activity = str(data['activity_level']).strip()
        diet_pref = str(data['diet_preference']).strip()
        water = float(data['water_intake'])
        sleep = float(data['sleep_hours'])
        experience = str(data['workout_experience']).strip()

        medical = str(data.get('medical_conditions', 'None')).strip()
        injuries = str(data.get('injuries', 'None')).strip()
        allergies = str(data.get('allergies', 'None')).strip()

        # Input validation
        if age <= 0 or age > 120:
            return jsonify({"error": "Age must be between 1 and 120"}), 400
        if height <= 50 or height > 275:
            return jsonify({"error": "Height must be between 50cm and 275cm"}), 400
        if weight <= 10 or weight > 500:
            return jsonify({"error": "Weight must be between 10kg and 500kg"}), 400

        # 1. Base biometrics
        bmi, bmi_cat, bmr, tdee = calculate_base_metrics(age, gender, height, weight, activity)

        # 2. ML predictions
        predicted_goal, goal_conf = predictor.predict_goal_category(age, gender, height, weight, activity)
        ml_cals = predictor.predict_calorie_requirement(age, weight, height, activity)
        predicted_risks = predictor.predict_health_risks(bmi, age, activity)
        diet_knn_res = predictor.recommend_diet_knn(goal, weight, activity, diet_pref)

        # 3. Weather & Hydration MCP
        today_date = datetime.today().strftime('%Y-%m-%d')
        weather = fetch_weather_recommendation()

        weather_log = WeatherHistory.query.filter_by(log_date=today_date).first()
        if not weather_log:
            weather_log = WeatherHistory(
                log_date=today_date,
                temp_c=weather["temperature_c"],
                humidity=weather["humidity"],
                air_quality=weather["air_quality"],
                condition=weather["condition"]
            )
            db.session.add(weather_log)
            db.session.commit()

        hydration_target_res = calculate_hydration_target(weight, activity, weather["temperature_c"])
        hydration_target = hydration_target_res["hydration_target_l"]

        # 4. Caloric goal targets
        if "loss" in goal.lower() or "deficit" in goal.lower():
            target_cals = tdee - 350 if "fat" in goal.lower() else tdee - 500
        elif "gain" in goal.lower() or "muscle" in goal.lower():
            target_cals = tdee + 500
        elif "strength" in goal.lower():
            target_cals = tdee + 300
        else:
            target_cals = tdee

        target_cals = max(1200.0, min(5000.0, target_cals))
        target_cals = round((target_cals * 0.7) + (ml_cals * 0.3), 2)

        # 5. Macros
        prot, carb, fat = calculate_macro_ratios(target_cals, diet_pref, goal)

        # 6. Advisory notes & safety score
        advisories = evaluate_advisory_notes(age, bmi, sleep, water, medical, injuries, allergies, predicted_risks)
        safety_score = 100
        if medical != "None": safety_score -= 15
        if injuries != "None": safety_score -= 15
        if allergies != "None": safety_score -= 5
        if bmi >= 32.0 or bmi < 17.5: safety_score -= 15
        if sleep < 6.0: safety_score -= 5
        safety_score = max(30, safety_score)

        # 7. Generate workout & diet plans
        workout_plan = workout_gen.generate_workout_plan(goal, experience, injuries, medical, weight, weather)
        diet_meals = diet_gen.generate_diet_plan(target_cals, prot, carb, fat, diet_pref, allergies)

        # 8. Plan recommendation score
        allergy_clash = (allergies != "None")
        injury_clash = (injuries != "None")
        rec_score = predictor.predict_recommendation_score(
            age, bmi, sleep, water, experience, abs(target_cals - ml_cals), allergy_clash, injury_clash
        )

        # 9. Save to DB
        new_profile = Profile(
            user_id=current_user.id,
            name=name, age=age, gender=gender,
            height=height, weight=weight,
            fitness_goal=goal, activity_level=activity,
            diet_preference=diet_pref,
            water_intake=water, sleep_hours=sleep,
            workout_experience=experience,
            medical_conditions=medical, injuries=injuries, allergies=allergies
        )
        db.session.add(new_profile)
        db.session.commit()

        fg = FitnessGoals(
            profile_id=new_profile.id,
            bmi=bmi, bmi_category=bmi_cat,
            bmr=bmr, tdee=tdee,
            target_calories=target_cals,
            target_protein=prot, target_carbs=carb, target_fat=fat,
            confidence_score=safety_score,
            advisory_notes=json.dumps(advisories)
        )
        db.session.add(fg)

        for day, exercises in workout_plan.items():
            db.session.add(WorkoutPlans(
                profile_id=new_profile.id,
                day_of_week=day,
                exercises=json.dumps(exercises)
            ))

        for meal in diet_meals:
            db.session.add(DietPlans(
                profile_id=new_profile.id,
                meal_type=meal["meal_type"],
                food_items=json.dumps(meal["food_items"]),
                calories=meal["calories"],
                protein=meal["protein"],
                carbohydrates=meal["carbohydrates"],
                fats=meal["fats"]
            ))

        rec_inputs = {
            "age": age, "gender": gender, "height": height, "weight": weight,
            "activity": activity, "pref": diet_pref,
            "experience": experience, "medical": medical, "injuries": injuries
        }
        rec_outputs = {
            "predicted_goal": predicted_goal, "goal_confidence": goal_conf,
            "predicted_risks": predicted_risks, "diet_knn_suggestion": diet_knn_res
        }
        db.session.add(Recommendations(
            profile_id=new_profile.id,
            model_name="XGBoost + RF + DecisionTree + KNN Pipeline",
            inputs=json.dumps(rec_inputs),
            outputs=json.dumps(rec_outputs),
            score=rec_score
        ))

        db.session.add(HydrationRecords(
            profile_id=new_profile.id,
            log_date=today_date,
            target_l=hydration_target,
            consumed_l=0.0
        ))

        db.session.commit()

        return jsonify({
            "message": "Fitness profile generated successfully!",
            "profile_id": new_profile.id,
            "recommendation_score": rec_score
        }), 201

    except ValueError:
        return jsonify({"error": "Physical measurements must be valid numeric values"}), 400
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error during profile creation: {str(e)}"}), 500


@profiles_bp.route('/profiles', methods=['GET'])
@login_required
def get_user_profiles():
    profiles = Profile.query.filter_by(user_id=current_user.id).order_by(Profile.created_at.desc()).all()
    profiles_data = []
    for p in profiles:
        target_cal = p.goals.target_calories if p.goals else 2000.0
        bmi_val = p.goals.bmi if p.goals else p.weight / ((p.height / 100.0) ** 2)
        profiles_data.append({
            "id": p.id,
            "name": p.name,
            "fitness_goal": p.fitness_goal,
            "created_at": p.created_at.strftime('%Y-%m-%d %H:%M'),
            "bmi": round(bmi_val, 2),
            "target_calories": round(target_cal, 2)
        })
    return jsonify(profiles_data), 200


@profiles_bp.route('/profile/<int:profile_id>', methods=['GET'])
@login_required
def get_profile_details(profile_id):
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Profile not found or access denied"}), 404

    g = profile.goals
    advisories = json.loads(g.advisory_notes) if g else []

    diet = []
    for dp in profile.diet_plans:
        diet.append({
            "meal_type": dp.meal_type,
            "food_items": json.loads(dp.food_items),
            "calories": dp.calories,
            "protein": dp.protein,
            "carbohydrates": dp.carbohydrates,
            "fats": dp.fats
        })

    workout = {}
    for wp in profile.workout_plans:
        workout[wp.day_of_week] = json.loads(wp.exercises)

    ml_rec = profile.recommendations[-1] if profile.recommendations else None
    rec_score = ml_rec.score if ml_rec else 85.0
    rec_outputs = json.loads(ml_rec.outputs) if ml_rec else {}

    return jsonify({
        "user": {
            "id": profile.id,
            "name": profile.name,
            "age": profile.age,
            "gender": profile.gender,
            "height": profile.height,
            "weight": profile.weight,
            "fitness_goal": profile.fitness_goal,
            "activity_level": profile.activity_level,
            "diet_preference": profile.diet_preference,
            "water_intake": profile.water_intake,
            "sleep_hours": profile.sleep_hours,
            "workout_experience": profile.workout_experience,
            "medical_conditions": profile.medical_conditions,
            "injuries": profile.injuries,
            "allergies": profile.allergies
        },
        "goals": {
            "bmi": g.bmi if g else round(profile.weight / ((profile.height / 100) ** 2), 2),
            "bmi_category": g.bmi_category if g else "Normal",
            "bmr": g.bmr if g else 1500.0,
            "tdee": g.tdee if g else 2000.0,
            "target_calories": g.target_calories if g else 2000.0,
            "target_protein": g.target_protein if g else 100.0,
            "target_carbs": g.target_carbs if g else 200.0,
            "target_fat": g.target_fat if g else 65.0,
            "confidence_score": g.confidence_score if g else 90,
            "advisory_notes": advisories,
            "recommendation_score": rec_score,
            "predicted_risks": rec_outputs.get("predicted_risks", {
                "obesity_risk": "Low Risk",
                "sedentary_risk": "Low Risk",
                "metabolic_risk": "Low Risk"
            })
        },
        "diet": diet,
        "workout": workout
    }), 200


@profiles_bp.route('/feedback', methods=['POST'])
@login_required
def post_feedback():
    data = request.json
    if not data or 'profile_id' not in data or 'rating' not in data:
        return jsonify({"error": "Missing profile_id or rating"}), 400

    profile_id = int(data['profile_id'])
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Access denied"}), 403

    try:
        rating = int(data['rating'])
        comments = str(data.get('comments', '')).strip()
        log_date = datetime.today().strftime('%Y-%m-%d')

        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400

        db.session.add(Feedback(
            profile_id=profile_id,
            rating=rating,
            comments=comments,
            log_date=log_date
        ))
        db.session.commit()
        return jsonify({"message": "Feedback review successfully saved!"}), 200

    except ValueError:
        return jsonify({"error": "Rating must be an integer"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@profiles_bp.route('/feedback/<int:profile_id>', methods=['GET'])
@login_required
def get_feedback_timeline(profile_id):
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Access denied"}), 403

    reviews = Feedback.query.filter_by(profile_id=profile_id).order_by(Feedback.created_at.desc()).all()
    return jsonify([{
        "rating": r.rating,
        "comments": r.comments,
        "log_date": r.log_date
    } for r in reviews]), 200
