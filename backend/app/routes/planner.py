from flask import Blueprint, request, jsonify
from datetime import datetime, date
from app.models import db, Task, StudyLog
from app.routes.auth import token_required

planner_bp = Blueprint('planner', __name__)

@planner_bp.route('/tasks', methods=['GET'])
@token_required
def get_tasks(current_user):
    try:
        tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date.asc()).all()
        return jsonify([t.to_dict() for t in tasks]), 200
    except Exception as e:
        return jsonify({'message': f'Database error: {str(e)}'}), 500

@planner_bp.route('/tasks', methods=['POST'])
@token_required
def create_task(current_user):
    data = request.get_json() or {}
    title = data.get('title')
    description = data.get('description', '')
    due_date_str = data.get('due_date')
    subject = data.get('subject', 'General')
    estimated_pomodoros = data.get('estimated_pomodoros', 1)
    
    # Validation
    if not title:
        return jsonify({'message': 'Task title is required.'}), 400
        
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format. Expected YYYY-MM-DD.'}), 400
            
    try:
        task = Task(
            user_id=current_user.id,
            title=title,
            description=description,
            due_date=due_date,
            subject=subject,
            estimated_pomodoros=estimated_pomodoros,
            completed_pomodoros=0,
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Database error: {str(e)}'}), 500

@planner_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(current_user, task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({'message': 'Task not found.'}), 404
            
        data = request.get_json() or {}
        
        # Track if status is transitioning to completed
        old_status = task.status
        
        if 'title' in data:
            if not data['title']:
                return jsonify({'message': 'Task title cannot be empty.'}), 400
            task.title = data['title']
            
        if 'description' in data:
            task.description = data['description']
            
        if 'due_date' in data:
            due_date_str = data['due_date']
            if due_date_str:
                try:
                    task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'message': 'Invalid date format. Expected YYYY-MM-DD.'}), 400
            else:
                task.due_date = None
                
        if 'subject' in data:
            task.subject = data['subject']
            
        if 'estimated_pomodoros' in data:
            task.estimated_pomodoros = int(data['estimated_pomodoros'])
            
        if 'completed_pomodoros' in data:
            task.completed_pomodoros = int(data['completed_pomodoros'])
            
        if 'status' in data:
            new_status = data['status']
            if new_status not in ['pending', 'in-progress', 'completed']:
                return jsonify({'message': 'Invalid status. Must be pending, in-progress, or completed.'}), 400
            task.status = new_status
            
            # If transitioned to completed, automatically log study session (e.g. 25 mins per Pomodoro completed)
            if old_status != 'completed' and new_status == 'completed':
                mins_studied = max(task.completed_pomodoros, 1) * 25
                study_log = StudyLog(
                    user_id=current_user.id,
                    subject=task.subject or 'General',
                    duration_minutes=mins_studied,
                    activity_type='pomodoro',
                    date=date.today()
                )
                db.session.add(study_log)
                
                # Check streak update
                today_date = date.today()
                if current_user.last_active:
                    delta = today_date - current_user.last_active
                    if delta.days == 1:
                        current_user.streak += 1
                    elif delta.days > 1:
                        current_user.streak = 1
                else:
                    current_user.streak = 1
                current_user.last_active = today_date
                
        db.session.commit()
        return jsonify(task.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Database error: {str(e)}'}), 500

@planner_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user, task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({'message': 'Task not found.'}), 404
            
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Database error: {str(e)}'}), 500
