import os
import jwt
import requests
from datetime import datetime, date, timedelta
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)

# Config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'ai_analytics.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
JWT_SECRET = "study-buddy-super-secret-key-2026"

AUTH_SERVICE_URL = "http://127.0.0.1:5001"
PLANNER_SERVICE_URL = "http://127.0.0.1:5002"
QUIZ_SERVICE_URL = "http://127.0.0.1:5003"

db = SQLAlchemy(app)

# Models
class StudyLog(db.Model):
    __tablename__ = 'study_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False) # Associated by ID
    subject = db.Column(db.String(50), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    activity_type = db.Column(db.String(50), default='pomodoro') # pomodoro, quiz, chat, task_completion
    date = db.Column(db.Date, default=date.today)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'duration_minutes': self.duration_minutes,
            'activity_type': self.activity_type,
            'date': self.date.isoformat()
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

# Helper to fetch user profiles internally from Auth Service
def get_user_profile(user_id):
    try:
        resp = requests.get(f"{AUTH_SERVICE_URL}/users/{user_id}", timeout=2)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Error fetching user profile: {e}")
    return {'id': user_id, 'streak': 0, 'daily_goal_minutes': 60, 'last_active': None, 'username': 'Student'}

# Helper to update user streak internally in Auth Service
def update_user_streak(user_id, today_date, current_streak, last_active_str):
    try:
        # Compute next streak
        new_streak = current_streak
        if last_active_str:
            last_active = date.fromisoformat(last_active_str)
            delta = today_date - last_active
            if delta.days == 1:
                new_streak += 1
            elif delta.days > 1:
                new_streak = 1
        else:
            new_streak = 1
            
        requests.put(
            f"{AUTH_SERVICE_URL}/users/{user_id}/streak",
            json={
                'streak': new_streak,
                'last_active': today_date.isoformat()
            },
            timeout=2
        )
    except Exception as e:
        print(f"Failed to update user streak in Auth microservice: {e}")

# Endpoints
@app.route('/study_log', methods=['POST'])
def add_study_log():
    # Supports both JWT-authenticated client and internal service calls
    current_user_id = None
    
    if 'Authorization' in request.headers:
        token = request.headers['Authorization'].split(' ')[1]
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user_id = data['user_id']
        except Exception:
            return jsonify({'message': 'Invalid Token.'}), 401
            
    data = request.get_json() or {}
    if not current_user_id:
        current_user_id = data.get('user_id')
        
    if not current_user_id:
        return jsonify({'message': 'User ID is missing.'}), 400
        
    subject = data.get('subject')
    duration = data.get('duration_minutes')
    activity = data.get('activity_type', 'pomodoro')
    
    if not subject or not duration:
        return jsonify({'message': 'Subject and duration_minutes are required.'}), 400
        
    try:
        log = StudyLog(
            user_id=current_user_id,
            subject=subject,
            duration_minutes=int(duration),
            activity_type=activity,
            date=date.today()
        )
        db.session.add(log)
        db.session.commit()
        
        # Resiliently update user streak in Auth microservice
        user_info = get_user_profile(current_user_id)
        update_user_streak(
            current_user_id,
            date.today(),
            user_info['streak'],
            user_info['last_active']
        )
        
        return jsonify(log.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/recommendations', methods=['GET'])
@token_required
def get_recommendations(current_user_id):
    # Fetch data internally from other microservices
    user_info = get_user_profile(current_user_id)
    streak = user_info['streak']
    
    tasks = []
    try:
        t_resp = requests.get(f"{PLANNER_SERVICE_URL}/users/{current_user_id}/tasks", timeout=2)
        if t_resp.status_code == 200:
            tasks = t_resp.json()
    except Exception:
        pass
        
    quizzes = []
    try:
        q_resp = requests.get(f"{QUIZ_SERVICE_URL}/users/{current_user_id}/quizzes", timeout=2)
        if q_resp.status_code == 200:
            quizzes = q_resp.json()
    except Exception:
        pass

    # Compile Rules
    recommendations = []
    
    if streak == 0:
        recommendations.append({
            "category": "Streak",
            "title": "Start Your Streak!",
            "suggestion": "Study for at least 25 minutes (1 Pomodoro session) today to kickstart your daily streak!",
            "priority": "high"
        })
    elif streak < 3:
        recommendations.append({
            "category": "Streak",
            "title": "Keep the Momentum!",
            "suggestion": f"You are on a {streak}-day streak. Log a study session today to maintain it!",
            "priority": "medium"
        })
    else:
        recommendations.append({
            "category": "Streak",
            "title": "Unstoppable! 🔥",
            "suggestion": f"Impressive {streak}-day study streak! Complete a custom quiz today to show off your knowledge.",
            "priority": "low"
        })
        
    pending_tasks = [t for t in tasks if t['status'] != 'completed']
    if len(pending_tasks) > 0:
        urgent_task = pending_tasks[0]
        recommendations.append({
            "category": "Planner",
            "title": "Next Deadline Focus",
            "suggestion": f"Spend your next session on: '{urgent_task['title']}' for {urgent_task['subject']}.",
            "priority": "high"
        })
    else:
        recommendations.append({
            "category": "Planner",
            "title": "All Tasks Caught Up!",
            "suggestion": "You have no pending tasks. Take some time to brainstorm next week's assignments or take a quiz.",
            "priority": "low"
        })
        
    if len(quizzes) == 0:
        recommendations.append({
            "category": "Practice",
            "title": "Try Active Recall",
            "suggestion": "You haven't taken any mock quizzes yet. Generate a test on Software Engineering to check your skills!",
            "priority": "medium"
        })
    else:
        avg_score = sum(q['score'] for q in quizzes if q['score'] is not None) / len(quizzes) if len(quizzes) > 0 else 0
        if avg_score < 3:
            recommendations.append({
                "category": "Practice",
                "title": "Review Quiz Concepts",
                "suggestion": "Your average quiz performance is below 60%. Try checking tutoring chat logs to study weaker subjects.",
                "priority": "high"
            })
            
    return jsonify(recommendations), 200

@app.route('/analytics', methods=['GET'])
@token_required
def get_analytics(current_user_id):
    # Fetch user properties from Auth
    user_info = get_user_profile(current_user_id)
    streak = user_info['streak']
    daily_goal = user_info['daily_goal_minutes']
    
    # Query logs
    today_date = date.today()
    logs = StudyLog.query.filter_by(user_id=current_user_id).all()
    
    total_minutes = sum(l.duration_minutes for l in logs)
    today_minutes = sum(l.duration_minutes for l in logs if l.date == today_date)
    
    # Subject breakdown
    subject_breakdown = {}
    for l in logs:
        subject_breakdown[l.subject] = subject_breakdown.get(l.subject, 0) + l.duration_minutes
        
    # Activity breakdown
    activity_breakdown = {}
    for l in logs:
        activity_breakdown[l.activity_type] = activity_breakdown.get(l.activity_type, 0) + l.duration_minutes
        
    # Weekly breakdown (last 7 days)
    history_breakdown = {}
    for i in range(6, -1, -1):
        day = today_date - timedelta(days=i)
        day_str = day.strftime('%a') # Mon, Tue...
        day_mins = sum(l.duration_minutes for l in logs if l.date == day)
        history_breakdown[day_str] = day_mins
        
    # Quiz stats fetched internally
    quizzes = []
    try:
        q_resp = requests.get(f"{QUIZ_SERVICE_URL}/users/{current_user_id}/quizzes", timeout=2)
        if q_resp.status_code == 200:
            quizzes = q_resp.json()
    except Exception:
        pass
        
    completed_quizzes = [q for q in quizzes if q['score'] is not None]
    avg_score = 0
    if len(completed_quizzes) > 0:
        avg_score = Math_round_score = sum(round((q['score']/q['total_questions'])*100) for q in completed_quizzes) / len(completed_quizzes)
        
    quiz_subjects = {}
    for q in completed_quizzes:
        pct = (q['score']/q['total_questions']) * 100
        if q['subject'] not in quiz_subjects:
            quiz_subjects[q['subject']] = []
        quiz_subjects[q['subject']].append(pct)
        
    quiz_subject_averages = {sub: sum(scores)/len(scores) for sub, scores in quiz_subjects.items()}
    
    return jsonify({
        'streak': streak,
        'daily_goal': daily_goal,
        'total_minutes': total_minutes,
        'today_minutes': today_minutes,
        'goal_reached': today_minutes >= daily_goal,
        'subject_breakdown': subject_breakdown,
        'activity_breakdown': activity_breakdown,
        'history_breakdown': history_breakdown,
        'quiz_stats': {
            'taken_count': len(quizzes),
            'average_score': round(avg_score, 1),
            'subject_averages': quiz_subject_averages
        }
    }), 200

# Local AI Chatbot Keywords Catalog
CHAT_RESPONSES = {
    "hello": "Hello! I am your AI Study Buddy Chatbot. 🤖 How can I help you study today?",
    "study": "The best way to study is using **Active Recall** (testing yourself with flashcards or quizzes) and **Spaced Repetition** (reviewing concepts over expanding intervals). Try taking a mock quiz!",
    "pomodoro": "The **Pomodoro Technique** involves studying with complete focus for 25 minutes, followed by a 5-minute break. This keeps your brain active and prevents fatigue.",
    "feynman": "The **Feynman Technique** involves explaining a complex concept in your own simple words, as if teaching a child. This quickly highlights gaps in your understanding.",
    "lehman": "Lehman's Laws of Software Evolution describe how software systems grow. The **Law of Continuing Change** states that a system must adapt or become progressively less useful. The **Law of Increasing Complexity** states that structure decays unless refactored.",
    "complexity": "Time complexity (Big O) represents how execution time scales with input size. For example, O(1) is constant, O(log n) is logarithmic, O(n) is linear, and O(n^2) is quadratic.",
    "agile": "The **Agile Methodology** breaks project management into iterative sprint cycles. Focus shifts from heavy upfront plan designs to customer review feedback loops and adaptive testing.",
    "scrum": "Scrum is an Agile framework. It involves roles like the **Scrum Master** and **Product Owner**, events like **Sprint Planning** and **Daily Standups**, and artifacts like the **Sprint Backlog**."
}

@app.route('/chat', methods=['POST'])
@token_required
def chat(current_user_id):
    data = request.get_json() or {}
    msg = data.get('message', '').strip()
    if not msg:
        return jsonify({'message': 'Message is required.'}), 400
        
    # Match keywords
    query_lower = msg.lower()
    bot_reply = f"That is a great question about **'{msg}'**! Try searching for this concept in your study materials or generating an AI Quiz to test your skills."
    
    for key, response in CHAT_RESPONSES.items():
        if key in query_lower:
            bot_reply = response
            break
            
    # Resiliently log a 1-minute study credit for chatbot usage
    try:
        log = StudyLog(
            user_id=current_user_id,
            subject='General',
            duration_minutes=1,
            activity_type='chat',
            date=date.today()
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Resilient chat logging failed: {e}")
        
    return jsonify({'response': bot_reply}), 200

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=5004, debug=True)
