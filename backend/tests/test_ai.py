from app.models import db, User

def test_chat_success(client, auth_headers):
    # Test Greeting Keyword
    response_greet = client.post('/api/ai/chat', headers=auth_headers, json={
        'message': 'Hello, buddy!'
    })
    assert response_greet.status_code == 200
    assert 'AI Study Buddy Chatbot' in response_greet.get_json()['response']

    # Test Focus Keyword
    response_focus = client.post('/api/ai/chat', headers=auth_headers, json={
        'message': 'How to improve my focus?'
    })
    assert response_focus.status_code == 200
    assert 'Pomodoro' in response_focus.get_json()['response']
    
    # Test Fallback default response
    response_fallback = client.post('/api/ai/chat', headers=auth_headers, json={
        'message': 'Tell me about cellular mitosis.'
    })
    assert response_fallback.status_code == 200
    assert 'mitosis' in response_fallback.get_json()['response']

def test_chat_missing_message(client, auth_headers):
    response = client.post('/api/ai/chat', headers=auth_headers, json={})
    assert response.status_code == 400

def test_recommendations_streak_0(app, client, auth_headers):
    # Set streak back to 0 (login automatically sets it to 1)
    with app.app_context():
        user = User.query.filter_by(username='teststudent').first()
        user.streak = 0
        db.session.commit()

    # For a new user with 0 streak and no tasks
    response = client.get('/api/ai/recommendations', headers=auth_headers)
    assert response.status_code == 200
    recs = response.get_json()
    
    # Must contain "Start Your Streak!" card
    streak_card = [r for r in recs if r['category'] == 'Streak']
    assert len(streak_card) == 1
    assert 'Start Your Streak!' in streak_card[0]['title']
    assert streak_card[0]['priority'] == 'high'

