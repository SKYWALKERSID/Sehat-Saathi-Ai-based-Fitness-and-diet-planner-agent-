import json
from backend.mcp.nutrition import NUTRITION_DATABASE

def get_foods_from_mcp() -> list:
    """Builds a flat list of food profiles dynamically from the Nutrition MCP Database."""
    foods_list = []
    for key, val in NUTRITION_DATABASE.items():
        # Create categories tags to filter preference easily
        tags = []
        cat_lower = val["category"].lower()
        if "veg" in cat_lower:
            tags.append("veg")
        if "non-veg" in cat_lower or "protein" in cat_lower and "veg" not in cat_lower:
            tags.append("non-veg")
        if "vegan" in cat_lower:
            tags.append("vegan")
            tags.append("veg")
        if "fats" in cat_lower or "nuts" in cat_lower:
            tags.append("keto")
            tags.append("low-carb")
            tags.append("veg")
        if "carbs" in cat_lower:
            tags.append("veg")
            
        foods_list.append({
            "name": key.title(),
            "category": val["category"],
            "calories": val["calories"],
            "protein": val["protein"],
            "carbs": val["carbs"],
            "fat": val["fat"],
            "vitamins": val["vitamins"],
            "tags": tags
        })
    return foods_list

def filter_foods(preference: str, allergies: str) -> list:
    foods = get_foods_from_mcp()
    allergy_list = [a.strip().lower() for a in allergies.split(",")] if allergies else []
    
    filtered = []
    for food in foods:
        # Check allergy exclusions
        has_allergen = False
        for allergen in allergy_list:
            if allergen and (allergen in food["name"].lower() or allergen in food["category"].lower()):
                has_allergen = True
                break
        if has_allergen:
            continue
            
        # Check preference filters
        pref = str(preference).lower()
        
        if "vegan" in pref:
            if "vegan" in food["tags"]:
                filtered.append(food)
        elif "vegetarian" in pref:
            if "veg" in food["tags"]:
                filtered.append(food)
        elif "keto" in pref:
            if "keto" in food["tags"] or (food["protein"] >= 10 and food["carbs"] <= 5):
                filtered.append(food)
        elif "low carb" in pref:
            if food["carbs"] <= 10 or "keto" in food["tags"]:
                filtered.append(food)
        else: # non-veg or anything
            filtered.append(food)
            
    # Fallback to general library if filters are too restrictive
    if not filtered:
        filtered = [f for f in foods if "veg" in f["tags"]]
        
    return filtered

def generate_diet_plan(target_calories: float, target_protein: float, target_carbs: float, target_fat: float, preference: str, allergies: str) -> list:
    """
    Generates a daily diet plan with 4 meals, matching calorie targets and food preferences.
    """
    foods = filter_foods(preference, allergies)
    
    # Split calories: Breakfast (30%), Lunch (35%), Evening Snack (12%), Dinner (23%)
    meal_splits = [
        {"type": "Breakfast", "pct": 0.30, "types": ["Carbs", "Protein/Dairy", "Fats/Nuts"]},
        {"type": "Lunch", "pct": 0.35, "types": ["Protein (Non-Veg)", "Protein (Veg)", "Carbs", "Vegetable"]},
        {"type": "Evening Snack", "pct": 0.12, "types": ["Fats/Nuts", "Protein/Dairy"]},
        {"type": "Dinner", "pct": 0.23, "types": ["Protein (Non-Veg)", "Protein (Veg)", "Vegetable", "Fats/Nuts"]}
    ]
    
    diet_plan = []
    
    for idx, split in enumerate(meal_splits):
        meal_cal_target = target_calories * split["pct"]
        
        # Select one food item for each category in the meal
        selected_foods = []
        for cat in split["types"]:
            # Check if category is present in category name or subcategories
            cat_pool = [f for f in foods if cat.lower() in f["category"].lower()]
            if not cat_pool:
                # Fallback: check tags
                cat_pool = [f for f in foods if "veg" in f["tags"]]
            if cat_pool:
                # Pick unique food items per meal
                item_idx = (idx + len(selected_foods)) % len(cat_pool)
                selected_foods.append(cat_pool[item_idx])
                
        # Deduplicate selected foods by name
        seen = set()
        deduped_foods = []
        for f in selected_foods:
            if f["name"] not in seen:
                seen.add(f["name"])
                deduped_foods.append(f)
        selected_foods = deduped_foods if deduped_foods else selected_foods
        
        # Scale food amounts to hit calories target
        total_base_cals = sum([f["calories"] for f in selected_foods])
        if total_base_cals == 0:
            total_base_cals = 100 # safety
            
        scaling_factor = meal_cal_target / total_base_cals
        
        food_details = []
        meal_cals = 0.0
        meal_protein = 0.0
        meal_carbs = 0.0
        meal_fat = 0.0
        
        for f in selected_foods:
            # grams of food
            g = round(scaling_factor * 100)
            if g < 15: g = 15 # safety min
            
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
