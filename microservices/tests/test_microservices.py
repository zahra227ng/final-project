import os
import sys
import subprocess
import time
import requests
import pytest

SERVICES = [
    {"name": "auth", "path": "microservices/auth/app.py"},
    {"name": "planner", "path": "microservices/planner/app.py"},
    {"name": "quiz", "path": "microservices/quiz/app.py"},
    {"name": "ai", "path": "microservices/ai/app.py"},
    {"name": "gateway", "path": "microservices/gateway/app.py"}
]

DB_PATHS = [
    "microservices/auth/auth.db",
    "microservices/planner/planner.db",
    "microservices/quiz/quiz.db",
    "microservices/ai/ai_analytics.db"
]

@pytest.fixture(scope="module")
def setup_services():
    # Clean old test DBs for a fresh start
    for path in DB_PATHS:
        abs_p = os.path.abspath(path)
        if os.path.exists(abs_p):
            try:
                os.remove(abs_p)
            except Exception:
                pass
                
    python_bin = sys.executable
    processes = []
    
    # Launch services
    for s in SERVICES:
        abs_path = os.path.abspath(s["path"])
        dir_name = os.path.dirname(abs_path)
        p = subprocess.Popen(
            [python_bin, abs_path],
            cwd=dir_name,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        processes.append(p)
        time.sleep(1.0) # wait for start

    # Wait extra time for the gateway and internal services to list ports
    time.sleep(3.0)
    
    yield
    
    # Teardown: terminate all processes
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=3)
        except Exception:
            p.kill()

    # Clean test DBs
    for path in DB_PATHS:
        abs_p = os.path.abspath(path)
        if os.path.exists(abs_p):
            try:
                os.remove(abs_p)
            except Exception:
                pass

def test_integration_flow(setup_services):
    gateway_url = "http://127.0.0.1:5000/api"
    
    # 1. Register User
    reg_resp = requests.post(f"{gateway_url}/auth/register", json={
        "username": "integrator",
        "email": "integration@test.edu",
        "password": "securepassword123"
    })
    assert reg_resp.status_code == 201
    data = reg_resp.json()
    token = data["token"]
    assert token is not None

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Profile
    prof_resp = requests.get(f"{gateway_url}/auth/profile", headers=headers)
    assert prof_resp.status_code == 200
    assert prof_resp.json()["username"] == "integrator"

    # 3. Create Task
    task_resp = requests.post(f"{gateway_url}/tasks", json={
        "title": "Complete Microservices Assignment",
        "subject": "Software Engineering",
        "estimated_pomodoros": 2
    }, headers=headers)
    assert task_resp.status_code == 201
    task = task_resp.json()
    task_id = task["id"]
    assert task["status"] == "pending"

    # 4. Complete Task (triggers inter-service study log logging)
    complete_resp = requests.put(f"{gateway_url}/tasks/{task_id}", json={
        "status": "completed"
    }, headers=headers)
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == "completed"

    # Sleep briefly to ensure the inter-service call finishes writing to SQLite
    time.sleep(1.0)

    # 5. Generate Practice Quiz
    quiz_resp = requests.post(f"{gateway_url}/quiz/generate", json={
        "subject": "Software Engineering"
    }, headers=headers)
    assert quiz_resp.status_code == 201
    quiz = quiz_resp.json()
    quiz_id = quiz["id"]
    assert len(quiz["questions"]) == 5

    # 6. Submit Quiz Answers (triggers 15 mins study logging)
    submit_resp = requests.post(f"{gateway_url}/quiz/submit", json={
        "quiz_id": quiz_id,
        "answers": [1, 2, 1, 1, 0] # simulated student selections
    }, headers=headers)
    assert submit_resp.status_code == 200
    assert "score" in submit_resp.json()

    # Sleep for inter-service call
    time.sleep(1.0)

    # 7. AI Chatbot interaction (triggers 1 min study logging)
    chat_resp = requests.post(f"{gateway_url}/ai/chat", json={
        "message": "tell me about Scrum"
    }, headers=headers)
    assert chat_resp.status_code == 200
    assert "Scrum is an Agile framework" in chat_resp.json()["response"]

    # Sleep for logging write
    time.sleep(1.0)

    # 8. Check AI Study recommendations
    recs_resp = requests.get(f"{gateway_url}/ai/recommendations", headers=headers)
    assert recs_resp.status_code == 200
    recs = recs_resp.json()
    assert len(recs) > 0

    # 9. Verify Aggregated Analytics
    # Total minutes should be = 50 (from task completion) + 15 (from quiz) + 1 (from chat) = 66 minutes
    analytics_resp = requests.get(f"{gateway_url}/ai/analytics", headers=headers)
    assert analytics_resp.status_code == 200
    stats = analytics_resp.json()
    assert stats["total_minutes"] >= 66
    assert stats["streak"] >= 1
    assert stats["quiz_stats"]["taken_count"] == 1
