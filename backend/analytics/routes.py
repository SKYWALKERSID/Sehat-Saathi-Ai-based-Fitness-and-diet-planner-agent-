import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from database.db import db
from database.models import Profile, ProgressTracking
import backend.ml_models.predictor as predictor
from backend.mcp.progress import analyze_progress_history

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
