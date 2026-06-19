from flask import Blueprint, request, jsonify
import os
from flask_login import login_required, current_user
from app.models import Profile, ProgressLog, Feedback
from app.recommender import generate_full_profile
from app import db
import json
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/profile', methods=['POST'])
@login_required
def create_profile():
    data = request.json
    if not data:
        return jsonify({"error": "No input parameters provided"}), 400
        
    required_fields = [
        'name', 'age', 'gender', 'height', 'weight', 
        'fitness_goal', 'activity_level', 'diet_preference', 
        'water_intake', 'sleep_hours', 'workout_experience'
    ]
    
    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == "":
            return jsonify({"error": f"Field '{field}' is required and cannot be empty"}), 400
            
    try:
        # Numerical bounds validation
        name = str(data['name']).strip()
        age = int(data['age'])
        height = float(data['height'])
        weight = float(data['weight'])
        water_intake = float(data['water_intake'])
        sleep_hours = float(data['sleep_hours'])
        
        if age <= 0 or age > 120:
            return jsonify({"error": "Age must be between 1 and 120"}), 400
        if height <= 50 or height > 275:
            return jsonify({"error": "Height must be between 50cm and 275cm"}), 400
        if weight <= 10 or weight > 500:
            return jsonify({"error": "Weight must be between 10kg and 500kg"}), 400
        if water_intake < 0 or water_intake > 20:
            return jsonify({"error": "Daily water intake must be between 0 and 20 Liters"}), 400
        if sleep_hours < 0 or sleep_hours > 24:
            return jsonify({"error": "Sleep hours must be between 0 and 24 hours"}), 400
            
        gender = str(data['gender']).strip()
        fitness_goal = str(data['fitness_goal']).strip()
        activity_level = str(data['activity_level']).strip()
        diet_preference = str(data['diet_preference']).strip()
        workout_experience = str(data['workout_experience']).strip()
        
        medical_conditions = str(data.get('medical_conditions', 'None')).strip()
        injuries = str(data.get('injuries', 'None')).strip()
        allergies = str(data.get('allergies', 'None')).strip()
        
        clean_user_data = {
            'name': name,
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'fitness_goal': fitness_goal,
            'activity_level': activity_level,
            'diet_preference': diet_preference,
            'water_intake': water_intake,
            'sleep_hours': sleep_hours,
            'workout_experience': workout_experience,
            'medical_conditions': medical_conditions if medical_conditions else "None",
            'injuries': injuries if injuries else "None",
            'allergies': allergies if allergies else "None"
        }
        
        # Run Rule-based Recommendation engine
        goals, diet, workouts = generate_full_profile(clean_user_data)
        
        # Save profile inside SQL Database bound to current_user
        new_profile = Profile(
            user_id=current_user.id,
            name=name,
            age=age,
            gender=gender,
            height=height,
            weight=weight,
            fitness_goal=fitness_goal,
            activity_level=activity_level,
            diet_preference=diet_preference,
            water_intake=water_intake,
            sleep_hours=sleep_hours,
            workout_experience=workout_experience,
            medical_conditions=clean_user_data['medical_conditions'],
            injuries=clean_user_data['injuries'],
            allergies=clean_user_data['allergies'],
            
            # Metrics
            bmi=goals['bmi'],
            bmi_category=goals['bmi_category'],
            bmr=goals['bmr'],
            tdee=goals['tdee'],
            target_calories=goals['target_calories'],
            target_protein=goals['target_protein'],
            target_carbs=goals['target_carbs'],
            target_fat=goals['target_fat'],
            confidence_score=goals['confidence_score'],
            
            # JSON structures
            advisory_notes=json.dumps(goals['advisory_notes']),
            diet_meals_json=json.dumps(diet),
            workout_plan_json=json.dumps(workouts)
        )
        
        db.session.add(new_profile)
        db.session.commit()
        
        # Log Day 0 progress metric
        today_str = datetime.today().strftime('%Y-%m-%d')
        initial_progress = ProgressLog(
            profile_id=new_profile.id,
            log_date=today_str,
            weight=weight,
            water_intake=water_intake,
            sleep_hours=sleep_hours,
            calories_consumed=0.0,
            calories_burned=0.0
        )
        db.session.add(initial_progress)
        db.session.commit()
        
        return jsonify({
            "message": "Fitness profile generated and saved!",
            "profile_id": new_profile.id
        }), 201
        
    except ValueError:
        return jsonify({"error": "Physical measurements must be valid numeric values"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error during profile creation: {str(e)}"}), 500

@api_bp.route('/profiles', methods=['GET'])
@login_required
def get_user_profiles():
    # Return user's own profiles only
    profiles = Profile.query.filter_by(user_id=current_user.id).order_by(Profile.created_at.desc()).all()
    
    profiles_data = []
    for p in profiles:
        profiles_data.append({
            "id": p.id,
            "name": p.name,
            "fitness_goal": p.fitness_goal,
            "created_at": p.created_at.strftime('%Y-%m-%d %H:%M'),
            "bmi": p.bmi,
            "target_calories": p.target_calories
        })
    return jsonify(profiles_data), 200

@api_bp.route('/profile/<int:profile_id>', methods=['GET'])
@login_required
def get_profile_details(profile_id):
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Profile not found or access denied"}), 404
        
    # Build complete return payload
    advisory = json.loads(profile.advisory_notes)
    diet = json.loads(profile.diet_meals_json)
    workout = json.loads(profile.workout_plan_json)
    
    return jsonify({
        "user": {
            "id": profile.id,
            "name": profile.name,
            "age": profile.age,
            "gender": profile.gender,
            "height": profile.height,
            "weight": profile.weight,
            "fitness_goal": profile.fitness_goal,
            "activity_level": profile.activity_level,
            "diet_preference": profile.diet_preference,
            "water_intake": profile.water_intake,
            "sleep_hours": profile.sleep_hours,
            "workout_experience": profile.workout_experience,
            "medical_conditions": profile.medical_conditions,
            "injuries": profile.injuries,
            "allergies": profile.allergies
        },
        "goals": {
            "bmi": profile.bmi,
            "bmi_category": profile.bmi_category,
            "bmr": profile.bmr,
            "tdee": profile.tdee,
            "target_calories": profile.target_calories,
            "target_protein": profile.target_protein,
            "target_carbs": profile.target_carbs,
            "target_fat": profile.target_fat,
            "confidence_score": profile.confidence_score,
            "advisory_notes": advisory
        },
        "diet": diet,
        "workout": workout
    }), 200

@api_bp.route('/progress', methods=['POST'])
@login_required
def log_progress():
    data = request.json
    if not data or 'profile_id' not in data:
        return jsonify({"error": "Missing profile_id parameters"}), 400
        
    profile_id = int(data['profile_id'])
    
    # Ownership Check
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Access denied"}), 403
        
    try:
        log_date = data.get('log_date', datetime.today().strftime('%Y-%m-%d'))
        datetime.strptime(log_date, '%Y-%m-%d')
        
        weight = float(data['weight'])
        water_intake = float(data['water_intake'])
        sleep_hours = float(data['sleep_hours'])
        calories_consumed = float(data.get('calories_consumed', 0.0))
        calories_burned = float(data.get('calories_burned', 0.0))
        
        # Insert or update
        log_entry = ProgressLog.query.filter_by(profile_id=profile_id, log_date=log_date).first()
        if log_entry:
            log_entry.weight = weight
            log_entry.water_intake = water_intake
            log_entry.sleep_hours = sleep_hours
            log_entry.calories_consumed = calories_consumed
            log_entry.calories_burned = calories_burned
        else:
            log_entry = ProgressLog(
                profile_id=profile_id,
                log_date=log_date,
                weight=weight,
                water_intake=water_intake,
                sleep_hours=sleep_hours,
                calories_consumed=calories_consumed,
                calories_burned=calories_burned
            )
            db.session.add(log_entry)
            
        db.session.commit()
        return jsonify({"message": "Progress metrics successfully logged!"}), 200
        
    except ValueError:
        return jsonify({"error": "Measurements must be valid numeric values"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/progress/<int:profile_id>', methods=['GET'])
@login_required
def get_progress(profile_id):
    # Ownership Check
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Access denied"}), 403
        
    logs = ProgressLog.query.filter_by(profile_id=profile_id).order_by(ProgressLog.log_date.asc()).all()
    logs_data = []
    for log in logs:
        logs_data.append({
            "log_date": log.log_date,
            "weight": log.weight,
            "water_intake": log.water_intake,
            "sleep_hours": log.sleep_hours,
            "calories_consumed": log.calories_consumed,
            "calories_burned": log.calories_burned
        })
    return jsonify(logs_data), 200

@api_bp.route('/feedback', methods=['POST'])
@login_required
def log_feedback():
    data = request.json
    if not data or 'profile_id' not in data or 'rating' not in data:
        return jsonify({"error": "Missing profile_id or rating parameters"}), 400
        
    profile_id = int(data['profile_id'])
    
    # Ownership Check
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Access denied"}), 403
        
    try:
        rating = int(data['rating'])
        comments = str(data.get('comments', '')).strip()
        log_date = datetime.today().strftime('%Y-%m-%d')
        
        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
            
        new_feedback = Feedback(
            profile_id=profile_id,
            rating=rating,
            comments=comments,
            log_date=log_date
        )
        db.session.add(new_feedback)
        db.session.commit()
        
        return jsonify({"message": "Feedback review saved!"}), 200
        
    except ValueError:
        return jsonify({"error": "Rating must be an integer"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/feedback/<int:profile_id>', methods=['GET'])
@login_required
def get_feedback(profile_id):
    # Ownership Check
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first()
    if not profile:
        return jsonify({"error": "Access denied"}), 403
        
    reviews = Feedback.query.filter_by(profile_id=profile_id).order_by(Feedback.created_at.desc()).all()
    reviews_data = []
    for r in reviews:
        reviews_data.append({
            "rating": r.rating,
            "comments": r.comments,
            "log_date": r.log_date
        })
    return jsonify(reviews_data), 200

@api_bp.route('/test-results', methods=['GET'])
def get_test_results():
    # Serve the test results summary markdown file
    try:
        # Prefer root-level summary if present, otherwise fall back to reports/test_results.md
        candidate_paths = ['test_results_summary.md', os.path.join('reports', 'test_results.md')]
        content = None
        for p in candidate_paths:
            if os.path.exists(p):
                with open(p, 'r', encoding='utf-8') as f:
                    content = f.read()
                break

        if content is None:
            return jsonify({"error": "Test results file not found"}), 404

        return jsonify({"content": content}), 200
    except FileNotFoundError:
        return jsonify({"error": "Test results file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
