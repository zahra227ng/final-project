import os
from flask import Flask, send_from_directory
from app.models import db

def create_app():
    # Setup paths relative to backend/app folder
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend'))
    
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    
    # Configure database (SQLite db file stored in backend folder)
    backend_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(backend_dir, 'ai_study_buddy.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.planner import planner_bp
    from app.routes.quiz import quiz_bp
    from app.routes.ai import ai_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(planner_bp, url_prefix='/api')  # Register directly to /api so tasks are under /api/tasks
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    
    # CORS Header configuration
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Catch-all routes to serve SPA static files
    @app.route('/')
    def serve_index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
            
    with app.app_context():
        db.create_all()
        
    return app
