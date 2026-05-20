import json

def test_generate_quiz_success(client, auth_headers):
    response = client.post('/api/quiz/generate', headers=auth_headers, json={
        'subject': 'Software Engineering',
        'topic': 'Agile Methodology'
    })
    data = response.get_json()
    assert response.status_code == 201
    assert 'title' in data
    assert len(data['questions']) == 5
    assert 'question' in data['questions'][0]
    assert len(data['questions'][0]['options']) == 4

def test_generate_quiz_missing_subject(client, auth_headers):
    response = client.post('/api/quiz/generate', headers=auth_headers, json={
        'topic': 'Feynman'
    })
    assert response.status_code == 400

def test_submit_quiz_success(client, auth_headers):
    # 1. Generate Quiz
    gen_response = client.post('/api/quiz/generate', headers=auth_headers, json={
        'subject': 'Math'
    })
    quiz = gen_response.get_json()
    quiz_id = quiz['id']
    
    # 2. Extract correct answers to achieve 100% score
    correct_answers = [q['correct'] for q in quiz['questions']]
    
    # 3. Submit quiz
    sub_response = client.post('/api/quiz/submit', headers=auth_headers, json={
        'quiz_id': quiz_id,
        'answers': correct_answers
    })
    data = sub_response.get_json()
    assert sub_response.status_code == 200
    assert data['score'] == 5
    assert data['total_questions'] == 5
    assert data['details'][0]['is_correct'] is True
    
    # 4. Verify study logs updated (Quiz yields 15 minutes of study effort)
    history_response = client.get('/api/quiz/history', headers=auth_headers)
    assert len(history_response.get_json()) == 1
    
    analytics_response = client.get('/api/ai/analytics', headers=auth_headers)
    assert analytics_response.get_json()['total_minutes'] == 15
