from flask import Blueprint, request, jsonify
from datetime import date
from app.models import db, Quiz, StudyLog
from app.routes.auth import token_required
from app.services.ai_engine import AIEngine

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/generate', methods=['POST'])
@token_required
def generate_quiz(current_user):
    data = request.get_json() or {}
    subject = data.get('subject')
    topic = data.get('topic')
    
    if not subject:
        return jsonify({'message': 'Subject is required to generate a quiz.'}), 400
        
    try:
        # Generate using our local AI Engine
        quiz_data = AIEngine.generate_quiz(subject, topic)
        
        # Save quiz details to DB
        quiz = Quiz(
            user_id=current_user.id,
            title=quiz_data['title'],
            subject=quiz_data['subject'],
            questions=quiz_data['questions'],
            total_questions=quiz_data['total_questions']
        )
        db.session.add(quiz)
        db.session.commit()
        
        return jsonify(quiz.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@quiz_bp.route('/submit', methods=['POST'])
@token_required
def submit_quiz(current_user):
    data = request.get_json() or {}
    quiz_id = data.get('quiz_id')
    user_answers = data.get('answers') # List of indices
    
    if not quiz_id or user_answers is None:
        return jsonify({'message': 'Quiz ID and answers are required.'}), 400
        
    try:
        quiz = Quiz.query.filter_by(id=quiz_id, user_id=current_user.id).first()
        if not quiz:
            return jsonify({'message': 'Quiz not found.'}), 404
            
        questions = quiz.questions
        if len(user_answers) != len(questions):
            return jsonify({'message': 'Incomplete quiz answers.'}), 400
            
        correct_count = 0
        details = []
        
        for idx, question in enumerate(questions):
            correct_idx = question['correct']
            user_idx = user_answers[idx]
            is_correct = (user_idx == correct_idx)
            if is_correct:
                correct_count += 1
                
            details.append({
                'question': question['question'],
                'user_answer': question['options'][user_idx] if user_idx is not None and user_idx >= 0 and user_idx < len(question['options']) else 'None',
                'correct_answer': question['options'][correct_idx],
                'is_correct': is_correct,
                'explanation': question['explanation']
            })
            
        # Update Quiz score
        quiz.score = correct_count
        
        # Log study session for taking the quiz (average duration = 15 minutes)
        study_log = StudyLog(
            user_id=current_user.id,
            subject=quiz.subject or 'General',
            duration_minutes=15,
            activity_type='quiz',
            date=date.today()
        )
        db.session.add(study_log)
        
        # Update Streak
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
        
        return jsonify({
            'quiz_id': quiz.id,
            'title': quiz.title,
            'subject': quiz.subject,
            'score': correct_count,
            'total_questions': quiz.total_questions,
            'details': details
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@quiz_bp.route('/history', methods=['GET'])
@token_required
def get_quiz_history(current_user):
    try:
        quizzes = Quiz.query.filter_by(user_id=current_user.id).order_by(Quiz.created_at.desc()).all()
        return jsonify([q.to_dict() for q in quizzes]), 200
    except Exception as e:
        return jsonify({'message': f'Database error: {str(e)}'}), 500
