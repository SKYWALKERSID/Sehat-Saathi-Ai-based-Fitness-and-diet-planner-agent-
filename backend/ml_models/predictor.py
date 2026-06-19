import os
import joblib
import numpy as np
import pandas as pd

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

# Cache of models
_models = {}

def get_model(name):
    """Loads and caches the model to avoid file I/O overhead on every request."""
    if name not in _models:
        path = os.path.join(MODELS_DIR, f"{name}.pkl")
        if os.path.exists(path):
            _models[name] = joblib.load(path)
        else:
            raise FileNotFoundError(f"Model file {name}.pkl not found! Please run the training pipeline first.")
    return _models[name]

def map_gender(gender_str):
    return 1 if str(gender_str).lower() == 'male' else 0

def map_activity(activity_str):
    mapping = {
        'sedentary': 0,
        'lightly active': 1,
        'moderately active': 2,
        'very active': 3
    }
    return mapping.get(str(activity_str).lower(), 1)

def map_goal(goal_str):
    # Mapping for synthetic goals:
    # 0: Weight Loss, 1: Muscle Gain, 2: Fat Loss, 3: Maintenance, 4: Strength Training
    g = str(goal_str).lower()
    if 'deficit' in g or 'weight loss' in g:
        return 0
    elif 'muscle' in g:
        return 1
    elif 'fat loss' in g:
        return 2
    elif 'strength' in g:
        return 4
    else: # maintenance / general fitness
        return 3

def map_diet_pref(pref_str):
    p = str(pref_str).lower()
    if 'vegan' in p:
        return 1
    elif 'vegetarian' in p:
        return 0
    else: # non-vegetarian / low-carb / keto / high-protein
        return 2

def map_experience(exp_str):
    e = str(exp_str).lower()
    if 'beginner' in e:
        return 0
    elif 'advanced' in e:
        return 2
    else:
        return 1

# 1. Goal Predictor
def predict_goal_category(age, gender_str, height, weight, activity_str):
    try:
        model = get_model('goal_predictor')
        gender = map_gender(gender_str)
        activity = map_activity(activity_str)
        bmi = weight / ((height / 100) ** 2)
        
        X = pd.DataFrame([{
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'bmi': bmi,
            'activity_level': activity
        }])
        
        pred_class = model.predict(X)[0]
        prob = model.predict_proba(X)[0][pred_class]
        
        goal_labels = {
            0: "Weight Loss",
            1: "Muscle Gain",
            2: "Fat Loss",
            3: "Maintenance",
            4: "Strength Training"
        }
        
        return goal_labels.get(pred_class, "Maintenance"), float(prob)
    except Exception as e:
        print(f"Goal Predictor Error: {e}. Falling back to default rules.")
        return "Maintenance", 1.0

# 2. Calorie Requirement Predictor
def predict_calorie_requirement(age, weight, height, activity_str):
    try:
        model = get_model('calorie_predictor')
        activity = map_activity(activity_str)
        
        X = pd.DataFrame([{
            'age': age,
            'weight': weight,
            'height': height,
            'activity_level': activity
        }])
        
        cals = model.predict(X)[0]
        return float(round(cals, 2))
    except Exception as e:
        print(f"Calorie Predictor Error: {e}. Falling back to manual formula.")
        # Mifflin-St Jeor formula fallback
        # Averages male/female BMR formula
        bmr = 10 * weight + 6.25 * height - 5 * age + 5 - 80
        multipliers = [1.2, 1.375, 1.55, 1.725]
        activity_val = map_activity(activity_str)
        tdee = bmr * multipliers[activity_val]
        return float(round(tdee, 2))

# 3. Diet KNN Recommender
def recommend_diet_knn(goal_str, weight, activity_str, pref_str):
    try:
        model = get_model('diet_knn')
        data = get_model('diet_knn_data')
        
        goal = map_goal(goal_str)
        activity = map_activity(activity_str)
        pref = map_diet_pref(pref_str)
        
        query = pd.DataFrame([{
            'goal': goal,
            'weight': weight,
            'activity_level': activity,
            'preference': pref
        }])
        
        distances, indices = model.kneighbors(query)
        similar_users = data.iloc[indices[0]]
        
        # Determine the most common diet preference and goal combo of similar users to suggest a plan type
        suggested_pref_val = similar_users['preference'].mode()[0]
        pref_labels = {0: "Vegetarian", 1: "Vegan", 2: "Non-Vegetarian"}
        suggested_pref = pref_labels.get(suggested_pref_val, pref_str)
        
        return {
            "suggested_preference": suggested_pref,
            "similar_weights": list(similar_users['weight'].values.astype(float))
        }
    except Exception as e:
        print(f"Diet KNN Error: {e}")
        return {
            "suggested_preference": pref_str,
            "similar_weights": [weight] * 5
        }

