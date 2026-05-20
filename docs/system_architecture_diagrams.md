# AI Study Buddy — UML System Architecture Diagrams

This document contains the official UML design representation for the **AI Study Buddy** application. The diagrams below model the database entities, routes, active lifecycles, and physical node layouts.

---

## 1. Class Diagram

The class diagram maps the relationships between the database model entities, route blueprints (controllers), and the rule-based AI core service.

![Class Diagram](images/class_diagram.png)

```mermaid
classDiagram
    %% Core SQLAlchemy Database Models
    class User {
        +int id
        +string username
        +string email
        +string password_hash
        +int streak
        +date last_active
        +int daily_goal_minutes
        +set_password(password)
        +check_password(password)
        +to_dict()
    }
    
    class Task {
        +int id
        +int user_id
        +string title
        +string description
        +date due_date
        +string subject
        +int estimated_pomodoros
        +int completed_pomodoros
        +string status
        +to_dict()
    }
    
    class Quiz {
        +int id
        +int user_id
        +string title
        +string subject
        +json questions
        +int score
        +int total_questions
        +date created_at
        +to_dict()
    }
    
    class StudyLog {
        +int id
        +int user_id
        +string subject
        +int duration_minutes
        +string activity_type
        +date date
        +to_dict()
    }

    %% AI Engine Service Layer
    class AIEngine {
        +get_recommendations(user_tasks, streak) List
        +generate_quiz(subject, topic) Dict
        +chatbot_response(message) Dict
    }

    %% Blueprint Routes (Controller Layer)
    class AuthRoutes {
        +register() Response
        +login() Response
        +get_profile() Response
    }
    
    class PlannerRoutes {
        +get_tasks() Response
        +create_task() Response
        +update_task() Response
        +delete_task() Response
    }
    
    class QuizRoutes {
        +generate_quiz() Response
        +submit_quiz() Response
        +get_quiz_history() Response
    }
    
    class AIRoutes {
        +get_recommendations() Response
        +get_analytics() Response
        +post_study_log() Response
        +post_chat() Response
    }

    %% Relationships
    User "1" *-- "*" Task : owns
    User "1" *-- "*" Quiz : attempts
    User "1" *-- "*" StudyLog : logs

    AuthRoutes ..> User : queries/modifies
    PlannerRoutes ..> User : authenticates
    PlannerRoutes ..> Task : queries/modifies
    PlannerRoutes ..> StudyLog : creates_on_complete

    QuizRoutes ..> User : authenticates
    QuizRoutes ..> Quiz : queries/modifies
    QuizRoutes ..> AIEngine : delegates_generation

    AIRoutes ..> User : authenticates
    AIRoutes ..> StudyLog : aggregates/inserts
    AIRoutes ..> AIEngine : queries_recs_and_chat
```

---

## 2. Sequence Diagrams

### 2.1 User Authentication Flow
This diagram details the flow of user registration/login, JWT token issuance, and subsequent authenticated sessions.

![User Authentication Flow](images/auth_flow.png)

```mermaid
sequenceDiagram
    autonumber
    actor Student as Student Client
    participant FE as Frontend (auth.js / api.js)
    participant AuthAPI as Auth Router (auth.py)
    participant DB as SQLite Database

    %% Registration
    Note over Student, DB: User Registration Flow
    Student->>FE: Fill register form & submit
    FE->>AuthAPI: POST /api/auth/register (username, email, password)
    AuthAPI->>DB: Check if username/email exists
    DB-->>AuthAPI: No duplicate found
    AuthAPI->>AuthAPI: Hash password via bcrypt
    AuthAPI->>DB: Insert new User row
    DB-->>AuthAPI: Confirm write
    AuthAPI->>AuthAPI: Encode signed JWT (user_id, exp)
    AuthAPI-->>FE: Return JSON Response + JWT Token
    FE->>FE: Cache JWT in LocalStorage

    %% Login & Session Usage
    Note over Student, DB: Authenticated API Session Flow
    Student->>FE: Click Dashboard / Refresh
    FE->>AuthAPI: GET /api/auth/profile (Headers: Authorization: Bearer JWT)
    AuthAPI->>AuthAPI: Decode JWT & Verify Signature
    AuthAPI->>DB: Query User profile (by user_id)
    DB-->>AuthAPI: Return User details (username, streak)
    AuthAPI-->>FE: HTTP 200 OK + User data
    FE->>Student: Render customized dashboard views
```

