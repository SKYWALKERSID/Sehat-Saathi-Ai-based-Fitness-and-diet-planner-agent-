import json

# Local Food database with macro & micro details per 100g
NUTRITION_DATABASE = {
    "chicken breast": {
        "calories": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6,
        "vitamins": "Vitamin B6, Vitamin B12, Niacin, Iron, Zinc",
        "category": "Protein (Non-Veg)",
        "tags": ["non-veg", "keto", "low-carb", "high-protein"],
        "substitutions": ["Grilled Salmon", "Paneer", "Firm Tofu"]
    },
    "salmon": {
        "calories": 206, "protein": 22.0, "carbs": 0.0, "fat": 13.0,
        "vitamins": "Omega-3 Fatty Acids, Vitamin D, Vitamin B12, Selenium",
        "category": "Protein (Non-Veg)",
        "tags": ["non-veg", "keto", "low-carb", "high-protein"],
        "substitutions": ["Chicken Breast", "Tuna", "Tempeh"]
    },
    "eggs": {
        "calories": 155, "protein": 13.0, "carbs": 1.1, "fat": 11.0,
        "vitamins": "Vitamin D, Vitamin B12, Riboflavin, Choline, Selenium",
        "category": "Protein (Eggetarian)",
        "tags": ["egg", "keto", "low-carb", "high-protein"],
        "substitutions": ["Paneer", "Greek Yogurt", "Tofu Scramble"]
    },
    "egg whites": {
        "calories": 52, "protein": 11.0, "carbs": 0.7, "fat": 0.2,
        "vitamins": "Riboflavin, Selenium, Potassium",
        "category": "Protein (Eggetarian)",
        "tags": ["egg", "keto", "low-carb", "high-protein", "low-fat"],
        "substitutions": ["Greek Yogurt", "Low-Fat Cottage Cheese", "Tofu"]
    },
    "paneer": {
        "calories": 265, "protein": 18.0, "carbs": 1.2, "fat": 20.8,
        "vitamins": "Calcium, Vitamin A, Vitamin D, Phosphorus",
        "category": "Protein/Dairy (Veg)",
        "tags": ["veg", "jain", "keto", "low-carb", "high-protein", "dairy"],
        "substitutions": ["Firm Tofu", "Greek Yogurt", "Chickpeas"]
    },
    "greek yogurt": {
        "calories": 59, "protein": 10.0, "carbs": 3.6, "fat": 0.4,
        "vitamins": "Calcium, Vitamin B12, Riboflavin, Potassium, Probiotics",
        "category": "Protein/Dairy (Veg)",
        "tags": ["veg", "jain", "low-carb", "high-protein", "dairy"],
        "substitutions": ["Paneer", "Soy Yogurt", "Cottage Cheese"]
    },
    "milk": {
        "calories": 42, "protein": 3.4, "carbs": 5.0, "fat": 1.0,
        "vitamins": "Calcium, Vitamin D, Vitamin B2, Vitamin B12, Potassium",
        "category": "Protein/Dairy (Veg)",
        "tags": ["veg", "jain", "dairy"],
        "substitutions": ["Soy Milk", "Almond Milk", "Greek Yogurt"]
    },
    "whey protein isolate": {
        "calories": 360, "protein": 85.0, "carbs": 3.0, "fat": 1.5,
        "vitamins": "BCAAs, Calcium, Iron",
        "category": "Protein/Dairy (Veg)",
        "tags": ["veg", "jain", "keto", "low-carb", "high-protein", "dairy"],
        "substitutions": ["Pea Protein Isolate", "Greek Yogurt", "Egg Whites"]
    },
    "tofu": {
        "calories": 144, "protein": 17.0, "carbs": 2.8, "fat": 8.0,
        "vitamins": "Calcium, Iron, Manganese, Selenium, Phosphorus",
        "category": "Protein (Vegan)",
        "tags": ["veg", "vegan", "jain", "keto", "low-carb", "high-protein"],
        "substitutions": ["Paneer", "Tempeh", "Cooked Lentils"]
    },
    "tempeh": {
        "calories": 193, "protein": 19.0, "carbs": 9.0, "fat": 11.0,
        "vitamins": "Iron, Calcium, Riboflavin, Niacin, Magnesium",
        "category": "Protein (Vegan)",
        "tags": ["veg", "vegan", "keto", "low-carb", "high-protein"],
        "substitutions": ["Firm Tofu", "Paneer", "Chickpeas"]
    },
    "lentils (moong dal)": {
        "calories": 116, "protein": 9.0, "carbs": 20.0, "fat": 0.4,
        "vitamins": "Folate, Iron, Manganese, Phosphorus, Thiamin",
        "category": "Protein (Vegan)",
        "tags": ["veg", "vegan", "jain", "high-protein", "low-fat"],
        "substitutions": ["Chickpeas", "Tofu", "Quinoa"]
    },
    "chickpeas (chana)": {
        "calories": 164, "protein": 8.9, "carbs": 27.4, "fat": 2.6,
        "vitamins": "Folate, Iron, Phosphorus, Copper, Manganese",
        "category": "Protein (Vegan)",
        "tags": ["veg", "vegan", "jain", "high-protein"],
        "substitutions": ["Lentils (Moong Dal)", "Kidney Beans (Rajma)", "Paneer"]
    },
    "rolled oats": {
        "calories": 389, "protein": 16.9, "carbs": 66.3, "fat": 6.9,
        "vitamins": "Manganese, Phosphorus, Magnesium, Iron, Zinc, Folate",
        "category": "Carbs",
        "tags": ["veg", "vegan", "jain", "high-protein"],
        "substitutions": ["Quinoa", "Dalia (Broken Wheat)", "Brown Rice"]
    },
    "brown rice": {
        "calories": 111, "protein": 2.6, "carbs": 23.0, "fat": 0.9,
        "vitamins": "Magnesium, Phosphorus, Niacin, Thiamin",
        "category": "Carbs",
        "tags": ["veg", "vegan", "jain", "gluten-free"],
        "substitutions": ["Quinoa", "Whole Wheat Roti", "White Rice"]
    },
    "white rice": {
        "calories": 130, "protein": 2.7, "carbs": 28.0, "fat": 0.3,
        "vitamins": "Iron, Thiamin, Niacin",
        "category": "Carbs",
        "tags": ["veg", "vegan", "jain", "gluten-free"],
        "substitutions": ["Brown Rice", "Quinoa", "Rolled Oats"]
    },
    "quinoa": {
        "calories": 120, "protein": 4.4, "carbs": 21.3, "fat": 1.9,
        "vitamins": "Manganese, Magnesium, Phosphorus, Folate, Iron",
        "category": "Carbs",
        "tags": ["veg", "vegan", "jain", "gluten-free", "high-protein"],
        "substitutions": ["Brown Rice", "Rolled Oats", "Buckwheat"]
    },
    "whole wheat roti": {
        "calories": 247, "protein": 11.0, "carbs": 43.0, "fat": 3.4,
        "vitamins": "Iron, Magnesium, Selenium, B Vitamins",
        "category": "Carbs",
        "tags": ["veg", "vegan", "jain", "gluten"],
        "substitutions": ["Jowar Roti", "Brown Rice", "Quinoa"]
    },
    "sweet potato": {
        "calories": 86, "protein": 1.6, "carbs": 20.0, "fat": 0.1,
        "vitamins": "Vitamin A, Vitamin C, Manganese, Potassium",
        "category": "Carbs",
        "tags": ["veg", "vegan", "root-vegetable", "gluten-free"],
        "substitutions": ["Brown Rice", "Quinoa", "Rolled Oats"]
    },
    "banana": {
        "calories": 89, "protein": 1.1, "carbs": 22.8, "fat": 0.3,
        "vitamins": "Vitamin B6, Vitamin C, Potassium, Manganese",
        "category": "Carbs",
        "tags": ["veg", "vegan", "jain", "fruit", "gluten-free"],
        "substitutions": ["Apple", "Papaya", "Pomegranate"]
    },
    "apple": {
        "calories": 52, "protein": 0.3, "carbs": 13.8, "fat": 0.2,
        "vitamins": "Vitamin C, Potassium, Vitamin K, Dietary Fiber",
        "category": "Carbs",
        "tags": ["veg", "vegan", "jain", "fruit", "gluten-free"],
        "substitutions": ["Pear", "Guava", "Orange"]
    },
    "almonds": {
        "calories": 579, "protein": 21.0, "carbs": 22.0, "fat": 49.0,
        "vitamins": "Vitamin E, Magnesium, Manganese, Riboflavin, Calcium",
        "category": "Fats/Nuts",
        "tags": ["veg", "vegan", "jain", "keto", "low-carb", "nuts"],
        "substitutions": ["Walnuts", "Pumpkin Seeds", "Chia Seeds"]
    },
    "walnuts": {
        "calories": 654, "protein": 15.0, "carbs": 14.0, "fat": 65.0,
        "vitamins": "Omega-3 ALA, Copper, Manganese, Molybdenum, Biotin",
        "category": "Fats/Nuts",
        "tags": ["veg", "vegan", "jain", "keto", "low-carb", "nuts"],
        "substitutions": ["Almonds", "Flaxseeds", "Chia Seeds"]
    },
    "peanut butter": {
        "calories": 588, "protein": 25.0, "carbs": 20.0, "fat": 50.0,
        "vitamins": "Vitamin E, Niacin, Magnesium, Vitamin B6, Phosphorus",
        "category": "Fats/Nuts",
        "tags": ["veg", "vegan", "jain", "keto", "low-carb", "high-protein", "peanuts", "nuts"],
        "substitutions": ["Almond Butter", "Sunflower Seed Butter", "Chia Seeds"]
    },
    "chia seeds": {
        "calories": 486, "protein": 17.0, "carbs": 42.0, "fat": 31.0,
        "vitamins": "Calcium, Iron, Magnesium, Omega-3 Fatty Acids, Fiber",
        "category": "Fats/Nuts",
        "tags": ["veg", "vegan", "jain", "keto", "low-carb", "gluten-free"],
        "substitutions": ["Flaxseeds", "Pumpkin Seeds", "Walnuts"]
    },
    "avocado": {
        "calories": 160, "protein": 2.0, "carbs": 9.0, "fat": 15.0,
        "vitamins": "Vitamin K, Folate, Vitamin C, Potassium, Vitamin E",
        "category": "Fats/Nuts",
        "tags": ["veg", "vegan", "jain", "keto", "low-carb", "gluten-free"],
        "substitutions": ["Almonds", "Olive Oil Drizzle", "Chia Seeds"]
    },
    "spinach (palak)": {
        "calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4,
        "vitamins": "Vitamin A, Vitamin C, Vitamin K1, Iron, Calcium, Folic Acid",
        "category": "Vegetable",
        "tags": ["veg", "vegan", "jain", "keto", "low-carb", "gluten-free"],
        "substitutions": ["Broccoli", "Fenugreek Leaves (Methi)", "Mixed Salad Greens"]
    },
    "broccoli": {
        "calories": 34, "protein": 2.8, "carbs": 6.6, "fat": 0.4,
        "vitamins": "Vitamin C, Vitamin K, Folate, Potassium, Manganese",
        "category": "Vegetable",
        "tags": ["veg", "vegan", "jain", "keto", "low-carb", "gluten-free"],
        "substitutions": ["Spinach (Palak)", "Green Beans", "Zucchini"]
    },
    "mixed cucumber & tomato salad": {
        "calories": 18, "protein": 0.9, "carbs": 3.8, "fat": 0.2,
        "vitamins": "Vitamin C, Vitamin K, Potassium, Lycopene",
        "category": "Vegetable",
        "tags": ["veg", "vegan", "jain", "keto", "low-carb", "gluten-free"],
        "substitutions": ["Spinach (Palak)", "Broccoli", "Bell Peppers"]
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
