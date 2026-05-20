import os
import jwt
import bcrypt
from datetime import datetime, timedelta, date
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'auth.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
JWT_SECRET = "study-buddy-super-secret-key-2026"

db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    streak = db.Column(db.Integer, default=0)
    last_active = db.Column(db.Date, nullable=True)
    daily_goal_minutes = db.Column(db.Integer, default=60)

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'streak': self.streak,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'daily_goal_minutes': self.daily_goal_minutes
        }

# JWT Helper Decorator
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

# Endpoints
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Username, email, and password are required.'}), 400

    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters.'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists.'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists.'}), 400

    try:
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(days=7)}, JWT_SECRET, algorithm='HS256')
        return jsonify({'message': 'Registration successful.', 'token': token, 'user': user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required.'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password.'}), 401

    try:
        # Streak Check
        today_date = date.today()
        if user.last_active:
            delta = today_date - user.last_active
            if delta.days == 1:
                user.streak += 1
            elif delta.days > 1:
                user.streak = 1
        else:
            user.streak = 1
            
        user.last_active = today_date
        db.session.commit()

        token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(days=7)}, JWT_SECRET, algorithm='HS256')
        return jsonify({'message': 'Login successful.', 'token': token, 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user_id):
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'message': 'User not found.'}), 404
    return jsonify(user.to_dict()), 200

# Inter-service GET endpoint to fetch user properties
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_internal(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found.'}), 404
    return jsonify(user.to_dict()), 200

# Inter-service PUT endpoint to update user streak (called by AI Service when studying)
@app.route('/users/<int:user_id>/streak', methods=['PUT'])
def update_streak_internal(user_id):
    data = request.get_json() or {}
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found.'}), 404

    try:
        if 'streak' in data:
            user.streak = data['streak']
        if 'last_active' in data:
            user.last_active = date.fromisoformat(data['last_active'])
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# Endpoint to update user daily goal
@app.route('/profile/goal', methods=['PUT'])
@token_required
def update_goal(current_user_id):
    data = request.get_json() or {}
    goal = data.get('daily_goal_minutes')
    
    if not goal or not isinstance(goal, int) or goal < 5:
        return jsonify({'message': 'Goal must be a number representing minutes (minimum 5).'}), 400

    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'message': 'User not found.'}), 404

    try:
        user.daily_goal_minutes = goal
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=5001, debug=True)
