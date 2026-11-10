import json
from backend.mcp.nutrition import NUTRITION_DATABASE

def get_foods_from_mcp() -> list:
    """Builds a flat list of food profiles dynamically from the Nutrition MCP Database."""
    foods_list = []
    for key, val in NUTRITION_DATABASE.items():
        tags = list(val.get("tags", []))
        cat_lower = val["category"].lower()
        if "veg" in cat_lower and "non-veg" not in cat_lower and "veg" not in tags:
            tags.append("veg")
        if "non-veg" in cat_lower and "non-veg" not in tags:
            tags.append("non-veg")
        if "vegan" in cat_lower and "vegan" not in tags:
            tags.append("vegan")
            if "veg" not in tags:
                tags.append("veg")
        if ("fats" in cat_lower or "nuts" in cat_lower) and "keto" not in tags:
            tags.extend(["keto", "low-carb", "veg"])
        if "carbs" in cat_lower and "veg" not in tags:
            tags.append("veg")

        foods_list.append({
            "name": key.title(),
            "category": val["category"],
            "calories": val["calories"],
            "protein": val["protein"],
            "carbs": val["carbs"],
            "fat": val["fat"],
            "vitamins": val["vitamins"],
            "tags": list(set(tags)),
            "substitutions": val.get("substitutions", [])
        })
    return foods_list

def filter_foods(preference: str, allergies: str) -> list:
    foods = get_foods_from_mcp()
    allergy_list = [a.strip().lower() for a in allergies.split(",") if a.strip().lower() != "none"] if allergies else []
    
    filtered = []
    for food in foods:
        # Check allergy exclusions (match name, category, or tags like gluten, dairy, nuts, peanuts)
        has_allergen = False
        food_tags_str = " ".join(food["tags"]).lower()
        for allergen in allergy_list:
            if allergen and (
                allergen in food["name"].lower()
                or allergen in food["category"].lower()
                or allergen in food_tags_str
            ):
                has_allergen = True
                break
        if has_allergen:
            continue
            
        # Check preference filters
        pref = str(preference).lower()
        tags = food["tags"]
        
        if "jain" in pref:
            if "jain" in tags and "non-veg" not in tags and "egg" not in tags and "root-vegetable" not in tags:
                filtered.append(food)
        elif "vegan" in pref:
            if "vegan" in tags and "dairy" not in tags and "egg" not in tags and "non-veg" not in tags:
                filtered.append(food)
        elif "eggetarian" in pref:
            if ("veg" in tags or "egg" in tags) and "non-veg" not in tags:
                filtered.append(food)
        elif "vegetarian" in pref:
            if "veg" in tags and "non-veg" not in tags and "egg" not in tags:
                filtered.append(food)
        elif "keto" in pref:
            if "keto" in tags or (food["protein"] >= 10 and food["carbs"] <= 5):
                filtered.append(food)
        elif "low carb" in pref:
            if food["carbs"] <= 15 or "low-carb" in tags or "keto" in tags:
                filtered.append(food)
        elif "high protein" in pref:
            if "high-protein" in tags or food["protein"] >= 12 or "vegetable" in food["category"].lower() or "carbs" in food["category"].lower():
                filtered.append(food)
        else:  # non-vegetarian or general
            filtered.append(food)
            
    # Fallback to general vegetarian library if filters are too restrictive
    if not filtered:
        filtered = [f for f in foods if "veg" in f["tags"] and "non-veg" not in f["tags"]]
        
    return filtered

