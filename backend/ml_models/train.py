import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBRegressor

# Models output directory
MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

def train_goal_prediction_model():
    print("Training ML Model 1: Goal Prediction (Random Forest)...")
    np.random.seed(42)
    n_samples = 1500
    
    age = np.random.randint(18, 70, n_samples)
    gender = np.random.choice([0, 1], n_samples) # 0: Female, 1: Male
    height = np.random.randint(150, 200, n_samples)
    weight = np.random.randint(50, 130, n_samples)
    
    # Calculate BMI
    bmi = weight / ((height / 100) ** 2)
    
    # Activity level: 0: Sedentary, 1: Lightly Active, 2: Moderately Active, 3: Very Active
    activity = np.random.choice([0, 1, 2, 3], n_samples)
    
    # Synthetic rules to determine goal labels:
    # 0: Weight Loss, 1: Muscle Gain, 2: Fat Loss, 3: Maintenance, 4: Strength Training
    goals = []
    for i in range(n_samples):
        if bmi[i] >= 28:
            goals.append(np.random.choice([0, 2], p=[0.7, 0.3])) # Weight/Fat Loss
        elif bmi[i] < 20:
            goals.append(1) # Muscle Gain
        else:
            if activity[i] >= 2:
                goals.append(np.random.choice([1, 4], p=[0.6, 0.4])) # Muscle or Strength
            else:
                goals.append(np.random.choice([3, 0], p=[0.7, 0.3])) # Maintenance or Weight Loss
                
    X = pd.DataFrame({
        'age': age,
        'gender': gender,
        'height': height,
        'weight': weight,
        'bmi': bmi,
        'activity_level': activity
    })
    y = np.array(goals)
    
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    joblib.dump(model, os.path.join(MODELS_DIR, 'goal_predictor.pkl'))
    print("ML Model 1 saved.")

def train_calorie_requirement_model():
    print("Training ML Model 2: Calorie Requirement (Linear Regression)...")
    np.random.seed(42)
    n_samples = 2000
    
    age = np.random.randint(18, 75, n_samples)
    weight = np.random.randint(45, 125, n_samples)
    height = np.random.randint(145, 195, n_samples)
    # 0: Sedentary, 1: Lightly Active, 2: Moderately Active, 3: Very Active
    activity = np.random.choice([0, 1, 2, 3], n_samples)
    
    # Calculate Mifflin-St Jeor as base
    # Averages male/female BMR formula
    bmr = 10 * weight + 6.25 * height - 5 * age + 5 - 80
    multipliers = [1.2, 1.375, 1.55, 1.725]
    tdee = bmr * np.array([multipliers[a] for a in activity])
    
    # Add noise
    tdee_target = tdee + np.random.normal(0, 50, n_samples)
    
    X = pd.DataFrame({
        'age': age,
        'weight': weight,
        'height': height,
        'activity_level': activity
    })
    y = tdee_target
    
    model = LinearRegression()
    model.fit(X, y)
    
    joblib.dump(model, os.path.join(MODELS_DIR, 'calorie_predictor.pkl'))
    print("ML Model 2 saved.")

def train_diet_recommendation_system():
    print("Training ML Model 3: Diet Recommendation (KNN Recommender)...")
    np.random.seed(42)
    n_users = 1000
    
    # Features: Goal (0-4), Weight, Activity (0-3), Diet Preference (0: Veg, 1: Vegan, 2: Non-Veg)
    goal = np.random.choice([0, 1, 2, 3, 4], n_users)
    weight = np.random.randint(45, 125, n_users)
    activity = np.random.choice([0, 1, 2, 3], n_users)
    preference = np.random.choice([0, 1, 2], n_users) # 0: Vegetarian, 1: Vegan, 2: Non-Vegetarian
    
    X = pd.DataFrame({
        'goal': goal,
        'weight': weight,
        'activity_level': activity,
        'preference': preference
    })
    
    # Diet plan maps for mock DB of KNN:
    # We will save the training matrix itself along with a lookup dict of templates
    model = NearestNeighbors(n_neighbors=5, metric='euclidean')
    model.fit(X)
    
    joblib.dump(model, os.path.join(MODELS_DIR, 'diet_knn.pkl'))
    joblib.dump(X, os.path.join(MODELS_DIR, 'diet_knn_data.pkl'))
    print("ML Model 3 saved.")

