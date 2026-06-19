from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

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
    fitness_goal = db.Column(db.String(50), nullable=False)
    activity_level = db.Column(db.String(50), nullable=False)
    diet_preference = db.Column(db.String(50), nullable=False)
    water_intake = db.Column(db.Float, nullable=False) # L
    sleep_hours = db.Column(db.Float, nullable=False) # Hours
    workout_experience = db.Column(db.String(50), nullable=False)
    
    medical_conditions = db.Column(db.Text, default='None')
    injuries = db.Column(db.Text, default='None')
    allergies = db.Column(db.Text, default='None')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Calculated metrics
    bmi = db.Column(db.Float, nullable=False)
    bmi_category = db.Column(db.String(50), nullable=False)
    bmr = db.Column(db.Float, nullable=False)
    tdee = db.Column(db.Float, nullable=False)
    target_calories = db.Column(db.Float, nullable=False)
    target_protein = db.Column(db.Float, nullable=False)
    target_carbs = db.Column(db.Float, nullable=False)
    target_fat = db.Column(db.Float, nullable=False)
    confidence_score = db.Column(db.Integer, nullable=False)
    
    advisory_notes = db.Column(db.Text, default='[]')      # JSON array representation
    diet_meals_json = db.Column(db.Text, nullable=False)    # Raw JSON of meal outputs
    workout_plan_json = db.Column(db.Text, nullable=False)  # Raw JSON of workouts week program
    
    # Relationships
    progress_logs = db.relationship('ProgressLog', backref='profile', lazy=True, cascade="all, delete-orphan")
    feedbacks = db.relationship('Feedback', backref='profile', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Profile {self.name} of UserID {self.user_id}>'

class ProgressLog(db.Model):
    __tablename__ = 'progress_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    log_date = db.Column(db.String(10), nullable=False) # YYYY-MM-DD
    weight = db.Column(db.Float, nullable=False)
    water_intake = db.Column(db.Float, nullable=False)
    sleep_hours = db.Column(db.Float, nullable=False)
    calories_consumed = db.Column(db.Float, default=0.0)
    calories_burned = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure profile only has one log per day
    __table_args__ = (db.UniqueConstraint('profile_id', 'log_date', name='uq_profile_day'),)

    def __repr__(self):
        return f'<ProgressLog {self.log_date} for ProfileID {self.profile_id}>'

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text, default='')
    log_date = db.Column(db.String(10), nullable=False) # YYYY-MM-DD
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Feedback Rating {self.rating} for ProfileID {self.profile_id}>'
