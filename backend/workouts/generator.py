import re
from backend.mcp.exercise import lookup_exercise, get_all_exercises

# Joint safety substitutions
KNEE_SUBSTITUTIONS = {
    "squats": "bird-dog & glute bridge",
    "leg press": "bird-dog & glute bridge",
    "running": "swimming",
    "hiit circuit": "rowing machine"
}

BACK_SUBSTITUTIONS = {
    "deadlift": "dumbbell rows",
    "squats": "leg press",
    "hiit circuit": "cycling"
}

SHOULDER_SUBSTITUTIONS = {
    "overhead press": "plank",
    "bench press": "bird-dog & glute bridge",
    "pushups": "plank",
    "pull-ups": "dumbbell rows"
}

def generate_workout_plan(goal: str, experience: str, injuries: str, medical_conditions: str, weight_kg: float, weather_data: dict = None) -> dict:
    """
    Generates a personalized, injury-safe 7-day workout plan adjusted for weather conditions.
    """
    inj_lower = str(injuries).lower() if injuries else "none"
    med_lower = str(medical_conditions).lower() if medical_conditions else "none"
    goal_lower = str(goal).lower()
    
    # Base 7-day schedule skeletons by fitness goal
    schedule_days = {
        "Monday": [], "Tuesday": [], "Wednesday": [], 
        "Thursday": [], "Friday": [], "Saturday": [], "Sunday": []
    }
    
    if "loss" in goal_lower or "fat" in goal_lower:
        schedule_raw = {
            "Monday": ["Squats", "Pushups", "Dumbbell Rows", "Plank"],
            "Tuesday": ["HIIT Circuit"],
            "Wednesday": ["Leg Press", "Bench Press", "Pull-ups", "Plank"],
            "Thursday": ["Yoga Flow", "Full Body Stretching"],
            "Friday": ["Running", "Pushups", "Dumbbell Rows"],
            "Saturday": ["HIIT Circuit"],
            "Sunday": ["Rest & Recovery"]
        }
    elif "muscle" in goal_lower or "gain" in goal_lower:
        schedule_raw = {
            "Monday": ["Bench Press", "Overhead Press", "Tricep Pushdowns"],
            "Tuesday": ["Pull-ups", "Dumbbell Rows", "Bicep Curls"],
            "Wednesday": ["Squats", "Leg Press", "Plank"],
            "Thursday": ["Rest & Recovery"],
            "Friday": ["Bench Press", "Dumbbell Rows", "Bicep Curls", "Tricep Pushdowns"],
            "Saturday": ["Squats", "Plank", "Full Body Stretching"],
            "Sunday": ["Rest & Recovery"]
        }
    elif "strength" in goal_lower:
        schedule_raw = {
            "Monday": ["Squats", "Bench Press", "Plank"],
            "Tuesday": ["Brisk Walking", "Full Body Stretching"],
            "Wednesday": ["Deadlift", "Overhead Press", "Pull-ups"],
            "Thursday": ["Rest & Recovery"],
            "Friday": ["Squats", "Bench Press", "Dumbbell Rows"],
            "Saturday": ["Cycling", "Plank"],
            "Sunday": ["Rest & Recovery"]
        }
    else: # General Fitness / Maintenance
        schedule_raw = {
            "Monday": ["Squats", "Pushups", "Plank"],
            "Tuesday": ["Cycling"],
            "Wednesday": ["Dumbbell Rows", "Bench Press", "Bird-Dog & Glute Bridge"],
            "Thursday": ["Yoga Flow"],
            "Friday": ["Brisk Walking", "Pushups", "Plank"],
            "Saturday": ["Swimming"],
            "Sunday": ["Rest & Recovery"]
        }
        
    # Weather modifiers
    override_indoor = False
    warmup_note = ""
    if weather_data:
        if weather_data.get("override_workout_type") == "indoor":
            override_indoor = True
        if weather_data.get("warmup_extension_mins", 0) > 0:
            warmup_note = f"Extend warm-up by {weather_data['warmup_extension_mins']} minutes due to cold outdoor temperature ({weather_data['temperature_c']}C)."

    final_schedule = {}
    
    for day, exercise_names in schedule_raw.items():
        day_workouts = []
        for name in exercise_names:
            if name == "Rest & Recovery":
                day_workouts.append({
                    "name": "Rest & Recovery",
                    "sets": 0,
                    "reps": "N/A",
                    "rest_time": "N/A",
                    "calories_burned": 0,
                    "description": "Rest day to allow muscle fibers to heal and rebuild.",
                    "caution": ""
                })
                continue
                
            actual_ex = name
            caution_msg = ""
            
            # Weather Override: Swap outdoor running/cycling/HIIT if extreme heat
            if override_indoor:
                if actual_ex.lower() == "running":
                    actual_ex = "Swimming"
                    caution_msg = "Outdoor running changed to indoor swimming due to extreme hot weather."
                elif actual_ex.lower() == "hiit circuit":
                    actual_ex = "Rowing Machine"
                    caution_msg = "HIIT Circuit swapped for rowing intervals in air-conditioned gym."
                    
            # Joint-friendly overrides
            if "knee" in inj_lower or "joint" in inj_lower:
                ex_key = actual_ex.lower()
                if ex_key in KNEE_SUBSTITUTIONS:
                    actual_ex = KNEE_SUBSTITUTIONS[ex_key].title()
                    caution_msg = f"Substituted {name} due to knee injury parameters."
            if "back" in inj_lower or "spine" in inj_lower or "spinal" in inj_lower:
                ex_key = actual_ex.lower()
                if ex_key in BACK_SUBSTITUTIONS:
                    actual_ex = BACK_SUBSTITUTIONS[ex_key].title()
                    caution_msg = f"Substituted {name} to safeguard lumbar column."
            if "shoulder" in inj_lower or "rotator" in inj_lower:
                ex_key = actual_ex.lower()
                if ex_key in SHOULDER_SUBSTITUTIONS:
                    actual_ex = SHOULDER_SUBSTITUTIONS[ex_key].title()
                    caution_msg = f"Substituted {name} to avoid shoulder strain."
                    
            # Cardiovascular/Asthma safety
            if ("heart" in med_lower or "cardio" in med_lower or "asthma" in med_lower) and actual_ex.lower() == "hiit circuit":
                actual_ex = "Brisk Walking"
                caution_msg = "HIIT swapped for steady-state Brisk Walking for cardiorespiratory safety."

            # Query exercise metrics using Exercise MCP
            lookup = lookup_exercise(actual_ex)
            ex_details = lookup["details"]
            
            sets = ex_details["base_sets"]
            reps = ex_details["base_reps"]
            rest = ex_details["base_rest"]
            
            # Scale sets and reps by experience
            exp = experience.lower()
            if exp == "beginner":
                if isinstance(sets, int) and sets > 2:
                    sets = sets - 1
                if "-" in reps:
                    parts = reps.split("-")
                    try:
                        val1 = int(parts[0].strip())
                        reps = f"{max(5, val1-2)}-{val1}"
                    except ValueError:
                        pass
                rest = "90s" if rest == "60s" else rest
            elif exp == "advanced":
                if isinstance(sets, int):
                    sets = sets + 1
                if "-" in reps:
                    parts = reps.split("-")
                    try:
                        val1 = int(reps.split("-")[0])
                        val2_match = re.match(r'^\s*(\d+)', parts[1])
                        if val2_match:
                            val2 = int(val2_match.group(1))
                            suffix = parts[1].replace(str(val2), "").strip()
                            reps = f"{val2}-{val2+3} {suffix}".strip()
                    except Exception:
                        pass
                rest = "60s" if rest == "90s" else rest
                
            # Calorie burns calculations
            if ex_details["category"] == "Cardio":
                duration_hours = 0.5 # 30 mins average
            elif ex_details["category"] == "Mobility":
                duration_hours = 0.33 # 20 mins average
            else:
                duration_hours = (sets * 2.5) / 60.0 # ~2.5 mins per set including rest
                
            cals = round(ex_details["met"] * weight_kg * duration_hours)
            
            day_workouts.append({
                "name": actual_ex,
                "sets": sets,
                "reps": reps,
                "rest_time": rest,
                "calories_burned": int(cals),
                "description": ex_details["description"],
                "caution": caution_msg + (" " + warmup_note if warmup_note else "")
            })
            
        final_schedule[day] = day_workouts
        
    return final_schedule
