from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch profiles associated with the logged-in user
    profiles = current_user.profiles
    return render_template('dashboard.html', profiles=profiles)


@main_bp.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')


@main_bp.route('/terms-and-conditions')
def terms_and_conditions():
    return render_template('terms_and_conditions.html')
