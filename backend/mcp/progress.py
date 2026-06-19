import json

def analyze_progress_history(history_logs: list, target_goal: str) -> dict:
    """
    Progress MCP: Analyze a list of daily progress logs to determine:
    1. Weight change velocity (kg/week).
    2. Compliance rate (water & sleep).
    3. Warning triggers if weight loss/gain is too aggressive or stalled.
    """
    if not history_logs or len(history_logs) < 2:
        return {
            "status": "Insufficient logs",
            "message": "At least 2 daily logs are needed to compute historical progress trends.",
            "weight_change_kg": 0.0,
            "weekly_velocity_kg": 0.0,
            "sleep_compliance_pct": 100.0,
            "water_compliance_pct": 100.0,
            "alerts": []
        }
        
    # Sort logs by date
    sorted_logs = sorted(history_logs, key=lambda x: x.get('log_date', ''))
    
    first_weight = float(sorted_logs[0]['weight'])
    last_weight = float(sorted_logs[-1]['weight'])
    weight_change = last_weight - first_weight
    
    # Calculate days range
    from datetime import datetime
    d1 = datetime.strptime(sorted_logs[0]['log_date'], '%Y-%m-%d')
    d2 = datetime.strptime(sorted_logs[-1]['log_date'], '%Y-%m-%d')
    days = (d2 - d1).days or 1
    
    weekly_velocity = (weight_change / days) * 7.0
    
    # Compute average compliance
    sleep_list = [float(l.get('sleep_hours', 8)) for l in sorted_logs]
    water_list = [float(l.get('water_intake', 2)) for l in sorted_logs]
    
    avg_sleep = sum(sleep_list) / len(sleep_list)
    avg_water = sum(water_list) / len(water_list)
    
    sleep_compliance = min(100.0, (avg_sleep / 7.5) * 100.0)
    water_compliance = min(100.0, (avg_water / 2.5) * 100.0)
    
    # Triggers
    alerts = []
    goal = str(target_goal).lower()
    
    if "loss" in goal or "deficit" in goal:
        if weekly_velocity < -1.5:
            alerts.append("CRITICAL: Weight loss is exceeding healthy bounds (>1.5kg/week). Scale up calories by 250 kcal to prevent lean mass catabolism.")
        elif weekly_velocity > -0.1:
            alerts.append("WARNING: Weight loss has stalled. Consider increasing cardiovascular energy expenditure or verifying food portions.")
            
    elif "gain" in goal or "muscle" in goal:
        if weekly_velocity > 1.2:
            alerts.append("WARNING: Weight gain is very rapid (>1.2kg/week). You may be accumulating fat rather than lean tissue. Scale down daily calories slightly.")
        elif weekly_velocity < 0.1:
            alerts.append("WARNING: Weight gain has stalled. Increase caloric intake by 300 kcal/day (add healthy fats/carbs).")
            
    return {
        "status": "Analyzed",
        "weight_change_kg": round(weight_change, 2),
        "weekly_velocity_kg": round(weekly_velocity, 2),
        "sleep_compliance_pct": round(sleep_compliance, 1),
        "water_compliance_pct": round(water_compliance, 1),
        "avg_sleep_hours": round(avg_sleep, 1),
        "avg_water_liters": round(avg_water, 1),
        "alerts": alerts
    }
