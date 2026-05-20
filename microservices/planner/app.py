import os
import jwt
import requests
from datetime import datetime, date
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'planner.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
JWT_SECRET = "study-buddy-super-secret-key-2026"
AI_SERVICE_URL = "http://127.0.0.1:5004"

db = SQLAlchemy(app)

# Models
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False) # Associated by ID
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    subject = db.Column(db.String(50), default='General')
    estimated_pomodoros = db.Column(db.Integer, default=1)
    completed_pomodoros = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending') # pending, completed

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'subject': self.subject,
            'estimated_pomodoros': self.estimated_pomodoros,
            'completed_pomodoros': self.completed_pomodoros,
            'status': self.status
        }

# JWT helper
def token_required(f):
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Authorization token is missing.'}), 401
            
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user_id = data['user_id']
        except Exception:
            return jsonify({'message': 'Invalid or expired authorization token.'}), 401
            
        return f(current_user_id, *args, **kwargs)
    decorator.__name__ = f.__name__
    return decorator

# Routes
@app.route('/tasks', methods=['GET'])
@token_required
def get_tasks(current_user_id):
    tasks = Task.query.filter_by(user_id=current_user_id).all()
    return jsonify([t.to_dict() for t in tasks]), 200

@app.route('/tasks', methods=['POST'])
@token_required
def create_task(current_user_id):
    data = request.get_json() or {}
    title = data.get('title')
    description = data.get('description')
    due_date_str = data.get('due_date')
    subject = data.get('subject', 'General')
    estimated_pomodoros = data.get('estimated_pomodoros', 1)
    
    if not title:
        return jsonify({'message': 'Task title is required.'}), 400
        
    due_date = None
    if due_date_str:
        try:
            due_date = date.fromisoformat(due_date_str)
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400
            
    try:
        task = Task(
            user_id=current_user_id,
            title=title,
            description=description,
            due_date=due_date,
            subject=subject,
            estimated_pomodoros=estimated_pomodoros,
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(current_user_id, task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    if not task:
        return jsonify({'message': 'Task not found.'}), 404
        
    data = request.get_json() or {}
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'due_date' in data:
        due_date_str = data['due_date']
        if due_date_str:
            try:
                task.due_date = date.fromisoformat(due_date_str)
            except ValueError:
                return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD.'}), 400
        else:
            task.due_date = None
            
    if 'subject' in data:
        task.subject = data['subject']
    if 'estimated_pomodoros' in data:
        task.estimated_pomodoros = int(data['estimated_pomodoros'])
    if 'completed_pomodoros' in data:
        task.completed_pomodoros = int(data['completed_pomodoros'])
        
    trigger_completion_log = False
    if 'status' in data:
        new_status = data['status']
        if new_status == 'completed' and task.status != 'completed':
            trigger_completion_log = True
        task.status = new_status
        
    try:
        db.session.commit()
        
        # Resilient internal call to log study session upon task completion
        if trigger_completion_log:
            try:
                duration = max(task.estimated_pomodoros * 25, 25)
                # Call AI service endpoint to record study log
                requests.post(
                    f"{AI_SERVICE_URL}/study_log",
                    json={
                        'user_id': current_user_id,
                        'subject': task.subject,
                        'duration_minutes': duration,
                        'activity_type': 'task_completion'
                    },
                    timeout=2
                )
            except Exception as service_err:
                # Log warning but do not fail the request (resiliency)
                print(f"Resilient fallback: failed to call AI Service for study log: {service_err}")
                
        return jsonify(task.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user_id, task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    if not task:
        return jsonify({'message': 'Task not found.'}), 404
        
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# Inter-service GET endpoint to fetch tasks list count for AI Service recommendation logic
@app.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks_internal(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([t.to_dict() for t in tasks]), 200

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=5002, debug=True)
