"""
Sehat Saathi Backend Application Factory
Flask app is created here using the Application Factory pattern.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, jsonify, request
from flask_login import LoginManager
from database.db import db
from config import Config

login_manager = LoginManager()


def create_app(config_class=Config):
    """
    Application Factory: creates and configures the Flask app instance.
    Templates live in /templates, static assets in /static.
    """
    # BASE_DIR = project root (one level up from this file)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static'),
        static_url_path='/static'
    )
    app.config.from_object(config_class)

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    # Import models to register them with SQLAlchemy before create_all
    import database.models

    # Create all DB tables on first run
    with app.app_context():
        db.create_all()

    # User Loader
    from database.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from backend.auth.routes import auth_bp
    from backend.profiles.routes import profiles_bp
    from backend.analytics.routes import analytics_bp
    from backend.chatbot.routes import chatbot_bp
    from backend.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(main_bp)

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Resource not found"}), 404
        return render_template('base.html', error_code=404,
                               error_message="The page you requested could not be found."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"Server Error: {str(e)}")
        if request.path.startswith('/api/'):
            return jsonify({"error": "Internal server error"}), 500
        return render_template('base.html', error_code=500,
                               error_message="An internal server error occurred. Please try again later."), 500

    # Logging Setup
    _setup_logging(app)

    return app


def _setup_logging(app):
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'aura_fit.log'),
        maxBytes=10240,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Sehat Saathi startup complete.')
