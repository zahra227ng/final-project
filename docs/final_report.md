# Software Engineering Project Report: AI Study Buddy

## 1. Project Overview

The **AI Study Buddy** is a web-based educational productivity application designed to optimize student focus, self-evaluation, and material synthesis. Grounded in established cognitive science and pedagogical techniques—specifically the **Pomodoro Technique** for temporal focus management, the **Feynman Technique** for concept articulation, and **Active Recall** for practice evaluation—the system aims to replace fragmented student tools with a unified, data-driven dashboard.

### Core Objectives
*   **Time Management**: Facilitate session-based work intervals with a customized Pomodoro timer linked directly to academic tasks.
*   **Active Recall**: Generate mock examinations on-demand to test student comprehension.
*   **Tutoring & Articulation**: Provide a conversational chatbot assistant using the Feynman Technique to help students explain complex ideas in simple terms.
*   **Aggregated Analytics**: Log all study activities to track completion statistics, streak records, and personalized study habits.

---

## 2. Monolithic Backend Structure

The monolithic backend is constructed using **Python 3.13** and the **Flask** microframework. It operates as a stateless RESTful JSON API.

### App Factory Pattern
The application uses the factory design pattern inside [backend/app/__init__.py](file:///d:/final-project/backend/app/__init__.py). This structure decouples app configuration from initialization, allowing clean environment swaps between test and production states.

### Modular Blueprint Routing
The endpoint controller layers are divided into distinct Blueprints:
*   `auth_bp` ([backend/app/routes/auth.py](file:///d:/final-project/backend/app/routes/auth.py)): User registration, logins, JWT signing, profile queries, and streak tracking.
*   `planner_bp` ([backend/app/routes/planner.py](file:///d:/final-project/backend/app/routes/planner.py)): Task creation, status updates, deletions, and task completion logging triggers.
*   `quiz_bp` ([backend/app/routes/quiz.py](file:///d:/final-project/backend/app/routes/quiz.py)): Interface for quiz generation delegator and answer submission evaluation.
*   `ai_bp` ([backend/app/routes/ai.py](file:///d:/final-project/backend/app/routes/ai.py)): AI Chat bot endpoint, study log insertions, study recommendations engine, and dashboard analytics compilations.

---

## 3. Frontend Architecture

The frontend is implemented as a lightweight **Single-Page Application (SPA)** written in semantic HTML5, vanilla CSS, and vanilla ES6 JavaScript. The interface is responsive, styled with glassmorphism visual designs, smooth micro-animations, and dynamic visual graphs.

### Code Organization
*   [frontend/index.html](file:///d:/final-project/frontend/index.html): Central application layout, viewport sections, and modal panels.
*   [frontend/index.css](file:///d:/final-project/frontend/index.css): Core design system tokens (variables, HSL palettes, transitions) and responsive layout rules.
*   [frontend/app/api.js](file:///d:/final-project/frontend/app/api.js): Centralized API caller client handling Bearer JWT headers and error mapping.
*   [frontend/app/auth.js](file:///d:/final-project/frontend/app/auth.js): Login/Registration states, profile bindings, and LocalStorage JWT caching.
*   [frontend/app/planner.js](file:///d:/final-project/frontend/app/planner.js): Task list managers, status toggles, and Pomodoro integrations.
*   [frontend/app/pomodoro.js](file:///d:/final-project/frontend/app/pomodoro.js): Timer loop, browser tab notification chimes, and auto-logging requests.
*   [frontend/app/quiz.js](file:///d:/final-project/frontend/app/quiz.js): Dynamic quiz builder, interactive question flow, and scoring feedback.
*   [frontend/app/chatbot.js](file:///d:/final-project/frontend/app/chatbot.js): Chat history management and quick feynman technique tutoring chips.
*   [frontend/app/analytics.js](file:///d:/final-project/frontend/app/analytics.js): Analytics rendering and dynamic recommendation panels.

---

## 4. Database Schema Design

The monolithic application utilizes **SQLite** for relational storage, accessed via the **SQLAlchemy ORM** interface. The database file `ai_study_buddy.db` is stored locally.

### Models and Fields
1.  **User (`users` table)**:
    *   `id` (Integer, Primary Key)
    *   `username` (String, Unique, Indexed)
    *   `email` (String, Unique, Indexed)
    *   `password_hash` (String, password security)
    *   `streak` (Integer, tracking consecutive days active)
    *   `last_active` (Date, daily calculation parameter)
    *   `daily_goal_minutes` (Integer, default 60)
2.  **Task (`tasks` table)**:
    *   `id` (Integer, Primary Key)
    *   `user_id` (Integer, Foreign Key $\rightarrow$ `users.id`)
    *   `title` (String, Not Null)
    *   `description` (String)
    *   `due_date` (Date)
    *   `subject` (String)
    *   `estimated_pomodoros` (Integer)
    *   `completed_pomodoros` (Integer)
    *   `status` (String: `pending`, `completed`)
3.  **Quiz (`quizzes` table)**:
    *   `id` (Integer, Primary Key)
    *   `user_id` (Integer, Foreign Key $\rightarrow$ `users.id`)
    *   `title` (String)
    *   `subject` (String)
    *   `questions` (JSON text blob representing MCQs)
    *   `score` (Integer, Nullable until submitted)
    *   `total_questions` (Integer)
    *   `created_at` (DateTime, defaults to UTC)
4.  **StudyLog (`study_logs` table)**:
    *   `id` (Integer, Primary Key)
    *   `user_id` (Integer, Foreign Key $\rightarrow$ `users.id`)
    *   `subject` (String)
    *   `duration_minutes` (Integer)
    *   `activity_type` (String: `pomodoro`, `quiz`, `chat`, `task_completion`)
    *   `date` (Date, defaults to today)

---

## 5. API Endpoints Map

All secured endpoints require authentication headers in the format: `Authorization: Bearer <JWT>`.

| Route | Method | Auth Required | Description |
|---|---|---|---|
| `/api/auth/register` | POST | No | Registers user, signs JWT |
| `/api/auth/login` | POST | No | Validates credentials, signs JWT |
| `/api/auth/profile` | GET | Yes | Retrieves profile stats & goals |
| `/api/auth/profile/goal` | PUT | Yes | Updates daily target minutes |
| `/api/tasks` | GET | Yes | Retrieves user task list |
| `/api/tasks` | POST | Yes | Creates new task record |
| `/api/tasks/<id>` | PUT | Yes | Modifies status or completed pomodoros |
| `/api/tasks/<id>` | DELETE | Yes | Removes task record |
| `/api/quiz/generate` | POST | Yes | Initiates AI mock quiz generation |
| `/api/quiz/submit` | POST | Yes | Submits quiz answers and records score |
| `/api/quiz/history` | GET | Yes | Retrieves user evaluation history |
| `/api/ai/chat` | POST | Yes | Conversational bot tutor interface |
| `/api/ai/study_log` | POST | Yes | Inserts custom study intervals |
| `/api/ai/recommendations` | GET | Yes | Compiles customized system rules suggestions |
| `/api/ai/analytics` | GET | Yes | Compiles aggregate focus stats |

---

## 6. Functional System Workflows

The monolithic platform is designed around four key interactive pipelines. These are visually mapped to sequence diagrams in the architecture documentation:

1.  **Authentication & JWT Lifecycle**:
    During registration, users input details which are stored alongside salted hashes. Subsequent logins evaluate password matches, returning a JWT token signed with user identifiers and a 7-day expiration. The token is attached to the client header on subsequent requests.
    *(Referenced in [docs/uml/auth_flow.png](file:///d:/final-project/docs/uml/auth_flow.png))*
2.  **Task Lifecycle & Pomodoro Focus Tracking**:
    Students create tasks and click "Focus" to port task descriptors directly into the Pomodoro system. Completing the 25-minute timer triggers an auto-logged 25-minute study log to the AI system and increments the completed pomodoro counter on the active task.
    *(Referenced in [docs/uml/task_flow.png](file:///d:/final-project/docs/uml/task_flow.png))*
3.  **Quiz Generation & Assessment Engine**:
    Students input a topic, prompting the system to generate a 5-question multiple choice test. The client renders the questions and submits student answers, returning a structured score card, question explanations, and logging a 15-minute study block.
    *(Referenced in [docs/uml/quiz_flow.png](file:///d:/final-project/docs/uml/quiz_flow.png))*
4.  **AI Feynman Chatbot**:
    The student requests concept explanations. The AI chatbot provides tutoring feedback and logs a 1-minute study session to capture the educational engagement.
    *(Referenced in [docs/uml/chatbot_flow.png](file:///d:/final-project/docs/uml/chatbot_flow.png))*

---

## 7. Testing and Verification Results

The monolithic project features a Python test suite implemented in `backend/tests/` using **pytest**. The test code verifies endpoints, exception handling, data structures, and database constraints.

### Test Execution Command
```powershell
.\venv\Scripts\pytest backend/tests/ -v
```

### Verification Summary
*   **Auth Module (11 tests)**: Checked duplicate user handling, validation constraints, JWT token signing/verification, and profile edits.
*   **Planner Module (6 tests)**: Verified task CRUD functionality, task deletions, and task completion database logs.
*   **Quiz & AI Module (3 tests)**: Checked AI mock quizzes, submit scores calculations, and chatbot greetings.
*   **Result**: All **20 tests passed successfully** in 19.04 seconds, confirming backend monolithic code is production-ready.

---

## 8. Technologies Used

*   **Backend Development**: Python 3.13, Flask (API Server), Flask-SQLAlchemy (ORM Mapping), SQLite (Database storage).
*   **Security & Auth**: bcrypt (Hashing credentials), PyJWT (Token serialization & validation).
*   **Frontend Interface**: HTML5 (Semantic pages), Vanilla CSS (Flexbox/Grid visual design), JavaScript (ES6 modules, Fetch API).
*   **Testing Infrastructure**: PyTest (Automated validation runner).

---

## 9. Future Improvements

*   **Peer Rooms (WebRTC)**: Collaborative Pomodoro lobbies allowing students to study together in live virtual groups.
*   **Calendar Integrations**: Sync tasks with external services like Google Calendar or Microsoft Outlook.
*   **Advanced LLM Agent Integration**: Connecting the AI chatbot and quiz generator to actual LLMs (e.g. OpenAI or Gemini) for open-ended concept tutor prompts instead of template-based keywords.

---

## 10. Conclusion

The monolithic configuration of the **AI Study Buddy** project successfully integrates active focus, self-assessment, and tutoring. Backed by solid unit coverage and production-ready WSGI compatibility with Gunicorn, this architecture serves as a stable base for monolithic deployments.
