import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from models import db
from models.user import User
from models.student import Student
from models.company import Company
from models.placement_drive import PlacementDrive
from models.application import Application
from models.interview import Interview
from models.result import Result

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.company import company_bp
from routes.student import student_bp

from database.seed import seed_admin


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # create database folder if it doesn't exist
    db_dir = os.path.dirname(app.config['DB_FILE'])
    os.makedirs(db_dir, exist_ok=True)

    # setup CORS so frontend can connect to backend
    CORS(app, resources={r'/api/*': {'origins': app.config['CORS_ORIGINS']}},
         supports_credentials=True)

    # initialize extensions
    db.init_app(app)
    JWTManager(app)

    # register all blueprints (routes)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    # simple error handlers
    @app.errorhandler(404)
    def not_found_error(e):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed_error(e):
        return jsonify({'error': 'Method not allowed'}), 405

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    # health check endpoint - useful for testing if server is running
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok', 'message': 'Placement Portal API is running'}), 200

    # create tables and seed initial data inside app context
    with app.app_context():
        db.create_all()
        seed_admin()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
