from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config


def create_app():
    app = Flask(__name__, static_folder='../static')
    
    # Enable CORS for all routes
    CORS(app)

    app.config.from_object(Config)

    from app.routes import status, login, profile, logout, attendance, timetable, present, absent, results, end_semester_results, academic_analysis

    app.register_blueprint(status.bp)
    app.register_blueprint(login.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(logout.bp)
    app.register_blueprint(attendance.bp)
    app.register_blueprint(timetable.bp)
    app.register_blueprint(present.bp)
    app.register_blueprint(absent.bp)
    app.register_blueprint(results.bp)
    app.register_blueprint(end_semester_results.bp)
    app.register_blueprint(academic_analysis.bp)

    # Add route for web interface
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return send_from_directory(app.static_folder, 'index.html')

    return app
