import json

def test_register_success(client):
    response = client.post('/api/auth/register', json={
        'username': 'newstudent',
        'email': 'new@test.edu',
        'password': 'securepassword'
    })
    data = response.get_json()
    assert response.status_code == 201
    assert 'token' in data
    assert data['user']['username'] == 'newstudent'

def test_register_missing_fields(client):
    response = client.post('/api/auth/register', json={
        'username': 'newstudent'
    })
    assert response.status_code == 400
    assert 'message' in response.get_json()

def test_register_password_too_short(client):
    response = client.post('/api/auth/register', json={
        'username': 'shortstudent',
        'email': 'short@test.edu',
        'password': '123'
    })
    assert response.status_code == 400
    assert 'at least 6 characters' in response.get_json()['message']

def test_register_duplicate(client, test_user):
    response = client.post('/api/auth/register', json={
        'username': test_user['username'],
        'email': 'another@test.edu',
        'password': 'password123'
    })
    assert response.status_code == 400
    assert 'Username already exists' in response.get_json()['message']

def test_login_success(client, test_user):
    response = client.post('/api/auth/login', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    data = response.get_json()
    assert response.status_code == 200
    assert 'token' in data
    assert data['user']['username'] == test_user['username']

def test_login_invalid_password(client, test_user):
    response = client.post('/api/auth/login', json={
        'email': test_user['email'],
        'password': 'wrongpassword'
    })
    assert response.status_code == 401

def test_profile_success(client, auth_headers):
    response = client.get('/api/auth/profile', headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()['username'] == 'teststudent'

def test_profile_unauthorized(client):
    response = client.get('/api/auth/profile')
    assert response.status_code == 401
