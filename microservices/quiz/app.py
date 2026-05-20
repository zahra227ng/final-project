import os
import jwt
import requests
import random
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'quiz.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
JWT_SECRET = "study-buddy-super-secret-key-2026"
AI_SERVICE_URL = "http://127.0.0.1:5004"

db = SQLAlchemy(app)

# Models
class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False) # Associated by ID
    title = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    questions = db.Column(db.JSON, nullable=False) # Questions array
    score = db.Column(db.Integer, nullable=True) # Null until submitted
    total_questions = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'subject': self.subject,
            'questions': self.questions,
            'score': self.score,
            'total_questions': self.total_questions,
            'created_at': self.created_at.isoformat()
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

# Local Questions Catalog (Rule-based simulation)
QUIZ_BANK = {
    "Computer Science": [
        {"question": "What is the time complexity to search an element in a balanced Binary Search Tree?", "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"], "correct": 1, "explanation": "A balanced BST splits search spaces in half at each step, yielding logarithmic search complexity."},
        {"question": "Which protocol works at the Transport Layer of the OSI Model?", "options": ["HTTP", "IP", "TCP", "DNS"], "correct": 2, "explanation": "TCP and UDP are Transport Layer protocols. HTTP is Application and IP is Network."},
        {"question": "What does CPU stand for?", "options": ["Central Processing Unit", "Control Program Utility", "Computer Processor Unit", "Common Peripheral Unit"], "correct": 0, "explanation": "CPU stands for Central Processing Unit, the main chip executing instructions."},
        {"question": "What is the base of the Hexadecimal number system?", "options": ["2", "8", "10", "16"], "correct": 3, "explanation": "Hexadecimal uses 16 digits (0-9 and A-F)."},
        {"question": "Which data structure operates on a Last In First Out (LIFO) model?", "options": ["Queue", "Stack", "Linked List", "Tree"], "correct": 1, "explanation": "Stacks place newly inserted elements on top, retrieving them first (LIFO)."}
    ],
    "Software Engineering": [
        {"question": "What is the primary objective of the Agile methodology?", "options": ["Rigid documentation", "Iterative progress & customer collaboration", "Fixed project planning", "Sequential design verification"], "correct": 1, "explanation": "Agile prioritizes customer feedback, adaptable sprint planning, and iterative releases."},
        {"question": "In Git, what does 'checkout' do?", "options": ["Deletes a branch", "Pushes commits", "Switches branches or restores files", "Merges modifications"], "correct": 2, "explanation": "Git checkout updates files in the working directory to match the target branch."},
        {"question": "Which phase of Scrum defines sprint goals?", "options": ["Daily Standup", "Sprint Planning", "Retrospective", "Review"], "correct": 1, "explanation": "Sprint Planning brings developers and product owners together to establish the backlog goals."},
        {"question": "What is clean code Refactoring?", "options": ["Adding new features", "Modifying internal code structure without changing external behavior", "Writing unit tests", "Compiling package files"], "correct": 1, "explanation": "Refactoring improves readability and decreases complexity without altering logic output."},
        {"question": "What does CI/CD stand for?", "options": ["Continuous Integration / Continuous Deployment", "Code Inspection / Compiler Design", "Central Instance / Control Deck", "Configuration Item / Change Delivery"], "correct": 0, "explanation": "CI/CD automates code integration checks and production delivery processes."}
    ],
    "Math": [
        {"question": "What is the derivative of x^2 with respect to x?", "options": ["x", "2", "2x", "x^3 / 3"], "correct": 2, "explanation": "By the calculus power rule, d/dx(x^n) = n*x^(n-1). So d/dx(x^2) = 2x."},
        {"question": "What is the value of the mathematical constant e to 2 decimal places?", "options": ["3.14", "2.72", "1.62", "1.41"], "correct": 1, "explanation": "e is approximately 2.71828, which rounds to 2.72."},
        {"question": "Which of the following matrices is invertible?", "options": ["Determinant is 0", "Determinant is non-zero", "All diagonal entries are 0", "Identity columns are identical"], "correct": 1, "explanation": "A matrix is invertible if and only if its determinant is not equal to zero."},
        {"question": "What is the integral of 1/x dx?", "options": ["x", "ln|x| + C", "-1/x^2 + C", "e^x + C"], "correct": 1, "explanation": "The anti-derivative of 1/x is the natural log of the absolute value of x."},
        {"question": "What does a correlation coefficient of -1 indicate?", "options": ["No relation", "Strong positive correlation", "Strong negative correlation", "Independent variables"], "correct": 2, "explanation": "-1 indicates a perfect linear negative relationship."}
    ]
}

