import json
import re

# Curated food item library with macronutrients per 100g (or standard serving)
FOOD_LIBRARY = [
    # Grains & Carbs
    {"name": "Rolled Oats", "category": "Carbs", "calories": 389, "protein": 16.9, "carbs": 66.3, "fat": 6.9, "tags": ["veg", "vegan", "low-fat"]},
    {"name": "Brown Rice", "category": "Carbs", "calories": 111, "protein": 2.6, "carbs": 23.0, "fat": 0.9, "tags": ["veg", "vegan", "low-fat"]},
    {"name": "Sweet Potato", "category": "Carbs", "calories": 86, "protein": 1.6, "carbs": 20.0, "fat": 0.1, "tags": ["veg", "vegan", "low-fat"]},
    {"name": "Quinoa", "category": "Carbs", "calories": 120, "protein": 4.4, "carbs": 21.3, "fat": 1.9, "tags": ["veg", "vegan", "high-protein"]},
    {"name": "Whole Wheat Bread", "category": "Carbs", "calories": 247, "protein": 13.0, "carbs": 41.0, "fat": 3.4, "tags": ["veg", "vegan"]},
    {"name": "Banana", "category": "Carbs", "calories": 89, "protein": 1.1, "carbs": 22.8, "fat": 0.3, "tags": ["veg", "vegan", "fruit"]},
    {"name": "Apple", "category": "Carbs", "calories": 52, "protein": 0.3, "carbs": 13.8, "fat": 0.2, "tags": ["veg", "vegan", "fruit"]},

    # Proteins
    {"name": "Chicken Breast (Grilled)", "category": "Protein", "calories": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6, "tags": ["non-veg", "keto", "low-carb", "high-protein"]},
    {"name": "Salmon (Grilled)", "category": "Protein", "calories": 206, "protein": 22.0, "carbs": 0.0, "fat": 13.0, "tags": ["non-veg", "keto", "low-carb", "high-protein"]},
    {"name": "Whole Eggs (Boiled)", "category": "Protein", "calories": 155, "protein": 13.0, "carbs": 1.1, "fat": 11.0, "tags": ["veg", "keto", "low-carb", "high-protein"]},
    {"name": "Egg Whites", "category": "Protein", "calories": 52, "protein": 11.0, "carbs": 0.7, "fat": 0.2, "tags": ["veg", "low-carb", "high-protein"]},
    {"name": "Tofu (Firm)", "category": "Protein", "calories": 144, "protein": 17.0, "carbs": 2.8, "fat": 8.0, "tags": ["veg", "vegan", "keto", "low-carb", "high-protein"]},
    {"name": "Tempeh", "category": "Protein", "calories": 193, "protein": 19.0, "carbs": 9.0, "fat": 11.0, "tags": ["veg", "vegan", "keto", "low-carb", "high-protein"]},
    {"name": "Lentils (Cooked)", "category": "Protein", "calories": 116, "protein": 9.0, "carbs": 20.0, "fat": 0.4, "tags": ["veg", "vegan", "high-protein"]},
    {"name": "Chickpeas (Boiled)", "category": "Protein", "calories": 164, "protein": 8.9, "carbs": 27.4, "fat": 2.6, "tags": ["veg", "vegan", "high-protein"]},
    {"name": "Greek Yogurt (Non-Fat)", "category": "Protein", "calories": 59, "protein": 10.0, "carbs": 3.6, "fat": 0.4, "tags": ["veg", "low-carb", "high-protein"]},
    {"name": "Cottage Cheese (Low-Fat)", "category": "Protein", "calories": 98, "protein": 11.0, "carbs": 3.4, "fat": 4.3, "tags": ["veg", "low-carb", "high-protein"]},
    {"name": "Whey Protein Isolate", "category": "Protein", "calories": 360, "protein": 90.0, "carbs": 3.0, "fat": 1.0, "tags": ["veg", "keto", "low-carb", "high-protein"]},
    {"name": "Vegan Protein Powder", "category": "Protein", "calories": 375, "protein": 80.0, "carbs": 5.0, "fat": 3.0, "tags": ["veg", "vegan", "keto", "low-carb", "high-protein"]},

    # Fats & Seeds
    {"name": "Almonds", "category": "Fats", "calories": 579, "protein": 21.0, "carbs": 22.0, "fat": 49.0, "tags": ["veg", "vegan", "keto", "low-carb"]},
    {"name": "Walnuts", "category": "Fats", "calories": 654, "protein": 15.0, "carbs": 14.0, "fat": 65.0, "tags": ["veg", "vegan", "keto", "low-carb"]},
    {"name": "Avocado", "category": "Fats", "calories": 160, "protein": 2.0, "carbs": 9.0, "fat": 15.0, "tags": ["veg", "vegan", "keto", "low-carb"]},
    {"name": "Peanut Butter", "category": "Fats", "calories": 588, "protein": 25.0, "carbs": 20.0, "fat": 50.0, "tags": ["veg", "vegan", "keto", "low-carb", "high-protein"]},
    {"name": "Olive Oil", "category": "Fats", "calories": 884, "protein": 0.0, "carbs": 0.0, "fat": 100.0, "tags": ["veg", "vegan", "keto", "low-carb"]},
    {"name": "Chia Seeds", "category": "Fats", "calories": 486, "protein": 17.0, "carbs": 42.0, "fat": 31.0, "tags": ["veg", "vegan", "keto", "low-carb"]},

    # Vegetables
    {"name": "Broccoli", "category": "Vegetable", "calories": 34, "protein": 2.8, "carbs": 6.6, "fat": 0.4, "tags": ["veg", "vegan", "keto", "low-carb"]},
    {"name": "Spinach", "category": "Vegetable", "calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "tags": ["veg", "vegan", "keto", "low-carb"]},
    {"name": "Mixed Salad Greens", "category": "Vegetable", "calories": 15, "protein": 1.4, "carbs": 2.9, "fat": 0.2, "tags": ["veg", "vegan", "keto", "low-carb"]},
    {"name": "Asparagus", "category": "Vegetable", "calories": 20, "protein": 2.2, "carbs": 3.9, "fat": 0.1, "tags": ["veg", "vegan", "keto", "low-carb"]}
]

# Workout items database with MET levels
EXERCISE_LIBRARY = {
    # Strength/Resistance exercises
    "Squats": {"category": "Strength", "met": 5.0, "description": "Barbell or Bodyweight Squat (Legs/Glutes)", "base_reps": "8-12", "base_sets": 4, "base_rest": "90s"},
    "Bench Press": {"category": "Strength", "met": 5.0, "description": "Barbell or Dumbbell Bench Press (Chest/Triceps)", "base_reps": "8-12", "base_sets": 4, "base_rest": "90s"},
    "Deadlift": {"category": "Strength", "met": 6.0, "description": "Barbell Conventional or Sumo Deadlift (Posterior Chain)", "base_reps": "5-8", "base_sets": 3, "base_rest": "120s"},
    "Overhead Press": {"category": "Strength", "met": 4.5, "description": "Barbell or Dumbbell Overhead Press (Shoulders)", "base_reps": "8-12", "base_sets": 4, "base_rest": "90s"},
    "Pull-ups": {"category": "Strength", "met": 5.0, "description": "Bodyweight or Assisted Pull-ups (Back/Biceps)", "base_reps": "6-12", "base_sets": 4, "base_rest": "90s"},
    "Dumbbell Rows": {"category": "Strength", "met": 4.0, "description": "Single-arm Dumbbell Rows (Lats/Upper Back)", "base_reps": "10-12", "base_sets": 3, "base_rest": "60s"},
    "Pushups": {"category": "Strength", "met": 4.0, "description": "Bodyweight Pushups (Chest/Triceps/Core)", "base_reps": "12-15", "base_sets": 3, "base_rest": "60s"},
    "Bicep Curls": {"category": "Strength", "met": 3.0, "description": "Dumbbell or Cable Bicep Curls (Arms)", "base_reps": "12-15", "base_sets": 3, "base_rest": "60s"},
    "Tricep Pushdowns": {"category": "Strength", "met": 3.0, "description": "Cable Rope Tricep Pushdowns (Arms)", "base_reps": "12-15", "base_sets": 3, "base_rest": "60s"},
    "Leg Press": {"category": "Strength", "met": 4.5, "description": "Machine Leg Press (Quads/Glutes)", "base_reps": "10-12", "base_sets": 3, "base_rest": "90s"},
    "Plank": {"category": "Strength", "met": 3.0, "description": "Bodyweight Plank hold for core stability", "base_reps": "45-60s hold", "base_sets": 3, "base_rest": "60s"},
    
    # Cardio/Endurance exercises
    "Running": {"category": "Cardio", "met": 8.0, "description": "Outdoor or Treadmill running at moderate pace", "base_reps": "20-30 mins", "base_sets": 1, "base_rest": "N/A"},
    "HIIT Circuit": {"category": "Cardio", "met": 8.5, "description": "Interval circuits of jumping jacks, mountain climbers, burpees", "base_reps": "20 mins (40s work / 20s rest)", "base_sets": 1, "base_rest": "N/A"},
    "Swimming": {"category": "Cardio", "met": 6.0, "description": "Laps in pool at steady effort (Knee/Spine Friendly)", "base_reps": "30 mins", "base_sets": 1, "base_rest": "N/A"},
    "Cycling": {"category": "Cardio", "met": 6.0, "description": "Stationary or Outdoor cycling (Knee/Back Friendly)", "base_reps": "25-35 mins", "base_sets": 1, "base_rest": "N/A"},
    "Rowing Machine": {"category": "Cardio", "met": 5.5, "description": "Rowing machine intervals (Low impact, full body)", "base_reps": "15-20 mins", "base_sets": 1, "base_rest": "N/A"},
    "Brisk Walking": {"category": "Cardio", "met": 3.5, "description": "Low-intensity walking (Joint Friendly, Heart Safe)", "base_reps": "30-45 mins", "base_sets": 1, "base_rest": "N/A"},
    
    # Mobility/Recovery
    "Yoga Flow": {"category": "Mobility", "met": 2.5, "description": "Vinyasa or Hatha Yoga flow for flexibility & recovery", "base_reps": "30 mins", "base_sets": 1, "base_rest": "N/A"},
    "Full Body Stretching": {"category": "Mobility", "met": 2.0, "description": "Static & dynamic stretching focused on major joints", "base_reps": "15-20 mins", "base_sets": 1, "base_rest": "N/A"},
    "Bird-Dog & Glute Bridge": {"category": "Mobility", "met": 2.5, "description": "Low back friendly activation exercises", "base_reps": "12-15 reps each", "base_sets": 3, "base_rest": "45s"}
}

def calculate_metrics(age, gender, height, weight, activity_level, goal):
    height_m = height / 100.0
    bmi = weight / (height_m ** 2)
    
    if bmi < 18.5:
        bmi_category = "Underweight"
    elif bmi < 25.0:
        bmi_category = "Normal"
    elif bmi < 30.0:
        bmi_category = "Overweight"
    else:
        bmi_category = "Obese"
        
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
    multipliers = {
        "sedentary": 1.2,
        "lightly active": 1.375,
        "moderately active": 1.55,
        "very active": 1.725
    }
    multiplier = multipliers.get(activity_level.lower(), 1.2)
    tdee = bmr * multiplier
    
    goal_key = goal.lower()
    if "loss" in goal_key or "deficit" in goal_key:
        if "fat" in goal_key:
            target_calories = tdee - 350
        else:
            target_calories = tdee - 500
    elif "gain" in goal_key or "muscle" in goal_key:
        target_calories = tdee + 500
    elif "strength" in goal_key:
        target_calories = tdee + 300
    else:
        target_calories = tdee
        
    target_calories = max(1200.0, min(5000.0, target_calories))
    
    return {
        "bmi": round(bmi, 2),
        "bmi_category": bmi_category,
        "bmr": round(bmr, 2),
        "tdee": round(tdee, 2),
        "target_calories": round(target_calories, 2)
    }

def calculate_macros(target_calories, diet_preference, goal):
    pref = diet_preference.lower()
    goal_key = goal.lower()
    
    if "keto" in pref:
        p_ratio, c_ratio, f_ratio = 0.25, 0.05, 0.70
    elif "low carb" in pref or "fat loss" in goal_key:
        p_ratio, c_ratio, f_ratio = 0.35, 0.25, 0.40
    elif "high protein" in pref or "muscle" in goal_key or "strength" in goal_key:
        p_ratio, c_ratio, f_ratio = 0.30, 0.40, 0.30
    else:
        p_ratio, c_ratio, f_ratio = 0.20, 0.50, 0.30
        
    protein_g = (target_calories * p_ratio) / 4.0
    carbs_g = (target_calories * c_ratio) / 4.0
    fat_g = (target_calories * f_ratio) / 9.0
    
    return {
        "protein_g": round(protein_g, 1),
        "carbs_g": round(carbs_g, 1),
        "fat_g": round(fat_g, 1)
    }

def calculate_confidence_score(user_data, metrics):
    score = 100
    reasons = []
    
    meds = user_data.get("medical_conditions", "")
    if meds and meds.strip() and meds.lower() != "none":
        score -= 15
        reasons.append("Pre-existing medical condition requires cautious workout scaling and low-intensity alternatives.")
        
    injuries = user_data.get("injuries", "")
    if injuries and injuries.strip() and injuries.lower() != "none":
        score -= 15
        reasons.append("Active or historical physical injury necessitates exercise modification to avoid strain.")
        
    allergies = user_data.get("allergies", "")
    if allergies and allergies.strip() and allergies.lower() != "none":
        score -= 5
        reasons.append("Dietary allergies restricted food ingredient pools to prevent allergen exposure.")
        
    bmi = metrics["bmi"]
    if bmi < 17.5:
        score -= 15
        reasons.append("Very low BMI detected: recommendation prioritizes caloric surplus and minimizes extreme cardio.")
    elif bmi >= 32.0:
        score -= 15
        reasons.append("High BMI (Class II+ Obesity) detected: recommendation switches to low impact joints protection exercises.")
        
    sleep = user_data.get("sleep_hours", 8)
    if sleep < 6:
        score -= 5
        reasons.append("Suboptimal sleep limits recovery rate. Plan targets moderate volume training.")
        
    water = user_data.get("water_intake", 2.0)
    if water < 1.5:
        score -= 5
        reasons.append("Low hydration levels flagged. Suggested plans encourage increased water tracking.")
        
    score = max(30, score)
    
    return {
        "score": score,
        "advisory_notes": reasons
    }

def filter_foods(preference, allergies):
    allergy_list = [a.strip().lower() for a in allergies.split(",")] if allergies else []
    
    filtered = []
    for food in FOOD_LIBRARY:
        has_allergen = False
        for allergen in allergy_list:
            if allergen and allergen in food["name"].lower():
                has_allergen = True
                break
        if has_allergen:
            continue
            
        pref = preference.lower()
        tags = food["tags"]
        
        if "vegan" in pref:
            if "vegan" in tags:
                filtered.append(food)
        elif "vegetarian" in pref:
            if "veg" in tags or "vegan" in tags:
                filtered.append(food)
        elif "keto" in pref:
            if "keto" in tags:
                filtered.append(food)
        elif "low carb" in pref:
            if "low-carb" in tags or "keto" in tags:
                filtered.append(food)
        else:
            filtered.append(food)
            
    if not filtered:
        filtered = [f for f in FOOD_LIBRARY if f["category"] != "Protein"]
        
    return filtered

def generate_diet_plan(target_calories, macros, preference, allergies):
    foods = filter_foods(preference, allergies)
    
    meal_splits = [
        {"type": "Breakfast", "pct": 0.30, "types": ["Carbs", "Protein", "Fats"]},
        {"type": "Lunch", "pct": 0.35, "types": ["Protein", "Carbs", "Vegetable"]},
        {"type": "Evening Snack", "pct": 0.12, "types": ["Fats", "Protein"]},
        {"type": "Dinner", "pct": 0.23, "types": ["Protein", "Vegetable", "Fats"]}
    ]
    
    diet_plan = []
    
    for split in meal_splits:
        meal_cal_target = target_calories * split["pct"]
        selected_foods = []
        for cat in split["types"]:
            cat_pool = [f for f in foods if f["category"] == cat or cat in f.get("tags", [])]
            if not cat_pool:
                cat_pool = [f for f in foods if f["category"] == "Protein"]
            if cat_pool:
                idx = len(diet_plan) % len(cat_pool)
                selected_foods.append(cat_pool[idx])
                
        total_base_cals = sum([f["calories"] for f in selected_foods])
        if total_base_cals == 0:
            total_base_cals = 100
            
        scaling_factor = meal_cal_target / total_base_cals
        
        food_details = []
        meal_cals = 0
        meal_protein = 0
        meal_carbs = 0
        meal_fat = 0
        
        for f in selected_foods:
            g = round(scaling_factor * 100)
            if g < 15: g = 15
            
            cal = (f["calories"] * g) / 100.0
            prot = (f["protein"] * g) / 100.0
            carb = (f["carbs"] * g) / 100.0
            fat = (f["fat"] * g) / 100.0
            
            food_details.append({
                "name": f["name"],
                "serving_g": g,
                "calories": round(cal, 1),
                "protein": round(prot, 1),
                "carbohydrates": round(carb, 1),
                "fats": round(fat, 1)
            })
            
            meal_cals += cal
            meal_protein += prot
            meal_carbs += carb
            meal_fat += fat
            
        diet_plan.append({
            "meal_type": split["type"],
            "food_items": food_details,
            "calories": round(meal_cals, 1),
            "protein": round(meal_protein, 1),
            "carbohydrates": round(meal_carbs, 1),
            "fats": round(meal_fat, 1)
        })
        
    return diet_plan

def generate_workout_plan(goal, experience, injuries, medical_conditions, weight_kg):
    inj_lower = injuries.lower() if injuries else ""
    med_lower = medical_conditions.lower() if medical_conditions else ""
    goal_key = goal.lower()
    
    schedule = {
        "Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [],
        "Friday": [], "Saturday": [], "Sunday": []
    }
    
    if "loss" in goal_key or "fat" in goal_key:
        w_monday = ["Squats", "Pushups", "Dumbbell Rows", "Plank"]
        w_tuesday = ["HIIT Circuit"]
        w_wednesday = ["Leg Press", "Bench Press", "Pull-ups", "Plank"]
        w_thursday = ["Yoga Flow", "Full Body Stretching"]
        w_friday = ["Running", "Pushups", "Dumbbell Rows"]
        w_saturday = ["HIIT Circuit"]
        w_sunday = ["Rest & Recovery"]
    elif "muscle" in goal_key or "gain" in goal_key:
        w_monday = ["Bench Press", "Overhead Press", "Tricep Pushdowns"]
        w_tuesday = ["Pull-ups", "Dumbbell Rows", "Bicep Curls"]
        w_wednesday = ["Squats", "Leg Press", "Plank"]
        w_thursday = ["Rest & Recovery"]
        w_friday = ["Bench Press", "Dumbbell Rows", "Bicep Curls", "Tricep Pushdowns"]
        w_saturday = ["Squats", "Plank", "Full Body Stretching"]
        w_sunday = ["Rest & Recovery"]
    elif "strength" in goal_key:
        w_monday = ["Squats", "Bench Press", "Plank"]
        w_tuesday = ["Brisk Walking", "Full Body Stretching"]
        w_wednesday = ["Deadlift", "Overhead Press", "Pull-ups"]
        w_thursday = ["Rest & Recovery"]
        w_friday = ["Squats", "Bench Press", "Dumbbell Rows"]
        w_saturday = ["Cycling", "Plank"]
        w_sunday = ["Rest & Recovery"]
    else:
        w_monday = ["Squats", "Pushups", "Plank"]
        w_tuesday = ["Cycling"]
        w_wednesday = ["Dumbbell Rows", "Bench Press", "Bird-Dog & Glute Bridge"]
        w_thursday = ["Yoga Flow"]
        w_friday = ["Brisk Walking", "Pushups", "Plank"]
        w_saturday = ["Swimming"]
        w_sunday = ["Rest & Recovery"]

    raw_schedule = {
        "Monday": w_monday, "Tuesday": w_tuesday, "Wednesday": w_wednesday,
        "Thursday": w_thursday, "Friday": w_friday, "Saturday": w_saturday,
        "Sunday": w_sunday
    }
    
    knee_friendly_sub = {
        "Squats": "Bird-Dog & Glute Bridge",
        "Leg Press": "Bird-Dog & Glute Bridge",
        "Running": "Swimming",
        "HIIT Circuit": "Rowing Machine"
    }
    back_friendly_sub = {
        "Deadlift": "Dumbbell Rows",
        "Squats": "Leg Press",
        "HIIT Circuit": "Cycling"
    }
    shoulder_friendly_sub = {
        "Overhead Press": "Plank",
        "Bench Press": "Bird-Dog & Glute Bridge",
        "Pushups": "Plank",
        "Pull-ups": "Dumbbell Rows"
    }
    
    for day, exercises in raw_schedule.items():
        day_exercises = []
        for ex_name in exercises:
            if ex_name == "Rest & Recovery":
                day_exercises.append({
                    "name": "Rest & Recovery",
                    "sets": 0,
                    "reps": "N/A",
                    "rest_time": "N/A",
                    "calories_burned": 0,
                    "description": "Rest day to allow muscle fibers to heal and rebuild.",
                    "caution": ""
                })
                continue
                
            actual_ex = ex_name
            caution_msg = ""
            
            if "knee" in inj_lower or "joint" in inj_lower:
                if actual_ex in knee_friendly_sub:
                    actual_ex = knee_friendly_sub[actual_ex]
                    caution_msg = "Replaced due to user knee injury concerns."
            if "back" in inj_lower or "spine" in inj_lower or "spinal" in inj_lower:
                if actual_ex in back_friendly_sub:
                    actual_ex = back_friendly_sub[actual_ex]
                    caution_msg = "Replaced to minimize spinal compression."
            if "shoulder" in inj_lower or "rotator" in inj_lower:
                if actual_ex in shoulder_friendly_sub:
                    actual_ex = shoulder_friendly_sub[actual_ex]
                    caution_msg = "Replaced to prevent shoulder impingement."
                    
            if ("heart" in med_lower or "cardio" in med_lower or "asthma" in med_lower) and actual_ex == "HIIT Circuit":
                actual_ex = "Brisk Walking"
                caution_msg = "Swapped HIIT for safe brisk walking."
                
            ex_details = EXERCISE_LIBRARY[actual_ex]
            
            sets = ex_details["base_sets"]
            reps = ex_details["base_reps"]
            rest = ex_details["base_rest"]
            
            exp = experience.lower()
            if exp == "beginner":
                if isinstance(sets, int) and sets > 1:
                    sets = max(2, sets - 1)
                if "-" in reps:
                    parts = reps.split("-")
                    try:
                        first_num = int(parts[0].strip())
                        reps = f"{max(6, first_num-2)}-{first_num}"
                    except ValueError:
                        pass
                rest = "90s" if rest == "60s" else rest
            elif exp == "advanced":
                if isinstance(sets, int) and sets > 0:
                    sets = sets + 1
                if "-" in reps:
                    parts = reps.split("-")
                    try:
                        first_num_match = re.match(r'^\s*(\d+)', parts[0])
                        second_num_match = re.match(r'^\s*(\d+)', parts[1])
                        if first_num_match and second_num_match:
                            val1 = int(first_num_match.group(1))
                            val2 = int(second_num_match.group(1))
                            suffix = parts[1].replace(str(val2), "").strip()
                            reps = f"{val2}-{val2+3} {suffix}".strip()
                        else:
                            reps = f"{parts[1].strip()}-{int(parts[1].strip())+3}"
                    except Exception:
                        pass
                rest = "60s" if rest == "90s" else rest
                
            if ex_details["category"] == "Cardio":
                duration_hours = 0.5
            elif ex_details["category"] == "Mobility":
                duration_hours = 0.33
            else:
                duration_hours = (sets * 2.5) / 60.0
                
            cals = round(ex_details["met"] * weight_kg * duration_hours)
            
            day_exercises.append({
                "name": actual_ex,
                "sets": sets,
                "reps": reps,
                "rest_time": rest,
                "calories_burned": cals,
                "description": ex_details["description"],
                "caution": caution_msg
            })
            
        schedule[day] = day_exercises
        
    return schedule

def generate_full_profile(user_input):
    age = int(user_input["age"])
    gender = user_input["gender"]
    height = float(user_input["height"])
    weight = float(user_input["weight"])
    activity_level = user_input["activity_level"]
    goal = user_input["fitness_goal"]
    diet_preference = user_input["diet_preference"]
    allergies = user_input.get("allergies", "")
    injuries = user_input.get("injuries", "")
    medical_conditions = user_input.get("medical_conditions", "")
    experience = user_input["workout_experience"]
    
    metrics = calculate_metrics(age, gender, height, weight, activity_level, goal)
    macros = calculate_macros(metrics["target_calories"], diet_preference, goal)
    
    fitness_goals = {
        "bmi": metrics["bmi"],
        "bmi_category": metrics["bmi_category"],
        "bmr": metrics["bmr"],
        "tdee": metrics["tdee"],
        "target_calories": metrics["target_calories"],
        "target_protein": macros["protein_g"],
        "target_carbs": macros["carbs_g"],
        "target_fat": macros["fat_g"],
    }
    
    confidence = calculate_confidence_score(user_input, metrics)
    fitness_goals["confidence_score"] = confidence["score"]
    fitness_goals["advisory_notes"] = confidence["advisory_notes"]
    
    diet_meals = generate_diet_plan(metrics["target_calories"], macros, diet_preference, allergies)
    workout_schedule = generate_workout_plan(goal, experience, injuries, medical_conditions, weight)
    
    return fitness_goals, diet_meals, workout_schedule
