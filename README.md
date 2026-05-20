Implementation Plan — AI Study Buddy Semester Project (Flask + HTML/CSS/JS)
Create a complete semester project called “AI Study Buddy”, a modern, interactive, and AI-powered study assistant application designed to help students improve productivity, focus, and study management. This project is structured specifically for a Software Construction & Development university course.

User Review Required
IMPORTANT

Tech Stack Adjustment: Since Node.js/NPM is not installed in the current environment but Python 3.13 is available, we will use Flask for the backend, PyTest for testing, and a highly polished Vanilla HTML/CSS/JS SPA architecture for the frontend. This runs natively without requiring any compilation or bundlers.

Database Choice: We will use SQLite through SQLAlchemy. This is a relational database matching MySQL semantics, but is fully self-contained as a local file, making it ready to run out of the box for grading.

AI Features: The AI recommendations, chatbot responses, and quiz generation will be implemented using a local AI simulation engine with pre-trained rules and semantic logic, ensuring the app is fully functional and interactive without requiring paid API keys.

Proposed Changes & Architecture
The project will be organized in a monorepo structure:

backend/ - Flask server, SQLAlchemy database models, REST API, PyTest suite.
frontend/ - Modern Vanilla HTML/CSS/JS web interface with responsive layouts, charts, and animations.
docs/ - Comprehensive software engineering documentation (Agile process, SPI, Lehman's laws, refactoring report, user guide, etc.)
legacy_demo/ - Demo of poorly structured code to satisfy the refactoring requirement
Folder Structure

final-project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── planner.py
│   │   │   ├── quiz.py
│   │   │   └── ai.py
│   │   └── services/
│   │       └── ai_engine.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_planner.py
│   │   ├── test_quiz.py
│   │   └── test_ai.py
│   ├── run.py
│   └── requirements.txt
├── frontend/
│   ├── assets/
│   │   └── logo.png
│   ├── css/
│   │   ├── variables.css
│   │   ├── app.css
│   │   └── components.css
│   ├── js/
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── dashboard.js
│   │   ├── planner.js
│   │   ├── quiz.js
│   │   ├── pomodoro.js
│   │   └── chatbot.js
│   └── index.html
├── docs/
│   ├── final_report.md
│   ├── presentation_outline.md
│   ├── agile_scrum_details.md
│   └── testing_report.md
├── legacy_demo/
│   ├── spaghetti_app_bad.py
│   └── refactoring_explanation.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── README.md
└── requirements.txt (root workspace)
Database Schema (SQLite / Relational)
Users Table
id (UUID or Integer, PK)
username (VARCHAR, Unique, Nullable=false)
email (VARCHAR, Unique, Nullable=false)
password (VARCHAR, Hash, Nullable=false)
streak (INTEGER, Default=0)
last_active (DATE)
daily_goal_minutes (INTEGER, Default=60)
created_at / updated_at
Tasks Table (Planner)
id (UUID or Integer, PK)
user_id (FK -> Users.id)
title (VARCHAR, Nullable=false)
description (TEXT)
due_date (DATE)
subject (VARCHAR)
estimated_pomodoros (INTEGER, Default=1)
completed_pomodoros (INTEGER, Default=0)
status (ENUM/VARCHAR: 'pending', 'in-progress', 'completed')
created_at / updated_at
Quizzes Table
id (UUID or Integer, PK)
user_id (FK -> Users.id)
title (VARCHAR, Nullable=false)
subject (VARCHAR)
questions (JSON text containing array of questions, options, and correct answers)
score (INTEGER, Nullable)
total_questions (INTEGER)
created_at / updated_at
StudyLogs Table (Analytics & Focus tracking)
id (UUID or Integer, PK)
user_id (FK -> Users.id)
subject (VARCHAR, Nullable=false)
duration_minutes (INTEGER, Nullable=false)
activity_type (VARCHAR: 'pomodoro', 'quiz', 'chat', 'reading')
date (DATE, Default=CURRENT_DATE)
created_at / updated_at
API Endpoints
Authentication
POST /api/auth/register - Register a new student
POST /api/auth/login - Login and return JWT token
GET /api/auth/profile - Get user profile and current streak status
Planner
GET /api/tasks - Get student task list
POST /api/tasks - Create a new task
PUT /api/tasks/<id> - Update status, title, description, or Pomodoro count
DELETE /api/tasks/<id> - Delete a task
Quiz Generator
POST /api/quiz/generate - Generate a quiz using local AI rules based on notes/topics
POST /api/quiz/submit - Save quiz attempts, scores, and track analytics
AI Assistant & Recommendations
POST /api/ai/chat - Chatbot for answering study questions
GET /api/ai/recommendations - Retrieve personalized study suggestions based on current tasks, completion history, and performance analytics
Verification Plan
Automated Tests
Run backend unit and integration tests using pytest inside the backend directory.
Test authentication validation, quiz generation structure, tasks CRUD, and AI recommendation rules.
Set up a GitHub Actions workflow .github/workflows/ci.yml that runs linting and PyTest on every push.
Manual Verification
Verify the responsive dark/light UI in various browser viewport sizes.
Verify Pomodoro audio alerts, page transitions, and interactive quiz interfaces.
Verify session persistent state across reloads.