def generate_local_quiz(subject, topic=None):
    bank = QUIZ_BANK.get(subject, QUIZ_BANK["Computer Science"])
    questions = list(bank)
    random.shuffle(questions)
    
    selected_questions = questions[:5]
    title = f"{subject} Quiz" if not topic else f"{subject} ({topic}) Quiz"
    
    return {
        "title": title,
        "subject": subject,
        "questions": selected_questions,
        "total_questions": len(selected_questions)
    }

# Routes
@app.route('/quiz/generate', methods=['POST'])
@token_required
def generate(current_user_id):
    data = request.get_json() or {}
    subject = data.get('subject')
    topic = data.get('topic')

    if not subject:
        return jsonify({'message': 'Subject is required.'}), 400

    quiz_data = generate_local_quiz(subject, topic)

    try:
        quiz = Quiz(
            user_id=current_user_id,
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
        return jsonify({'message': str(e)}), 500

@app.route('/quiz/submit', methods=['POST'])
@token_required
def submit(current_user_id):
    data = request.get_json() or {}
    quiz_id = data.get('quiz_id')
    answers = data.get('answers', []) # Array of integer indices

    if not quiz_id or not isinstance(answers, list):
        return jsonify({'message': 'Quiz ID and answers array are required.'}), 400

    quiz = Quiz.query.filter_by(id=quiz_id, user_id=current_user_id).first()
    if not quiz:
        return jsonify({'message': 'Quiz not found.'}), 404

    # Evaluate Score
    score = 0
    details = []
    
    for idx, q in enumerate(quiz.questions):
        user_ans = answers[idx] if idx < len(answers) else -1
        correct_ans = q['correct']
        is_correct = (user_ans == correct_ans)
        
        if is_correct:
            score += 1
            
        details.append({
            'question': q['question'],
            'user_answer': q['options'][user_ans] if user_ans != -1 else 'No Answer',
            'correct_answer': q['options'][correct_ans],
            'is_correct': is_correct,
            'explanation': q['explanation']
        })

    try:
        quiz.score = score
        db.session.commit()

        # Resilient internal call to log study session (Quizzes yield 15 mins)
        try:
            requests.post(
                f"{AI_SERVICE_URL}/study_log",
                json={
                    'user_id': current_user_id,
                    'subject': quiz.subject,
                    'duration_minutes': 15,
                    'activity_type': 'quiz'
                },
                timeout=2
            )
        except Exception as service_err:
            print(f"Resilient fallback: failed to call AI Service for quiz study log: {service_err}")

        return jsonify({
            'quiz_id': quiz.id,
            'score': score,
            'total_questions': quiz.total_questions,
            'details': details
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/quiz/history', methods=['GET'])
@token_required
def get_history(current_user_id):
    quizzes = Quiz.query.filter_by(user_id=current_user_id).order_by(Quiz.created_at.desc()).all()
    return jsonify([q.to_dict() for q in quizzes]), 200

# Inter-service GET endpoint to fetch user quizzes for AI Service recommendation logic
@app.route('/users/<int:user_id>/quizzes', methods=['GET'])
def get_user_quizzes_internal(user_id):
    quizzes = Quiz.query.filter_by(user_id=user_id).all()
    return jsonify([q.to_dict() for q in quizzes]), 200

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=5003, debug=True)