def generate_diet_plan(target_calories: float, target_protein: float, target_carbs: float, target_fat: float, preference: str, allergies: str) -> list:
    """
    Generates a daily diet plan with 4 meals, matching calorie targets and food preferences.
    """
    foods = filter_foods(preference, allergies)
    pref_lower = str(preference).lower()
    
    # Split calories: Breakfast (28%), Lunch (35%), Evening Snack (12%), Dinner (25%)
    meal_splits = [
        {"type": "Breakfast", "pct": 0.28, "roles": ["carb", "protein", "fat"]},
        {"type": "Lunch", "pct": 0.35, "roles": ["protein", "carb", "veg"]},
        {"type": "Evening Snack", "pct": 0.12, "roles": ["fat", "protein"]},
        {"type": "Dinner", "pct": 0.25, "roles": ["protein", "veg", "carb" if "keto" not in pref_lower else "fat"]}
    ]
    
    # Classify filtered foods into functional roles
    proteins = [f for f in foods if "protein" in f["category"].lower()]
    carbs = [f for f in foods if "carb" in f["category"].lower()]
    fats = [f for f in foods if "fat" in f["category"].lower() or "nuts" in f["category"].lower()]
    veggies = [f for f in foods if "vegetable" in f["category"].lower()]
    
    # Ensure non-empty pools using fallback from filtered foods
    if not proteins: proteins = foods
    if not carbs: carbs = veggies if "keto" in pref_lower and veggies else foods
    if not fats: fats = foods
    if not veggies: veggies = foods

    role_pools = {
        "protein": proteins,
        "carb": carbs,
        "fat": fats,
        "veg": veggies
    }
    
    diet_plan = []
    
    for idx, split in enumerate(meal_splits):
        meal_cal_target = target_calories * split["pct"]
        
        selected_foods = []
        for r_idx, role in enumerate(split["roles"]):
            pool = role_pools.get(role, foods)
            if pool:
                candidate = pool[(idx + r_idx) % len(pool)]
                # Avoid duplicate food in the same meal if pool has other options
                if any(s["name"] == candidate["name"] for s in selected_foods) and len(pool) > 1:
                    candidate = pool[(idx + r_idx + 1) % len(pool)]
                selected_foods.append(candidate)
                
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
            total_base_cals = 100
            
        scaling_factor = meal_cal_target / total_base_cals
        
        food_details = []
        meal_cals = 0.0
        meal_protein = 0.0
        meal_carbs = 0.0
        meal_fat = 0.0
        
        for f in selected_foods:
            # Adjust serving size realistically (nuts/fats shouldn't be 300g, veggies shouldn't be 15g)
            base_g = scaling_factor * 100
            if "fats" in f["category"].lower():
                g = max(15, min(60, round(base_g * 0.45)))
            elif "vegetable" in f["category"].lower():
                g = max(80, min(250, round(base_g * 1.4)))
            else:
                g = max(30, min(350, round(base_g)))
            
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
                "fats": round(fat, 1),
                "vitamins": f.get("vitamins", ""),
                "substitutions": f.get("substitutions", [])
            })
            
            meal_cals += cal
            meal_protein += prot
            meal_carbs += carb
            meal_fat += fat
            
        # Second pass: normalize primary protein/carb item so meal calories match target closely
        if food_details and meal_cals > 0:
            cal_ratio = meal_cal_target / meal_cals
            if 0.6 <= cal_ratio <= 1.6:
                meal_cals = 0.0
                meal_protein = 0.0
                meal_carbs = 0.0
                meal_fat = 0.0
                for item, orig_f in zip(food_details, selected_foods):
                    new_g = max(15, round(item["serving_g"] * cal_ratio))
                    item["serving_g"] = new_g
                    item["calories"] = round((orig_f["calories"] * new_g) / 100.0, 1)
                    item["protein"] = round((orig_f["protein"] * new_g) / 100.0, 1)
                    item["carbohydrates"] = round((orig_f["carbs"] * new_g) / 100.0, 1)
                    item["fats"] = round((orig_f["fat"] * new_g) / 100.0, 1)
                    meal_cals += item["calories"]
                    meal_protein += item["protein"]
                    meal_carbs += item["carbohydrates"]
                    meal_fat += item["fats"]

        diet_plan.append({
            "meal_type": split["type"],
            "food_items": food_details,
            "calories": round(meal_cals, 1),
            "protein": round(meal_protein, 1),
            "carbohydrates": round(meal_carbs, 1),
            "fats": round(meal_fat, 1)
        })
        
    return diet_plan