def train_progress_prediction_model():
    print("Training ML Model 4: Progress Prediction (Linear Regression)...")
    np.random.seed(42)
    n_samples = 1500
    
    # Inputs: Current Weight (kg), Calorie Intake Deficit/Surplus (kcal/day relative to maintenance), Workout Frequency (days/week)
    weight = np.random.randint(50, 130, n_samples)
    # Deficit is negative, surplus is positive: -1000 to +1000
    cal_delta = np.random.randint(-1000, 1000, n_samples)
    workout_freq = np.random.randint(0, 7, n_samples)
    
    # 7-day weight change: (cal_delta * 7 / 7700) - (workout_freq * 0.05) + noise
    weight_7d = weight + (cal_delta * 7 / 7700) - (workout_freq * 0.05) + np.random.normal(0, 0.2, n_samples)
    weight_30d = weight + (cal_delta * 30 / 7700) - (workout_freq * 0.20) + np.random.normal(0, 0.5, n_samples)
    weight_90d = weight + (cal_delta * 90 / 7700) - (workout_freq * 0.50) + np.random.normal(0, 1.2, n_samples)
    
    X = pd.DataFrame({
        'weight': weight,
        'calorie_delta': cal_delta,
        'workout_frequency': workout_freq
    })
    
    model_7d = LinearRegression().fit(X, weight_7d)
    model_30d = LinearRegression().fit(X, weight_30d)
    model_90d = LinearRegression().fit(X, weight_90d)
    
    joblib.dump({
        '7d': model_7d,
        '30d': model_30d,
        '90d': model_90d
    }, os.path.join(MODELS_DIR, 'progress_predictors.pkl'))
    print("ML Model 4 saved.")

def train_advanced_scoring_model():
    print("Training ML Model 5: Plan Scoring (XGBoost)...")
    np.random.seed(42)
    n_samples = 2000
    
    # Inputs representing compatibility metrics:
    # age, bmi, compliance_score, allergy_clash (0/1), injury_clash (0/1), calorie_clash (kcal difference)
    age = np.random.randint(18, 70, n_samples)
    bmi = np.random.uniform(15, 40, n_samples)
    sleep = np.random.uniform(4, 10, n_samples)
    water = np.random.uniform(1, 5, n_samples)
    experience_level = np.random.choice([0, 1, 2], n_samples) # 0: Beg, 1: Int, 2: Adv
    calorie_diff = np.random.uniform(0, 600, n_samples) # diff between actual BMR target & meal plan cals
    allergy_match = np.random.choice([0, 1], n_samples, p=[0.9, 0.1])
    injury_match = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    
    # Output score: 100 - penalties
    scores = []
    for i in range(n_samples):
        score = 100.0
        score -= calorie_diff[i] * 0.05
        if allergy_match[i] == 1:
            score -= 40
        if injury_match[i] == 1:
            score -= 30
        if sleep[i] < 6:
            score -= 10
        if water[i] < 2:
            score -= 5
        score += experience_level[i] * 3
        # bounds
        score = max(0.0, min(100.0, score))
        scores.append(score)
        
    X = pd.DataFrame({
        'age': age,
        'bmi': bmi,
        'sleep_hours': sleep,
        'water_intake': water,
        'experience_level': experience_level,
        'calorie_difference': calorie_diff,
        'allergy_clash': allergy_match,
        'injury_clash': injury_match
    })
    y = np.array(scores)
    
    model = XGBRegressor(n_estimators=30, max_depth=4, learning_rate=0.1, random_state=42)
    model.fit(X, y)
    
    joblib.dump(model, os.path.join(MODELS_DIR, 'plan_scorer.pkl'))
    print("ML Model 5 saved.")

def train_health_risk_model():
    print("Training ML Model 6: Health Risk Prediction (Decision Tree)...")
    np.random.seed(42)
    n_samples = 1500
    
    bmi = np.random.uniform(15, 45, n_samples)
    age = np.random.randint(18, 80, n_samples)
    activity = np.random.choice([0, 1, 2, 3], n_samples) # 0: Sedentary, 1: Light, 2: Mod, 3: Active
    
    # Target 1: Obesity Risk (0: Low, 1: High)
    obesity_risk = [1 if b >= 30 else 0 for b in bmi]
    
    # Target 2: Sedentary Risk (0: Low, 1: High)
    sedentary_risk = [1 if a == 0 else 0 for a in activity]
    
    # Target 3: Metabolic Risk (0: Low, 1: High)
    metabolic_risk = []
    for i in range(n_samples):
        if bmi[i] >= 27 and age[i] > 40:
            metabolic_risk.append(1)
        elif bmi[i] >= 32:
            metabolic_risk.append(1)
        else:
            metabolic_risk.append(0)
            
    X = pd.DataFrame({
        'bmi': bmi,
        'age': age,
        'activity_level': activity
    })
    
    model_obesity = DecisionTreeClassifier(max_depth=3, random_state=42).fit(X, obesity_risk)
    model_sedentary = DecisionTreeClassifier(max_depth=3, random_state=42).fit(X, sedentary_risk)
    model_metabolic = DecisionTreeClassifier(max_depth=3, random_state=42).fit(X, metabolic_risk)
    
    joblib.dump({
        'obesity': model_obesity,
        'sedentary': model_sedentary,
        'metabolic': model_metabolic
    }, os.path.join(MODELS_DIR, 'health_risk_predictors.pkl'))
    print("ML Model 6 saved.")

def main():
    print("Starting ML Model training pipeline...")
    train_goal_prediction_model()
    train_calorie_requirement_model()
    train_diet_recommendation_system()
    train_progress_prediction_model()
    train_advanced_scoring_model()
    train_health_risk_model()
    print("All ML models successfully trained and serialized!")

if __name__ == '__main__':
    main()
