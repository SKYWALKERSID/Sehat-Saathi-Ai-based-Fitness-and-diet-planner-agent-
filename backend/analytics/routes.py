import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from database.db import db
from database.models import (
    Profile, ProgressTracking, HydrationRecords,
    NutritionLogs, HealthMetrics, MCPLogs
)
import backend.ml_models.predictor as predictor
from backend.mcp.progress import analyze_progress_history
from backend.mcp.nutrition import lookup_food_nutrition

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api')

@analytics_bp.route('/progress', methods=['POST'])
@login_required
def log_progress():
    data = request.json
    if not data or 'profile_id' not in data:
        return jsonify({"error": "Missing profile_id parameter"}), 400
        
    profile_id = int(data['profile_id'])
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Access denied"}), 403
        
    try:
        log_date = data.get('log_date', datetime.today().strftime('%Y-%m-%d'))
        # Simple date syntax validator
        datetime.strptime(log_date, '%Y-%m-%d')
        
        weight = float(data['weight'])
        water = float(data['water_intake'])
        sleep = float(data['sleep_hours'])
        consumed = float(data.get('calories_consumed', 0.0))
        burned = float(data.get('calories_burned', 0.0))
        
        # Check if log already exists for the day
        log_entry = ProgressTracking.query.filter_by(profile_id=profile_id, log_date=log_date).first()
        if log_entry:
            log_entry.weight = weight
            log_entry.water_intake = water
            log_entry.sleep_hours = sleep
            log_entry.calories_consumed = consumed
            log_entry.calories_burned = burned
        else:
            log_entry = ProgressTracking(
                profile_id=profile_id,
                log_date=log_date,
                weight=weight,
                water_intake=water,
                sleep_hours=sleep,
                calories_consumed=consumed,
                calories_burned=burned
            )
            db.session.add(log_entry)

        # Sync HydrationRecords for the logged date
        hydration_rec = HydrationRecords.query.filter_by(profile_id=profile_id, log_date=log_date).first()
        if hydration_rec:
            hydration_rec.consumed_l = water
        else:
            db.session.add(HydrationRecords(
                profile_id=profile_id,
                log_date=log_date,
                target_l=profile.water_intake,
                consumed_l=water
            ))
            
        # Update user's profile weight with latest tracked weight for accurate future calculations
        profile.weight = weight
        
        db.session.commit()
        return jsonify({"message": "Biometric progress logged successfully!"}), 200
        
    except ValueError:
        return jsonify({"error": "Biometric logs must be valid numbers"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/progress/<int:profile_id>', methods=['GET'])
@login_required
def get_progress_history(profile_id):
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Access denied"}), 403
        
    logs = ProgressTracking.query.filter_by(profile_id=profile_id).order_by(ProgressTracking.log_date.asc()).all()
    history = []
    for l in logs:
        history.append({
            "log_date": l.log_date,
            "weight": l.weight,
            "water_intake": l.water_intake,
            "sleep_hours": l.sleep_hours,
            "calories_consumed": l.calories_consumed,
            "calories_burned": l.calories_burned
        })
    return jsonify(history), 200

@analytics_bp.route('/progress/analyze/<int:profile_id>', methods=['GET'])
@login_required
def run_progress_mcp_analysis(profile_id):
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Access denied"}), 403
        
    logs = ProgressTracking.query.filter_by(profile_id=profile_id).order_by(ProgressTracking.log_date.asc()).all()
    history_logs = [{
        "log_date": l.log_date,
        "weight": l.weight,
        "water_intake": l.water_intake,
        "sleep_hours": l.sleep_hours
    } for l in logs]
    
    analysis = analyze_progress_history(history_logs, profile.fitness_goal)
    db.session.add(MCPLogs(
        profile_id=profile.id,
        mcp_name="Progress MCP",
        tool_name="progress_analyze",
        input_params=json.dumps({"logs_count": len(history_logs), "target_goal": profile.fitness_goal}),
        output_data=json.dumps(analysis)
    ))
    db.session.commit()
    return jsonify(analysis), 200

@analytics_bp.route('/progress/predict/<int:profile_id>', methods=['GET'])
@login_required
def run_progress_predictions(profile_id):
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Access denied"}), 403
        
    # Get current parameters
    curr_weight = profile.weight
    target_cals = profile.goals.target_calories if profile.goals else 2000.0
    tdee = profile.goals.tdee if profile.goals else 2000.0
    calorie_delta = target_cals - tdee
    
    # Calculate workout frequency (number of non-rest days)
    workout_frequency = 0
    for wp in profile.workout_plans:
        exercises = json.loads(wp.exercises)
        has_workout = any(ex.get("name") != "Rest & Recovery" for ex in exercises)
        if has_workout:
            workout_frequency += 1
            
    # Default frequency fallback
    workout_frequency = max(1, min(7, workout_frequency))
    
    # Execute ML Model 4: Progress Prediction
    predictions = predictor.predict_weight_progress(curr_weight, calorie_delta, workout_frequency)
    
    return jsonify({
        "current_weight": curr_weight,
        "calorie_delta": round(calorie_delta, 1),
        "workout_frequency": workout_frequency,
        "predictions": {
            "7_days": predictions["7_days"],
            "30_days": predictions["30_days"],
            "90_days": predictions["90_days"]
        }
    }), 200


@analytics_bp.route('/nutrition-logs/<int:profile_id>', methods=['GET'])
@login_required
def get_nutrition_logs(profile_id):
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Access denied"}), 403

    logs = NutritionLogs.query.filter_by(profile_id=profile_id).order_by(NutritionLogs.created_at.desc()).limit(30).all()
    return jsonify([{
        "id": l.id,
        "log_date": l.log_date,
        "food_name": l.food_name,
        "quantity_g": l.quantity_g,
        "calories": l.calories,
        "protein": l.protein,
        "carbs": l.carbs,
        "fat": l.fat
    } for l in logs]), 200


@analytics_bp.route('/nutrition-logs', methods=['POST'])
@login_required
def add_nutrition_log():
    data = request.json or {}
    profile_id = data.get('profile_id')
    food_name = str(data.get('food_name', '')).strip()
    quantity_g = float(data.get('quantity_g', 100.0))
    log_date = data.get('log_date', datetime.today().strftime('%Y-%m-%d'))

    if not profile_id or not food_name or quantity_g <= 0:
        return jsonify({"error": "Valid profile_id, food_name, and quantity_g are required"}), 400

    profile = Profile.query.filter_by(id=int(profile_id), user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Access denied"}), 403

    lookup = lookup_food_nutrition(food_name)
    details = lookup["details"]
    scale = quantity_g / 100.0

    entry = NutritionLogs(
        profile_id=profile.id,
        log_date=log_date,
        food_name=lookup.get("food", food_name).title(),
        quantity_g=round(quantity_g, 1),
        calories=round(details["calories"] * scale, 1),
        protein=round(details["protein"] * scale, 1),
        carbs=round(details["carbs"] * scale, 1),
        fat=round(details["fat"] * scale, 1)
    )
    db.session.add(entry)
    db.session.add(MCPLogs(
        profile_id=profile.id,
        mcp_name="Nutrition MCP",
        tool_name="nutrition_lookup",
        input_params=json.dumps({"food_name": food_name, "quantity_g": quantity_g}),
        output_data=json.dumps(lookup)
    ))
    db.session.commit()
    return jsonify({
        "message": "Food logged via Nutrition MCP",
        "entry": {
            "id": entry.id,
            "log_date": entry.log_date,
            "food_name": entry.food_name,
            "quantity_g": entry.quantity_g,
            "calories": entry.calories,
            "protein": entry.protein,
            "carbs": entry.carbs,
            "fat": entry.fat,
            "found_in_mcp": lookup["found"]
        }
    }), 201


@analytics_bp.route('/health-metrics/<int:profile_id>', methods=['GET'])
@login_required
def get_health_metrics(profile_id):
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Access denied"}), 403

    metrics = HealthMetrics.query.filter_by(profile_id=profile_id).order_by(HealthMetrics.log_date.desc(), HealthMetrics.created_at.desc()).limit(30).all()
    return jsonify([{
        "id": m.id,
        "log_date": m.log_date,
        "blood_pressure": m.blood_pressure,
        "heart_rate": m.heart_rate,
        "blood_sugar": m.blood_sugar,
        "notes": m.notes
    } for m in metrics]), 200


@analytics_bp.route('/health-metrics', methods=['POST'])
@login_required
def add_health_metric():
    data = request.json or {}
    profile_id = data.get('profile_id')
    if not profile_id:
        return jsonify({"error": "Missing profile_id"}), 400

    profile = Profile.query.filter_by(id=int(profile_id), user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Access denied"}), 403

    log_date = data.get('log_date', datetime.today().strftime('%Y-%m-%d'))
    bp = str(data.get('blood_pressure', '')).strip() or None
    hr = int(data['heart_rate']) if data.get('heart_rate') else None
    sugar = float(data['blood_sugar']) if data.get('blood_sugar') else None
    notes = str(data.get('notes', '')).strip()

    metric = HealthMetrics(
        profile_id=profile.id,
        log_date=log_date,
        blood_pressure=bp,
        heart_rate=hr,
        blood_sugar=sugar,
        notes=notes
    )
    db.session.add(metric)
    db.session.commit()
    return jsonify({"message": "Health vitals logged successfully!"}), 201


@analytics_bp.route('/mcp-logs/<int:profile_id>', methods=['GET'])
@login_required
def get_mcp_logs(profile_id):
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Access denied"}), 403

    logs = MCPLogs.query.filter_by(profile_id=profile_id).order_by(MCPLogs.created_at.desc()).limit(25).all()
    return jsonify([{
        "id": l.id,
        "mcp_name": l.mcp_name,
        "tool_name": l.tool_name,
        "input_params": json.loads(l.input_params) if l.input_params else {},
        "output_data": json.loads(l.output_data) if l.output_data else {},
        "created_at": l.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for l in logs]), 200
