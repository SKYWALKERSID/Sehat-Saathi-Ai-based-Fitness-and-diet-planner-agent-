from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Render main onboarding and dashboard SPA
    return render_template('dashboard.html', profiles=current_user.profiles)

@main_bp.route('/analytics')
@login_required
def analytics():
    # Render the detailed analytics reports page
    return render_template('analytics.html', profiles=current_user.profiles)
