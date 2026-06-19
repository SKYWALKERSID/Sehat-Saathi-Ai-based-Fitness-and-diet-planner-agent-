import json

EXERCISE_DATABASE = {
    "squats": {
        "category": "Strength",
        "met": 5.0,
        "muscle_group": "Quads, Glutes, Hamstrings",
        "equipment": "Barbell or Bodyweight",
        "difficulty": "Intermediate",
        "base_sets": 4,
        "base_reps": "8-12",
        "base_rest": "90s",
        "description": "Barbell or Bodyweight Squat (Legs/Glutes)"
    },
    "bench press": {
        "category": "Strength",
        "met": 5.0,
        "muscle_group": "Chest, Shoulders, Triceps",
        "equipment": "Barbell or Dumbbells",
        "difficulty": "Intermediate",
        "base_sets": 4,
        "base_reps": "8-12",
        "base_rest": "90s",
        "description": "Barbell or Dumbbell Bench Press (Chest/Triceps)"
    },
    "deadlift": {
        "category": "Strength",
        "met": 6.0,
        "muscle_group": "Hamstrings, Glutes, Lower Back, Traps",
        "equipment": "Barbell",
        "difficulty": "Advanced",
        "base_sets": 3,
        "base_reps": "5-8",
        "base_rest": "120s",
        "description": "Barbell Conventional or Sumo Deadlift (Posterior Chain)"
    },
    "overhead press": {
        "category": "Strength",
        "met": 4.5,
        "muscle_group": "Shoulders, Triceps, Core",
        "equipment": "Barbell or Dumbbells",
        "difficulty": "Intermediate",
        "base_sets": 4,
        "base_reps": "8-12",
        "base_rest": "90s",
        "description": "Barbell or Dumbbell Overhead Press (Shoulders)"
    },
    "pull-ups": {
        "category": "Strength",
        "met": 5.0,
        "muscle_group": "Lats, Upper Back, Biceps",
        "equipment": "Pull-up Bar",
        "difficulty": "Intermediate",
        "base_sets": 4,
        "base_reps": "6-12",
        "base_rest": "90s",
        "description": "Bodyweight or Assisted Pull-ups (Back/Biceps)"
    },
    "dumbbell rows": {
        "category": "Strength",
        "met": 4.0,
        "muscle_group": "Lats, Rhomboids, Biceps",
        "equipment": "Dumbbells",
        "difficulty": "Beginner",
        "base_sets": 3,
        "base_reps": "10-12",
        "base_rest": "60s",
        "description": "Single-arm Dumbbell Rows (Lats/Upper Back)"
    },
    "pushups": {
        "category": "Strength",
        "met": 4.0,
        "muscle_group": "Chest, Shoulders, Triceps, Core",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "base_sets": 3,
        "base_reps": "12-15",
        "base_rest": "60s",
        "description": "Bodyweight Pushups (Chest/Triceps/Core)"
    },
    "bicep curls": {
        "category": "Strength",
        "met": 3.0,
        "muscle_group": "Biceps, Forearms",
        "equipment": "Dumbbells or Cable",
        "difficulty": "Beginner",
        "base_sets": 3,
        "base_reps": "12-15",
        "base_rest": "60s",
        "description": "Dumbbell or Cable Bicep Curls (Arms)"
    },
    "tricep pushdowns": {
        "category": "Strength",
        "met": 3.0,
        "muscle_group": "Triceps",
        "equipment": "Cable Machine",
        "difficulty": "Beginner",
        "base_sets": 3,
        "base_reps": "12-15",
        "base_rest": "60s",
        "description": "Cable Rope Tricep Pushdowns (Arms)"
    },
    "leg press": {
        "category": "Strength",
        "met": 4.5,
        "muscle_group": "Quads, Glutes, Hamstrings",
        "equipment": "Leg Press Machine",
        "difficulty": "Beginner",
        "base_sets": 3,
        "base_reps": "10-12",
        "base_rest": "90s",
        "description": "Machine Leg Press (Quads/Glutes)"
    },
    "plank": {
        "category": "Strength",
        "met": 3.0,
        "muscle_group": "Transverse Abdominis, Rectus Abdominis, Obliques",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "base_sets": 3,
        "base_reps": "45-60s hold",
        "base_rest": "60s",
        "description": "Bodyweight Plank hold for core stability"
    },
    "running": {
        "category": "Cardio",
        "met": 8.0,
        "muscle_group": "Cardiovascular System, Legs",
        "equipment": "Treadmill or Outdoor path",
        "difficulty": "Beginner",
        "base_sets": 1,
        "base_reps": "20-30 mins",
        "base_rest": "N/A",
        "description": "Outdoor or Treadmill running at moderate pace"
    },
    "hiit circuit": {
        "category": "Cardio",
        "met": 8.5,
        "muscle_group": "Full Body, Cardiovascular System",
        "equipment": "Bodyweight",
        "difficulty": "Advanced",
        "base_sets": 1,
        "base_reps": "20 mins (40s work / 20s rest)",
        "base_rest": "N/A",
        "description": "Interval circuits of jumping jacks, mountain climbers, burpees"
    },
    "swimming": {
        "category": "Cardio",
        "met": 6.0,
        "muscle_group": "Full Body, Cardiovascular System",
        "equipment": "Pool",
        "difficulty": "Beginner",
        "base_sets": 1,
        "base_reps": "30 mins",
        "base_rest": "N/A",
        "description": "Laps in pool at steady effort (Knee/Spine Friendly)"
    },
    "cycling": {
        "category": "Cardio",
        "met": 6.0,
        "muscle_group": "Quads, Glutes, Cardio System",
        "equipment": "Stationary or Road Bike",
        "difficulty": "Beginner",
        "base_sets": 1,
        "base_reps": "25-35 mins",
        "base_rest": "N/A",
        "description": "Stationary or Outdoor cycling (Knee/Back Friendly)"
    },
    "rowing machine": {
        "category": "Cardio",
        "met": 5.5,
        "muscle_group": "Lats, Upper Back, Quads, Hamstrings, Cardio",
        "equipment": "Rowing Machine",
        "difficulty": "Intermediate",
        "base_sets": 1,
        "base_reps": "15-20 mins",
        "base_rest": "N/A",
        "description": "Rowing machine intervals (Low impact, full body)"
    },
    "brisk walking": {
        "category": "Cardio",
        "met": 3.5,
        "muscle_group": "Legs, Cardiovascular System",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "base_sets": 1,
        "base_reps": "30-45 mins",
        "base_rest": "N/A",
        "description": "Low-intensity walking (Joint Friendly, Heart Safe)"
    },
    "yoga flow": {
        "category": "Mobility",
        "met": 2.5,
        "muscle_group": "Full Body Flexibility, Core",
        "equipment": "Yoga Mat",
        "difficulty": "Beginner",
        "base_sets": 1,
        "base_reps": "30 mins",
        "base_rest": "N/A",
        "description": "Vinyasa or Hatha Yoga flow for flexibility & recovery"
    },
    "full body stretching": {
        "category": "Mobility",
        "met": 2.0,
        "muscle_group": "Joints, Major Muscle Groups",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "base_sets": 1,
        "base_reps": "15-20 mins",
        "base_rest": "N/A",
        "description": "Static & dynamic stretching focused on major joints"
    },
    "bird-dog & glute bridge": {
        "category": "Mobility",
        "met": 2.5,
        "muscle_group": "Glutes, Core, Lower Back",
        "equipment": "Bodyweight",
        "difficulty": "Beginner",
        "base_sets": 3,
        "base_reps": "12-15 reps each",
        "base_rest": "45s",
        "description": "Low back friendly activation exercises"
    }
}

def lookup_exercise(name: str) -> dict:
    """Exercise MCP: Lookup exercise parameters by name."""
    clean_name = str(name).strip().lower()
    
    if clean_name in EXERCISE_DATABASE:
        return {"exercise": name, "found": True, "details": EXERCISE_DATABASE[clean_name]}
        
    for key, val in EXERCISE_DATABASE.items():
        if key in clean_name or clean_name in key:
            return {"exercise": key, "found": True, "details": val}
            
    return {
        "exercise": name,
        "found": False,
        "message": f"Exercise '{name}' not found in Exercise MCP database.",
        "details": {
            "category": "General",
            "met": 3.0,
            "muscle_group": "Full Body",
            "equipment": "None",
            "difficulty": "Beginner",
            "base_sets": 3,
            "base_reps": "10",
            "base_rest": "60s",
            "description": "Custom physical movement"
        }
    }

def get_all_exercises() -> dict:
    return EXERCISE_DATABASE
