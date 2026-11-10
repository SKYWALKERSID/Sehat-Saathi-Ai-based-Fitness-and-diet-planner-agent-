"""
Unified Recommendation Facade for Sehat Saathi.
Delegates health calculations, diet generation, and workout generation to the
ML + MCP backend modules (`backend.ml_models.predictor`, `backend.profiles.routes`,
`backend.diets.generator`, and `backend.workouts.generator`) while maintaining
backwards-compatible function signatures.
"""
from backend.ml_models import predictor
from backend.profiles.routes import (
    calculate_base_metrics,
    calculate_macro_ratios,
    evaluate_advisory_notes,
)
from backend.diets.generator import generate_diet_plan as _mcp_generate_diet_plan
from backend.workouts.generator import generate_workout_plan as _mcp_generate_workout_plan
from backend.mcp.weather import fetch_weather_recommendation


def calculate_health_metrics(
    weight,
    height,
    age,
    gender,
    activity_level,
    goal,
    medical_conditions="None",
    injuries="None",
    allergies="None",
    diet_preference="Vegetarian",
    sleep_hours=7.5,
    water_intake=2.5,
    workout_experience="Beginner",
):
    bmi, bmi_cat, bmr, tdee = calculate_base_metrics(age, gender, height, weight, activity_level)
    ml_cals = predictor.predict_calorie_requirement(age, weight, height, activity_level)
    base_cals = (tdee + ml_cals) / 2.0

    g_low = str(goal).lower()
    if "weight loss" in g_low or "fat loss" in g_low:
        target_calories = max(1200.0, base_cals - 500.0)
    elif "weight gain" in g_low or "muscle" in g_low or "strength" in g_low:
        target_calories = base_cals + 350.0
    else:
        target_calories = base_cals

    target_calories = round(target_calories, 1)
    p_g, c_g, f_g = calculate_macro_ratios(target_calories, diet_preference, goal)
    risks = predictor.predict_health_risks(bmi, age, activity_level)
    pred_goal, goal_conf = predictor.predict_goal_category(age, gender, height, weight, activity_level)
    diet_knn = predictor.recommend_diet_knn(goal, weight, activity_level, diet_preference)
    weather_ctx = fetch_weather_recommendation()
    from backend.mcp.hydration import calculate_hydration_target
    hydration_res = calculate_hydration_target(weight, activity_level, weather_ctx["temperature_c"])

    advisory_notes = evaluate_advisory_notes(
        age, bmi, sleep_hours, water_intake, medical_conditions, injuries, allergies, risks
    )
    score = predictor.predict_recommendation_score(
        age, bmi, sleep_hours, water_intake, workout_experience, 5.0, False, False
    )

    return {
        "bmi": bmi,
        "bmi_category": bmi_cat,
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target_calories,
        "target_protein": p_g,
        "target_carbs": c_g,
        "target_fat": f_g,
        "confidence_score": round(score, 1),
        "advisory_notes": advisory_notes,
        "predicted_risks": risks,
        "predicted_goal": pred_goal,
        "goal_confidence": round(goal_conf, 3),
        "diet_knn_suggestion": diet_knn,
        "weather_context": weather_ctx,
        "hydration_target_l": hydration_res["hydration_target_l"],
    }


def generate_diet_plan(target_calories, diet_preference, allergies="None", medical_conditions="None"):
    p_g, c_g, f_g = calculate_macro_ratios(target_calories, diet_preference, "General Fitness")
    return _mcp_generate_diet_plan(
        target_calories=target_calories,
        target_protein=p_g,
        target_carbs=c_g,
        target_fat=f_g,
        preference=diet_preference,
        allergies=allergies,
    )


def generate_workout_plan(goal, experience, injuries="None", medical_conditions="None", weight_kg=70.0):
    weather_data = fetch_weather_recommendation()
    return _mcp_generate_workout_plan(
        goal=goal,
        experience=experience,
        injuries=injuries,
        medical_conditions=medical_conditions,
        weight_kg=weight_kg,
        weather_data=weather_data,
    )


def generate_full_profile(profile):
    goals = calculate_health_metrics(
        weight=profile["weight"],
        height=profile["height"],
        age=profile["age"],
        gender=profile["gender"],
        activity_level=profile["activity_level"],
        goal=profile["fitness_goal"],
        medical_conditions=profile.get("medical_conditions", "None"),
        injuries=profile.get("injuries", "None"),
        allergies=profile.get("allergies", "None"),
        diet_preference=profile.get("diet_preference", "Vegetarian"),
        sleep_hours=profile.get("sleep_hours", 7.5),
        water_intake=profile.get("water_intake", 2.5),
        workout_experience=profile.get("workout_experience", "Beginner"),
    )
    diet = _mcp_generate_diet_plan(
        target_calories=goals["target_calories"],
        target_protein=goals["target_protein"],
        target_carbs=goals["target_carbs"],
        target_fat=goals["target_fat"],
        preference=profile["diet_preference"],
        allergies=profile.get("allergies", "None"),
    )
    weather_data = fetch_weather_recommendation()
    workouts = _mcp_generate_workout_plan(
        goal=profile["fitness_goal"],
        experience=profile["workout_experience"],
        injuries=profile.get("injuries", "None"),
        medical_conditions=profile.get("medical_conditions", "None"),
        weight_kg=profile["weight"],
        weather_data=weather_data,
    )
    return goals, diet, workouts
