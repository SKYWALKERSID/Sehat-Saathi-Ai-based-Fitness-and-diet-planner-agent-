from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship: A user can have multiple profiles
    profiles = db.relationship('Profile', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    height = db.Column(db.Float, nullable=False) # cm
    weight = db.Column(db.Float, nullable=False) # kg
    fitness_goal = db.Column(db.String(100), nullable=False)
    activity_level = db.Column(db.String(50), nullable=False)
    diet_preference = db.Column(db.String(50), nullable=False)
    water_intake = db.Column(db.Float, nullable=False) # L
    sleep_hours = db.Column(db.Float, nullable=False) # Hours
    workout_experience = db.Column(db.String(50), nullable=False)
    medical_conditions = db.Column(db.Text, default='None')
    injuries = db.Column(db.Text, default='None')
    allergies = db.Column(db.Text, default='None')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    goals = db.relationship('FitnessGoals', backref='profile', uselist=False, lazy=True, cascade="all, delete-orphan")
    workout_plans = db.relationship('WorkoutPlans', backref='profile', lazy=True, cascade="all, delete-orphan")
    diet_plans = db.relationship('DietPlans', backref='profile', lazy=True, cascade="all, delete-orphan")
    nutrition_logs = db.relationship('NutritionLogs', backref='profile', lazy=True, cascade="all, delete-orphan")
    progress_tracks = db.relationship('ProgressTracking', backref='profile', lazy=True, cascade="all, delete-orphan")
    health_metrics = db.relationship('HealthMetrics', backref='profile', lazy=True, cascade="all, delete-orphan")
    mcp_logs = db.relationship('MCPLogs', backref='profile', lazy=True, cascade="all, delete-orphan")
    recommendations = db.relationship('Recommendations', backref='profile', lazy=True, cascade="all, delete-orphan")
    hydration_records = db.relationship('HydrationRecords', backref='profile', lazy=True, cascade="all, delete-orphan")
    feedbacks = db.relationship('Feedback', backref='profile', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Profile {self.name} (UserID {self.user_id})>'

class FitnessGoals(db.Model):
    __tablename__ = 'fitness_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    bmi_category = db.Column(db.String(50), nullable=False)
    bmr = db.Column(db.Float, nullable=False)
    tdee = db.Column(db.Float, nullable=False)
    target_calories = db.Column(db.Float, nullable=False)
    target_protein = db.Column(db.Float, nullable=False)
    target_carbs = db.Column(db.Float, nullable=False)
    target_fat = db.Column(db.Float, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    advisory_notes = db.Column(db.Text, default='[]') # JSON array of notes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WorkoutPlans(db.Model):
    __tablename__ = 'workout_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    day_of_week = db.Column(db.String(15), nullable=False)
    exercises = db.Column(db.Text, nullable=False) # JSON array of exercises
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DietPlans(db.Model):
    __tablename__ = 'diet_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    meal_type = db.Column(db.String(30), nullable=False) # Breakfast, Lunch, Snack, Dinner
    food_items = db.Column(db.Text, nullable=False) # JSON array of foods
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbohydrates = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NutritionLogs(db.Model):
    __tablename__ = 'nutrition_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    log_date = db.Column(db.String(10), nullable=False) # YYYY-MM-DD
    food_name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    quantity_g = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProgressTracking(db.Model):
    __tablename__ = 'progress_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    log_date = db.Column(db.String(10), nullable=False) # YYYY-MM-DD
    weight = db.Column(db.Float, nullable=False)
    water_intake = db.Column(db.Float, nullable=False)
    sleep_hours = db.Column(db.Float, nullable=False)
    calories_consumed = db.Column(db.Float, default=0.0)
    calories_burned = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('profile_id', 'log_date', name='uq_profile_progress_day'),)

class HealthMetrics(db.Model):
    __tablename__ = 'health_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    log_date = db.Column(db.String(10), nullable=False) # YYYY-MM-DD
    blood_pressure = db.Column(db.String(15)) # e.g. "120/80"
    heart_rate = db.Column(db.Integer) # bpm
    blood_sugar = db.Column(db.Float) # mg/dL
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MCPLogs(db.Model):
    __tablename__ = 'mcp_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=True) # Can be null if global lookup
    mcp_name = db.Column(db.String(50), nullable=False)
    tool_name = db.Column(db.String(50), nullable=False)
    input_params = db.Column(db.Text) # JSON string
    output_data = db.Column(db.Text) # JSON/text output
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Recommendations(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    model_name = db.Column(db.String(50), nullable=False)
    inputs = db.Column(db.Text) # JSON string
    outputs = db.Column(db.Text) # JSON string
    score = db.Column(db.Float) # Confidence or recommendation score
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WeatherHistory(db.Model):
    __tablename__ = 'weather_history'
    
    id = db.Column(db.Integer, primary_key=True)
    log_date = db.Column(db.String(10), nullable=False, unique=True) # YYYY-MM-DD
    temp_c = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    air_quality = db.Column(db.String(30), nullable=False)
    condition = db.Column(db.String(50), nullable=False) # Hot, Cold, Rain, Moderate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HydrationRecords(db.Model):
    __tablename__ = 'hydration_records'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    log_date = db.Column(db.String(10), nullable=False) # YYYY-MM-DD
    target_l = db.Column(db.Float, nullable=False)
    consumed_l = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('profile_id', 'log_date', name='uq_profile_hydration_day'),)

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text, default='')
    log_date = db.Column(db.String(10), nullable=False) # YYYY-MM-DD
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
