import pytest
from app import create_app
from app.models import db, User

@pytest.fixture
def app():
    app = create_app()
    # Override configuration to use in-memory SQLite database for testing
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(username='teststudent', email='student@test.edu')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Reload user from DB
        db.session.refresh(user)
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'password': 'password123'
        }

@pytest.fixture
def auth_headers(client, test_user):
    response = client.post('/api/auth/login', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    token = response.get_json()['token']
    return {
        'Authorization': f'Bearer {token}'
    }