### 2.2 Task Lifecycle & Pomodoro Focus Flow
This diagram shows how creating a task leads to Pomodoro study, which subsequently triggers automatic SQL logs.

![Task Lifecycle & Pomodoro Focus Flow](images/task_flow.png)

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant PlannerJS as planner.js
    participant PomoJS as pomodoro.js
    participant Router as Planner/AI Router
    participant DB as SQLite Database

    %% 1. Task Creation
    Student->>PlannerJS: Input task details (Math, Est Pomo: 2) & save
    PlannerJS->>Router: POST /api/tasks
    Router->>DB: Insert Task (status='pending', completed_pomodoros=0)
    DB-->>Router: Confirm write
    Router-->>PlannerJS: HTTP 201 Created (task_id)
    PlannerJS->>Student: Render pending task card

    %% 2. Link Focus
    Student->>PlannerJS: Click "Focus ⏱️" on math task card
    PlannerJS->>PomoJS: Redirect view, prefill subject: "Math", link task_id
    PomoJS->>Student: Display "Focusing on: Math task"

    %% 3. Pomodoro Timer Active Session
    Student->>PomoJS: Click "Start Focus"
    Note over PomoJS: Countdown ticks down (25 mins)...
    PomoJS->>PomoJS: Timer reaches 0:00 (synthesize Web Audio chime)
    
    %% 4. Automatic Log Triggers
    PomoJS->>Router: POST /api/ai/study_log (Math, 25 mins, activity='pomodoro')
    Router->>DB: Insert StudyLog row
    Router->>DB: Update User daily streak & check goal targets
    DB-->>Router: Confirm update
    Router-->>PomoJS: HTTP 201 Created
    
    %% 5. Task completed_pomodoros increment
    PomoJS->>Router: PUT /api/tasks/<task_id> (completed_pomodoros = 1)
    Router->>DB: Update Task row
    DB-->>Router: Confirm write
    Router-->>PomoJS: HTTP 200 OK
    PomoJS->>Student: Alert focus session logged! Transition to break mode.
```

### 2.3 Interactive Practice Quiz Flow
This sequence details generating a quiz, evaluating answers, scoring, and writing study logs.

![Interactive Practice Quiz Flow](images/quiz_flow.png)

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant QuizJS as quiz.js
    participant Router as Quiz Router
    participant AI as AI Engine (ai_engine.py)
    participant DB as SQLite Database

    %% Quiz Generation
    Student->>QuizJS: Select Subject "Software Eng", Topic "Agile" & Generate
    QuizJS->>Router: POST /api/quiz/generate (subject, topic)
    Router->>AI: generate_quiz("Software Engineering", "Agile")
    AI-->>Router: Return Dict (5 MCQs, options, correct answers, explanations)
    Router->>DB: Save Quiz object (score=NULL, total=5)
    DB-->>Router: Confirm write
    Router-->>QuizJS: Return Quiz data JSON (quiz_id, questions, choices)
    QuizJS->>Student: Render Question 1 board

    %% Answer Submission & Evaluation
    Student->>QuizJS: Answer all questions & click submit
    QuizJS->>Router: POST /api/quiz/submit (quiz_id, answers array)
    Router->>DB: Query Quiz details
    DB-->>Router: Return saved answers keys
    Router->>Router: Compare keys & compute score (e.g. 4/5)
    Router->>DB: Update Quiz score (4/5)
    Router->>DB: Insert StudyLog (duration=15 mins, activity='quiz')
    DB-->>Router: Confirm write
    Router-->>QuizJS: Return Results (score=4, correct indices, explanations)
    QuizJS->>Student: Render Score Card + explanation boxes + Audio chimes
```

### 2.4 AI Chatbot Flow
This sequence details the chat flow.

![AI Chatbot Flow](images/chatbot_flow.png)

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant ChatJS as chatbot.js
    participant Router as AI Router
    participant AI as AI Engine (ai_engine.py)
    participant DB as SQLite Database

    Student->>ChatJS: Types query / clicks Feynman quick chip
    ChatJS->>ChatJS: Append user message bubble to view
    ChatJS->>Router: POST /api/ai/chat (message text)
    Router->>AI: chatbot_response(message text)
    AI->>AI: Scan keywords matching greetings, study tips, or default concepts
    AI-->>Router: Return Dict (response text)
    Router->>DB: Insert StudyLog (duration=1 min, activity='chat')
    DB-->>Router: Confirm write
    Router-->>ChatJS: Return response text JSON
    ChatJS->>ChatJS: Parse bold tags, append bot bubble, scroll to bottom
    ChatJS->>Student: Display tutoring response
