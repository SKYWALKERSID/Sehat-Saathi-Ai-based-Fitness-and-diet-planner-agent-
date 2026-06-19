def calculate_hydration_target(weight_kg: float, activity_level: str, temperature_c: float = 24.0) -> dict:
    """
    Hydration MCP: Calculate dynamic hydration targets based on:
    1. Body weight (baseline: ~35ml per kg of body weight).
    2. Activity level adjustments (+0.5L for lightly active, +1.0L for mod active, +1.5L for very active).
    3. Weather temperature adjustments (+0.5L if temperature exceeds 30C, +1.0L if temperature exceeds 38C).
    """
    # Baseline water intake in Liters
    base_intake = (weight_kg * 35) / 1000.0
    
    # Activity addition
    act_lower = str(activity_level).lower()
    activity_add = 0.0
    if "light" in act_lower:
        activity_add = 0.5
    elif "moderately" in act_lower or "mod" in act_lower:
        activity_add = 1.0
    elif "very" in act_lower or "heavy" in act_lower or "athlete" in act_lower:
        activity_add = 1.5
        
    # Weather addition
    weather_add = 0.0
    if temperature_c >= 38.0:
        weather_add = 1.0
    elif temperature_c >= 30.0:
        weather_add = 0.5
        
    total_target = base_intake + activity_add + weather_add
    
    # Safety capping (Min: 1.5L, Max: 7.0L)
    total_target = max(1.5, min(7.0, round(total_target, 2)))
    
    reasons = [
        f"Baseline physiological target for {weight_kg}kg body weight: {round(base_intake, 2)} Liters."
    ]
    if activity_add > 0:
        reasons.append(f"Added {activity_add}L for training moisture loss ({activity_level}).")
    if weather_add > 0:
        reasons.append(f"Added {weather_add}L to compensate for high ambient temperature ({temperature_c}C).")
        
    return {
        "weight_kg": weight_kg,
        "temperature_c": temperature_c,
        "activity_level": activity_level,
        "hydration_target_l": total_target,
        "calculation_log": reasons
    }
