print("Git push test")
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "alphanex-demo-secret-key-for-session-management-2025")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database - use PostgreSQL for production and multi-user support
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///alphanex.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_timeout": 20,
    "pool_size": 10,
    "max_overflow": 20,
    "connect_args": {"connect_timeout": 10, "application_name": "alphanex"}
}

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'name_entry'
login_manager.login_message = None  # Disable login required messages
login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))


# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize scheduler for automated tasks
scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

with app.app_context():
    # Import models to ensure tables are created
    import models  # noqa: F401
    import routes  # noqa: F401

    try:
        db.create_all()
    except Exception as e:
        app.logger.error(f"Database initialization error: {e}")
        # Continue running even if DB init fails

# Add error handlers to prevent 502 gateway errors
@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Internal server error: {e}")
    return "Internal server error occurred. Please try again.", 500

@app.errorhandler(502)
def bad_gateway(e):
    app.logger.error(f"Bad gateway error: {e}")
    return "Service temporarily unavailable. Please try again.", 502

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {e}")
    return "An unexpected error occurred. Please try again.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
