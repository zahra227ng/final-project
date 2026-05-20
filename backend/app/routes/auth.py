from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, date
import jwt
from functools import wraps
from app.models import db, User

auth_bp = Blueprint('auth', __name__)
JWT_SECRET = 'ai-study-buddy-secret-key-12345' # Standard secret key for university project

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Authorization token is missing!'}), 401
        
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # Exception Handling: Input Validation
    if not username or not email or not password:
        return jsonify({'message': 'Username, email, and password are required.'}), 400
        
    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters long.'}), 400
        
    # Check duplicate
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists.'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered.'}), 400
        
    try:
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Create token
        token = jwt.encode(
            {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(days=7)},
            JWT_SECRET,
            algorithm='HS256'
        )
        
        return jsonify({
            'message': 'Registration successful.',
            'token': token,
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Database error occurred: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    
    # Exception Handling: Input Validation
    if not email or not password:
        return jsonify({'message': 'Email and password are required.'}), 400
        
    try:
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({'message': 'Invalid email or password.'}), 401
            
        # Update streak logic
        today_date = date.today()
        if user.last_active:
            delta = today_date - user.last_active
            if delta.days == 1:
                # Studied yesterday, increment streak
                user.streak += 1
            elif delta.days > 1:
                # Missed a day, reset streak
                user.streak = 1 # reset and start new streak
            # If delta.days == 0 (today), keep the streak as is
        else:
            # First active day
            user.streak = 1
            
        user.last_active = today_date
        db.session.commit()
        
        token = jwt.encode(
            {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(days=7)},
            JWT_SECRET,
            algorithm='HS256'
        )
        
        return jsonify({
            'token': token,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
    # Proactively check and update streak on profile refresh
    today_date = date.today()
    if current_user.last_active:
        delta = today_date - current_user.last_active
        if delta.days > 1:
            current_user.streak = 0
            db.session.commit()
            
    return jsonify(current_user.to_dict()), 200

@auth_bp.route('/update_goal', methods=['PUT'])
@token_required
def update_goal(current_user):
    data = request.get_json() or {}
    goal = data.get('daily_goal_minutes')
    
    if not goal or not isinstance(goal, int) or goal <= 0:
        return jsonify({'message': 'Invalid daily goal value.'}), 400
        
    try:
        current_user.daily_goal_minutes = goal
        db.session.commit()
        return jsonify({
            'message': 'Daily study goal updated.',
            'user': current_user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Database error: {str(e)}'}), 500
