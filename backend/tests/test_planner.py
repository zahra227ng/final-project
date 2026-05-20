import json

def test_get_tasks_empty(client, auth_headers):
    response = client.get('/api/tasks', headers=auth_headers)
    assert response.status_code == 200
    assert len(response.get_json()) == 0

def test_create_task_success(client, auth_headers):
    response = client.post('/api/tasks', headers=auth_headers, json={
        'title': 'Test Assignment',
        'description': 'Write code walkthroughs',
        'due_date': '2026-06-30',
        'subject': 'Software Engineering',
        'estimated_pomodoros': 3
    })
    data = response.get_json()
    assert response.status_code == 201
    assert data['title'] == 'Test Assignment'
    assert data['subject'] == 'Software Engineering'
    assert data['estimated_pomodoros'] == 3
    assert data['status'] == 'pending'

def test_create_task_missing_title(client, auth_headers):
    response = client.post('/api/tasks', headers=auth_headers, json={
        'due_date': '2026-06-30'
    })
    assert response.status_code == 400

def test_create_task_invalid_date(client, auth_headers):
    response = client.post('/api/tasks', headers=auth_headers, json={
        'title': 'Bad Date Task',
        'due_date': '30-06-2026' # WRONG FORMAT
    })
    assert response.status_code == 400
    assert 'YYYY-MM-DD' in response.get_json()['message']

def test_update_task_completed_logs_study(client, auth_headers):
    # 1. Create a task
    create_response = client.post('/api/tasks', headers=auth_headers, json={
        'title': 'Study Calculus',
        'subject': 'Math',
        'estimated_pomodoros': 2
    })
    task_id = create_response.get_json()['id']
    
    # 2. Update task status to completed
    update_response = client.put(f'/api/tasks/{task_id}', headers=auth_headers, json={
        'status': 'completed',
        'completed_pomodoros': 2
    })
    assert update_response.status_code == 200
    assert update_response.get_json()['status'] == 'completed'
    
    # 3. Verify that a study log was automatically created for Math (2 Pomodoros = 50 mins)
    analytics_response = client.get('/api/ai/analytics', headers=auth_headers)
    analytics = analytics_response.get_json()
    assert analytics['total_minutes'] == 50
    assert analytics['subject_breakdown']['Math'] == 50

def test_delete_task_success(client, auth_headers):
    # Create task
    create_response = client.post('/api/tasks', headers=auth_headers, json={
        'title': 'Delete Me'
    })
    task_id = create_response.get_json()['id']
    
    # Delete task
    delete_response = client.delete(f'/api/tasks/{task_id}', headers=auth_headers)
    assert delete_response.status_code == 200
    
    # Verify gone
    get_response = client.get('/api/tasks', headers=auth_headers)
    assert len(get_response.get_json()) == 0
