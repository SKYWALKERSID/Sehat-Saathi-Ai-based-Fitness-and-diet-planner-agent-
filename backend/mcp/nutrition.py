import json

# Local Food database with macro & micro details per 100g
NUTRITION_DATABASE = {
    "chicken breast": {
        "calories": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6,
        "vitamins": "Vitamin B6, Vitamin B12, Niacin, Iron, Zinc",
        "category": "Protein (Non-Veg)"
    },
    "paneer": {
        "calories": 265, "protein": 18.0, "carbs": 1.2, "fat": 20.8,
        "vitamins": "Calcium, Vitamin A, Vitamin D, Phosphorus",
        "category": "Protein (Veg)"
    },
    "brown rice": {
        "calories": 111, "protein": 2.6, "carbs": 23.0, "fat": 0.9,
        "vitamins": "Magnesium, Phosphorus, Niacin, Thiamin",
        "category": "Carbs"
    },
    "white rice": {
        "calories": 130, "protein": 2.7, "carbs": 28.0, "fat": 0.3,
        "vitamins": "Iron, Thiamin, Niacin",
        "category": "Carbs"
    },
    "eggs": {
        "calories": 155, "protein": 13.0, "carbs": 1.1, "fat": 11.0,
        "vitamins": "Vitamin D, Vitamin B12, Riboflavin, Choline, Selenium",
        "category": "Protein (Veg-Egg)"
    },
    "milk": {
        "calories": 42, "protein": 3.4, "carbs": 5.0, "fat": 1.0,
        "vitamins": "Calcium, Vitamin D, Vitamin B2, Vitamin B12, Potassium",
        "category": "Protein/Dairy"
    },
    "banana": {
        "calories": 89, "protein": 1.1, "carbs": 22.8, "fat": 0.3,
        "vitamins": "Vitamin B6, Vitamin C, Potassium, Manganese",
        "category": "Fruit/Carbs"
    },
    "tofu": {
        "calories": 144, "protein": 17.0, "carbs": 2.8, "fat": 8.0,
        "vitamins": "Calcium, Iron, Manganese, Selenium, Phosphorus",
        "category": "Protein (Vegan)"
    },
    "salmon": {
        "calories": 206, "protein": 22.0, "carbs": 0.0, "fat": 13.0,
        "vitamins": "Omega-3 Fatty Acids, Vitamin D, Vitamin B12, Selenium",
        "category": "Protein (Non-Veg)"
    },
    "greek yogurt": {
        "calories": 59, "protein": 10.0, "carbs": 3.6, "fat": 0.4,
        "vitamins": "Calcium, Vitamin B12, Riboflavin, Potassium",
        "category": "Protein/Dairy"
    },
    "almonds": {
        "calories": 579, "protein": 21.0, "carbs": 22.0, "fat": 49.0,
        "vitamins": "Vitamin E, Magnesium, Manganese, Riboflavin, Calcium",
        "category": "Fats/Nuts"
    },
    "spinach": {
        "calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4,
        "vitamins": "Vitamin A, Vitamin C, Vitamin K1, Iron, Calcium, Folic Acid",
        "category": "Vegetable"
    },
    "broccoli": {
        "calories": 34, "protein": 2.8, "carbs": 6.6, "fat": 0.4,
        "vitamins": "Vitamin C, Vitamin K, Folate, Potassium, Manganese",
        "category": "Vegetable"
    }
}

def lookup_food_nutrition(food_name: str) -> dict:
    """Nutrition MCP: Lookup nutrient profile for a given food name."""
    name_clean = str(food_name).strip().lower()
    
    # Try exact match first
    if name_clean in NUTRITION_DATABASE:
        return {"food": food_name, "found": True, "details": NUTRITION_DATABASE[name_clean]}
        
    # Try substring match
    for key, val in NUTRITION_DATABASE.items():
        if key in name_clean or name_clean in key:
            return {"food": key, "found": True, "details": val}
            
    # Default fallback
    return {
        "food": food_name,
        "found": False,
        "message": f"Food item '{food_name}' not found in Nutrition MCP database.",
        "details": {
            "calories": 100,
            "protein": 5.0,
            "carbs": 15.0,
            "fat": 2.0,
            "vitamins": "General Micronutrients",
            "category": "Generic"
        }
    }
