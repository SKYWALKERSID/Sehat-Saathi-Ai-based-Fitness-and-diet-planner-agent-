import json

HEALTH_KNOWLEDGE = {
    "bmi_categories": {
        "underweight": {
            "range": "< 18.5",
            "health_implications": "Increased risk of nutritional deficiency, osteoporosis, and compromised immune function.",
            "guideline": "Focus on muscle gain, high nutrient density, caloric surplus, and resistance training rather than high-intensity cardiovascular work."
        },
        "normal": {
            "range": "18.5 - 24.9",
            "health_implications": "Low risk of weight-associated chronic diseases.",
            "guideline": "Maintain current body mass index, focus on athletic performance, cardiovascular conditioning, and clean whole-food nutrition balance."
        },
        "overweight": {
            "range": "25.0 - 29.9",
            "health_implications": "Moderate risk of developing cardiovascular issues, metabolic dysfunction, and load-bearing joint stress.",
            "guideline": "Create a mild caloric deficit, limit high-glycemic grains, and incorporate a combination of strength training and steady-state cardio."
        },
        "obese": {
            "range": ">= 30.0",
            "health_implications": "High risk of Type-2 Diabetes, Hypertension, osteoarthritis, and metabolic syndrome.",
            "guideline": "Generate moderate caloric deficit (-500 to -800 kcal), scale exercises to joint-friendly (swimming, cycling, walking) to avoid knee/spine loading, and track glycemic intake."
        }
    },
    "who_exercise_guidelines": {
        "general_adults": "At least 150-300 minutes of moderate-intensity aerobic physical activity, or at least 75-150 minutes of vigorous-intensity aerobic physical activity per week, plus muscle-strengthening activities on 2 or more days per week.",
        "senior_citizens": "Older adults should do varied physical activity that emphasizes functional balance and strength training at moderate or greater intensity on 3 or more days a week, to enhance functional capacity and prevent falls.",
        "hypertension_guidelines": "Avoid heavy isometric straining (e.g., maximum powerlifts or breath-holding Valsalva maneuver). Prioritize steady-state cardiovascular work and high-repetition low-resistance circuits."
    },
    "medical_risks": {
        "hypertension": {
            "action": "Avoid maximal heavy lifting, limit sodium intake, encourage aerobic activity like cycling/brisk walking, ensure slow warmups.",
            "excluded_movements": ["Deadlift (heavy)", "Overhead Press (heavy barbell)"]
        },
        "asthma": {
            "action": "Ensure easy rescue inhaler access, avoid extreme cold-weather outdoor cardio, keep interval cards self-paced, focus on recovery intervals.",
            "excluded_movements": ["HIIT Circuit (outdoor, winter)"]
        },
        "diabetes": {
            "action": "Maintain stable carbohydrate ingestion timings, support low-glycemic high-protein items, integrate regular resistance training to optimize insulin sensitivity.",
            "excluded_movements": []
        }
    }
}

def lookup_health_standards(topic: str) -> dict:
    """Health Knowledge MCP: Retrieves guidelines, WHO standards, or medical risk suggestions."""
    clean_topic = str(topic).strip().lower()
    
    if "bmi" in clean_topic:
        return {"topic": "BMI Categories", "data": HEALTH_KNOWLEDGE["bmi_categories"]}
    elif "who" in clean_topic or "guideline" in clean_topic or "standard" in clean_topic:
        return {"topic": "WHO Guidelines", "data": HEALTH_KNOWLEDGE["who_exercise_guidelines"]}
    elif "medical" in clean_topic or "risk" in clean_topic or "condition" in clean_topic:
        return {"topic": "Medical Risk Management", "data": HEALTH_KNOWLEDGE["medical_risks"]}
        
    # Default: Return everything
    return {"topic": "General Health Knowledge Base", "data": HEALTH_KNOWLEDGE}
