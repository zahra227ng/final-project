from flask import Blueprint, request, jsonify
from datetime import date, timedelta
from sqlalchemy import func
from app.models import db, Task, Quiz, StudyLog
from app.routes.auth import token_required
from app.services.ai_engine import AIEngine

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/chat', methods=['POST'])
@token_required
def chat(current_user):
    data = request.get_json() or {}
    message = data.get('message')
    
    if not message:
        return jsonify({'message': 'Message is required.'}), 400
        
    try:
        response = AIEngine.get_chat_response(message)
        
        # Save a mini study log for chatting (e.g. 5 minutes of study effort)
        log = StudyLog(
            user_id=current_user.id,
            subject='General',
            duration_minutes=5,
            activity_type='chat',
            date=date.today()
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': message,
            'response': response
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@ai_bp.route('/recommendations', methods=['GET'])
@token_required
def get_recommendations(current_user):
    try:
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        study_logs = StudyLog.query.filter_by(user_id=current_user.id).all()
        
        recommendations = AIEngine.get_recommendations(tasks, study_logs, current_user.streak)
        return jsonify(recommendations), 200
    except Exception as e:
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@ai_bp.route('/analytics', methods=['GET'])
@token_required
def get_analytics(current_user):
    try:
        # 1. Total minutes studied
        total_minutes = db.session.query(func.sum(StudyLog.duration_minutes))\
            .filter(StudyLog.user_id == current_user.id).scalar() or 0
            
        # 2. Today's minutes studied (for daily goals progress)
        today_minutes = db.session.query(func.sum(StudyLog.duration_minutes))\
            .filter(StudyLog.user_id == current_user.id, StudyLog.date == date.today()).scalar() or 0
            
        # 3. Subject-wise breakdown (minutes)
        subject_data = db.session.query(StudyLog.subject, func.sum(StudyLog.duration_minutes))\
            .filter(StudyLog.user_id == current_user.id)\
            .group_by(StudyLog.subject).all()
        subject_breakdown = {subject: mins for subject, mins in subject_data}
        
        # 4. Activity-type breakdown (minutes)
        activity_data = db.session.query(StudyLog.activity_type, func.sum(StudyLog.duration_minutes))\
            .filter(StudyLog.user_id == current_user.id)\
            .group_by(StudyLog.activity_type).all()
        activity_breakdown = {act: mins for act, mins in activity_data}
        
        # 5. Last 7 days study progress history (for line charts)
        history_breakdown = {}
        for i in range(6, -1, -1):
            day = date.today() - timedelta(days=i)
            day_str = day.strftime('%a') # Mon, Tue, etc.
            day_mins = db.session.query(func.sum(StudyLog.duration_minutes))\
                .filter(StudyLog.user_id == current_user.id, StudyLog.date == day).scalar() or 0
            history_breakdown[day_str] = day_mins
            
        # 6. Quiz stats
        quizzes_taken = Quiz.query.filter(Quiz.user_id == current_user.id, Quiz.score != None).all()
        total_quizzes = len(quizzes_taken)
        avg_score = 0
        if total_quizzes > 0:
            avg_score = sum((q.score / q.total_questions) * 100 for q in quizzes_taken) / total_quizzes
            
        # Subject-wise quiz average scores
        quiz_subject_scores = {}
        for q in quizzes_taken:
            if q.subject not in quiz_subject_scores:
                quiz_subject_scores[q.subject] = []
            quiz_subject_scores[q.subject].append((q.score / q.total_questions) * 100)
            
        avg_quiz_subject_scores = {
            subject: sum(scores) / len(scores) for subject, scores in quiz_subject_scores.items()
        }
        
        # 7. Goals status
        goal_reached = today_minutes >= current_user.daily_goal_minutes
        
        return jsonify({
            'total_minutes': total_minutes,
            'today_minutes': today_minutes,
            'daily_goal': current_user.daily_goal_minutes,
            'goal_reached': goal_reached,
            'streak': current_user.streak,
            'subject_breakdown': subject_breakdown,
            'activity_breakdown': activity_breakdown,
            'history_breakdown': history_breakdown,
            'quiz_stats': {
                'total_quizzes': total_quizzes,
                'average_score': round(avg_score, 1),
                'subject_averages': {s: round(v, 1) for s, v in avg_quiz_subject_scores.items()}
            }
        }), 200
    except Exception as e:
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@ai_bp.route('/study_log', methods=['POST'])
@token_required
def add_study_log(current_user):
    """
    Explicitly logs a custom study session (e.g. from the Pomodoro focus timer).
    """
    data = request.get_json() or {}
    subject = data.get('subject', 'General')
    duration_minutes = data.get('duration_minutes')
    activity_type = data.get('activity_type', 'pomodoro')
    
    if not duration_minutes or not isinstance(duration_minutes, int) or duration_minutes <= 0:
        return jsonify({'message': 'Duration minutes is required and must be positive.'}), 400
        
    try:
        log = StudyLog(
            user_id=current_user.id,
            subject=subject,
            duration_minutes=duration_minutes,
            activity_type=activity_type,
            date=date.today()
        )
        db.session.add(log)
        
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
        return jsonify(log.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Database error: {str(e)}'}), 500