```

---

## 3. Component Diagram

The component diagram showcases the boundaries between modules, mapping frontend event controllers, API routers, service layers, and the SQLite schema objects.

![Component Diagram](images/component_diagram.png)

```mermaid
flowchart TD
    %% Front-End SPA Components
    subgraph Frontend ["Frontend Single-Page Application"]
        UI["index.html"]
        API_Client["api.js"]
        Auth_Controller["auth.js"]
        Planner_Controller["planner.js"]
        Pomo_Controller["pomodoro.js"]
        Quiz_Controller["quiz.js"]
        Chat_Controller["chatbot.js"]
        Analytics_Controller["analytics.js"]
        
        Auth_Controller --> API_Client
        Planner_Controller --> API_Client
        Pomo_Controller --> API_Client
        Quiz_Controller --> API_Client
        Chat_Controller --> API_Client
        Analytics_Controller --> API_Client
    end

    %% Backend Flask Components
    subgraph Backend ["Flask REST API Server"]
        Factory["__init__.py (App Factory)"]
        Auth_Routes["auth.py (Blueprint)"]
        Planner_Routes["planner.py (Blueprint)"]
        Quiz_Routes["quiz.py (Blueprint)"]
        AI_Routes["ai.py (Blueprint)"]
        AI_Engine["ai_engine.py (AI Service)"]
        
        Factory --> Auth_Routes
        Factory --> Planner_Routes
        Factory --> Quiz_Routes
        Factory --> AI_Routes
        
        Quiz_Routes --> AI_Engine
        AI_Routes --> AI_Engine
    end

    %% Data Store Layer
    subgraph DB_Layer ["Database Layer"]
        ORM_Models["models.py (SQLAlchemy ORM)"]
        DB[("SQLite Database<br>(ai_study_buddy.db)")]
        
        ORM_Models --> DB
    end

    %% Inter-component Connectors
    API_Client ==>|HTTP JWT in Headers| Auth_Routes
    API_Client ==>|HTTP JWT in Headers| Planner_Routes
    API_Client ==>|HTTP JWT in Headers| Quiz_Routes
    API_Client ==>|HTTP JWT in Headers| AI_Routes
    
    Auth_Routes ----> ORM_Models
    Planner_Routes ----> ORM_Models
    Quiz_Routes ----> ORM_Models
    AI_Routes ----> ORM_Models
```

---

## 4. Deployment Diagram

The deployment diagram illustrates the physical hosting configuration, tracing how browsers communicate with Gunicorn on Render, and showcasing the GitHub automated verification runner.

![Deployment Diagram](images/deployment_diagram.png)

```mermaid
flowchart TD
    %% User System Node
    subgraph Client ["User PC (Client Tier)"]
        subgraph Browser ["Web Browser (Chrome/Firefox/Safari)"]
            SPA["Single-Page Application"]
        end
    end

    %% Render Production Cloud Service Node
    subgraph Render ["Render Production Cloud (Application Tier)<br>OS: Ubuntu Linux"]
        subgraph Daemon ["Gunicorn HTTP Daemon"]
            WSGI["WSGI Application Server"]
        end
        subgraph Flask ["Flask Backend Instance"]
            FlaskApp["AI Study Buddy Core"]
        end
        subgraph Storage ["Persistent File System Storage"]
            DB_File[("SQLite File<br>(ai_study_buddy.db)")]
        end
        
        WSGI --> FlaskApp
        FlaskApp --> DB_File
    end

    %% GitHub actions Node
    subgraph CI_CD ["GitHub Actions (CI/CD Pipeline)<br>OS: ubuntu-latest VM"]
        subgraph Actions ["Python 3.13 Test Environment"]
            Tests["PyTest Suite"]
        end
    end

    %% Communication Connectors
    SPA ==>|HTTPS / WSS on Port 443| WSGI
    Tests -->|Clones and runs automated validation| FlaskApp
```
