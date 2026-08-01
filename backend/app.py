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
from routes.exports import export_bp      # async CSV export routes
from routes.reports import report_bp      # async report generation routes

from database.seed import seed_admin


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── Create required directories ───────────────────────────────
    os.makedirs(app.config['UPLOAD_FOLDER'],  exist_ok=True)
    os.makedirs(app.config['EXPORTS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(app.config['DB_FILE'])
    os.makedirs(db_dir, exist_ok=True)

    # ── CORS ──────────────────────────────────────────────────────
    CORS(app, resources={r'/api/*': {'origins': app.config['CORS_ORIGINS']}},
         supports_credentials=True)

    # ── Initialize extensions ─────────────────────────────────────
    db.init_app(app)
    JWTManager(app)

    # ── Register blueprints (all API routes) ──────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(export_bp)    # POST /api/admin/export/...
    app.register_blueprint(report_bp)    # POST /api/admin/reports/...

    # ── Error handlers ────────────────────────────────────────────
    from exceptions import PlacementError

    @app.errorhandler(PlacementError)
    def handle_placement_error(e):
        return jsonify({'error': e.message}), e.status_code

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

    # ── Health check ──────────────────────────────────────────────
    @app.route('/api/health', methods=['GET'])
    def health_check():
        from cache import cache
        return jsonify({
            'status': 'ok',
            'message': 'Placement Portal API is running',
            'redis_cache': 'connected' if cache.is_available else 'unavailable (caching disabled)',
        }), 200

    # ── Create tables and seed admin user ─────────────────────────
    with app.app_context():
        db.create_all()
        try:
            from sqlalchemy import text
            db.session.execute(text("ALTER TABLE applications ADD COLUMN resume_path VARCHAR(256)"))
            db.session.commit()
        except Exception:
            db.session.rollback()
        seed_admin()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