# 4. Progress Predictor
def predict_weight_progress(current_weight, calorie_delta, workout_frequency):
    try:
        models = get_model('progress_predictors')
        
        X = pd.DataFrame([{
            'weight': current_weight,
            'calorie_delta': calorie_delta,
            'workout_frequency': workout_frequency
        }])
        
        w_7d = models['7d'].predict(X)[0]
        w_30d = models['30d'].predict(X)[0]
        w_90d = models['90d'].predict(X)[0]
        
        return {
            "7_days": float(round(w_7d, 2)),
            "30_days": float(round(w_30d, 2)),
            "90_days": float(round(w_90d, 2))
        }
    except Exception as e:
        print(f"Progress Predictor Error: {e}")
        # Mathematical fallback
        w_7d = current_weight + (calorie_delta * 7 / 7700.0) - (workout_frequency * 0.05)
        w_30d = current_weight + (calorie_delta * 30 / 7700.0) - (workout_frequency * 0.20)
        w_90d = current_weight + (calorie_delta * 90 / 7700.0) - (workout_frequency * 0.50)
        return {
            "7_days": float(round(w_7d, 2)),
            "30_days": float(round(w_30d, 2)),
            "90_days": float(round(w_90d, 2))
        }

# 5. Advanced Scoring Model (XGBoost)
def predict_recommendation_score(age, bmi, sleep_hours, water_intake, experience_str, calorie_diff, allergy_clash, injury_clash):
    try:
        model = get_model('plan_scorer')
        exp = map_experience(experience_str)
        
        X = pd.DataFrame([{
            'age': age,
            'bmi': bmi,
            'sleep_hours': sleep_hours,
            'water_intake': water_intake,
            'experience_level': exp,
            'calorie_difference': calorie_diff,
            'allergy_clash': 1 if allergy_clash else 0,
            'injury_clash': 1 if injury_clash else 0
        }])
        
        score = model.predict(X)[0]
        return float(max(0.0, min(100.0, round(score, 1))))
    except Exception as e:
        print(f"Plan Scorer Error: {e}")
        # Rule fallback score calculation
        score = 100.0 - (calorie_diff * 0.05)
        if allergy_clash: score -= 40
        if injury_clash: score -= 30
        if sleep_hours < 6: score -= 10
        if water_intake < 2: score -= 5
        return float(max(0.0, min(100.0, round(score, 1))))

# 6. Health Risk Predictor (Decision Tree)
def predict_health_risks(bmi, age, activity_str):
    try:
        models = get_model('health_risk_predictors')
        activity = map_activity(activity_str)
        
        X = pd.DataFrame([{
            'bmi': bmi,
            'age': age,
            'activity_level': activity
        }])
        
        ob_risk = models['obesity'].predict(X)[0]
        sed_risk = models['sedentary'].predict(X)[0]
        met_risk = models['metabolic'].predict(X)[0]
        
        risk_labels = {0: "Low Risk", 1: "High Risk"}
        
        return {
            "obesity_risk": risk_labels.get(ob_risk, "Low Risk"),
            "sedentary_risk": risk_labels.get(sed_risk, "Low Risk"),
            "metabolic_risk": risk_labels.get(met_risk, "Low Risk")
        }
    except Exception as e:
        print(f"Health Risk Predictor Error: {e}")
        # Fallback rules
        ob_risk = "High Risk" if bmi >= 30 else "Low Risk"
        sed_risk = "High Risk" if activity_str.lower() == 'sedentary' else "Low Risk"
        met_risk = "High Risk" if (bmi >= 27 and age > 40) or (bmi >= 32) else "Low Risk"
        return {
            "obesity_risk": ob_risk,
            "sedentary_risk": sed_risk,
            "metabolic_risk": met_risk
        }
