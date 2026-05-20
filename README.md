# AI Study Buddy 📚🤖

An intelligent, interactive study assistant application designed to help university students optimize productivity, schedule target deadlines, and perform active recall studying. Built as a comprehensive university semester project for the **Software Construction & Development** course.

---

## 🚀 Key Features

* **Smart Task Planner**: Organize academic deadlines and estimate effort using Pomodoro cycles.
* **Pomodoro Focus Timer**: Customizable work and break cycles linked directly to planner tasks, featuring native Web Audio chimes.
* **AI Practice Quiz Generator**: Create custom multiple-choice quizzes dynamically from subjects (Computer Science, Math, Software Engineering) with explanation reviews.
* **AI Chatbot Tutor**: An interactive conversational buddy to explain complex concepts on command.
* **Progress Analytics Dashboard**: Visual CSS bar charts tracking 7-day habits, subject study hours, and quiz averages.
* **Daily Goal & Streak System**: Motivation systems tracking study streaks.
* **Responsive Dark/Light UI**: Adaptive interface styling.

---

## 🛠️ Technology Stack

* **Frontend**: HTML5, Vanilla CSS3 (dynamic HSL theme variables, glassmorphic visual cards), ES6 JavaScript modules.
* **Backend**: Flask (Python 3.13) REST API.
* **Database**: SQLite with SQLAlchemy ORM (Serverless local SQL file database).
* **Testing**: PyTest for unit and integration routes checking.
* **CI/CD**: GitHub Actions Build & Test workflows.

---

## 📁 Repository Directory Structure

```
final-project/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI pipeline
├── backend/
│   ├── app/
│   │   ├── __init__.py        # App Factory & routes registration
│   │   ├── models.py          # SQLAlchemy user and study schema
│   │   ├── routes/
│   │   │   ├── auth.py        # Registration, Login, Profile JWT routes
│   │   │   ├── planner.py     # Task CRUD endpoints
│   │   │   ├── quiz.py        # MCQ generator & submission evaluation
│   │   │   └── ai.py          # Chatbot conversation & recommendations
│   │   └── services/
│   │       └── ai_engine.py   # AI rules & recommendation filters
│   ├── tests/
│   │   ├── conftest.py        # PyTest database & client setups
│   │   └── test_*.py          # Unit test suites
│   ├── run.py                 # Flask server launch script
│   └── requirements.txt       # Backend dependencies log
├── docs/
│   ├── agile_scrum_details.md # Scrum sprints, Lehmann's Laws details
│   ├── final_report.md        # Comprehensive semester report
│   └── presentation_outline.md# grading presentation slides outline
├── frontend/
│   ├── css/
│   │   ├── variables.css      # Core HSL color variables
│   │   ├── app.css            # Navigation, layout, sidebars
│   │   └── components.css     # Form elements, dials, chats, bars
│   ├── js/
│   │   ├── api.js             # Fetch helper, auth token logic
│   │   ├── auth.js            # Registration, login views controller
│   │   ├── dashboard.js       # Navigation and dashboard statistics
│   │   ├── planner.js         # Tasks list compiler
│   │   ├── pomodoro.js        # Timer countdown cycle chimes
│   │   ├── quiz.js            # MCQ player interface
│   │   ├── chatbot.js         # Dialog bubbler
│   │   └── analytics.js       # Bar graph visualizer
│   └── index.html             # UI HTML SPA template
├── legacy_demo/
│   ├── spaghetti_app_bad.py   # spaghetti monolithic baseline
│   └── refactoring_explanation.md # Refactoring optimization report
└── README.md                  # Master manual documentation
```

---

## 💻 Installation & Execution Guide

### Prerequisites
* Python 3.10+ (tested on Python 3.13.5)

### Step 1: Clone and Navigate
Clone this repository to your local system and navigate to the project directory:
```bash
cd final-project
```

### Step 2: Set Up Virtual Environment & Install Dependencies
Create a Python virtual environment and install the required libraries:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate
pip install -r backend/requirements.txt

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### Step 3: Run the Application
Start the Flask application server:
```bash
python backend/run.py
```
The server will boot on `http://127.0.0.1:5000/`.

### Step 4: Open in Web Browser
Open your browser and navigate to:
```url
http://127.0.0.1:5000/
```
The Flask backend will serve both the backend API and the static frontend SPA natively, avoiding all CORS configurations!

---

## 🧪 Running the Test Suite

We use **PyTest** to check route logic. To run tests:
```bash
# Activate environment if not already activated
.\venv\Scripts\activate

# Run tests with verbose details
pytest backend/tests/ -v
```

---

## 🛡️ Software Engineering Highlights

* **Agile Sprints**: Project execution split into 4 increments (1. DB/Auth, 2. Planner/Timer, 3. Quiz/Chatbot, 4. Analytics/Testing).
* **Refactoring Legacy Code**: Contrast our secure modular MVC production database app with the spaghetti monolith inside the `legacy_demo/` folder.
* **Security & JWT**: Password encryption via `bcrypt` salts, API routing blocked by signed authentication JWT tokens.
* **Exception Controls**: Strict checks validate date entries and handle database rolls to block crashes.
* **Continuous Integration**: GitHub Actions CI builds automatically verify every commits pull request.
