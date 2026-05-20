# Slide Presentation Outline — AI Study Buddy

This document provides a slide-by-slide outline for the semester project final evaluation presentation.

---

### Slide 1: Project Title & Team
* **Slide Title**: AI Study Buddy — Interactive Academic Focus Companion
* **Content**:
  - Semester Project for Software Construction & Development
  - Team Name: Code Crafting Associates
  - Team Members: Frontend Lead, Backend Lead, Database Manager, Testing Lead, Documentation Lead
* **Visuals**: Modern mockup of the dashboard layout showing focus statistics.

### Slide 2: The Problem Statement
* **Slide Title**: Challenges in Modern Student Productivity
* **Content**:
  - **Procrastination**: Students struggle to maintain focused, uninterrupted study sessions.
  - **Disorganized Planning**: Academic calendars are disconnected from actual study efforts.
  - **Passive Reading**: Re-reading textbook notes is ineffective compared to active recall (quizzing).
  - **Vague Metrics**: Students lack a subject-wise breakdown of where their study time actually goes.

### Slide 3: Proposed Solution
* **Slide Title**: AI Study Buddy — An Interactive System
* **Content**:
  - A comprehensive student cockpit linking planning, focusing, and evaluation.
  - **Smart Planner**: Tasks mapped with estimated Pomodoro focus counts.
  - **Focus Timer**: Embedded Pomodoro timer with customizable Work/Break cycles.
  - **Practice Quizzes**: AI-generated MCQ tests with instant grading and explanation boxes.
  - **Conversational Tutor**: A chatbot to explain topics on command.
  - **Dashboard Analytics**: Visual 7-day study history graphs.

### Slide 4: Technology Stack
* **Slide Title**: Lightweight, Self-Contained Architecture
* **Content**:
  - **Frontend**: Single-Page Application (SPA) using HTML5, Vanilla CSS3 (with variables & glassmorphic styles), and ES6 JavaScript modules. (Zero compile overhead).
  - **Backend**: Flask (Python) REST API.
  - **Database**: SQLite with SQLAlchemy ORM (Serverless local database, easily adaptable to MySQL).
  - **Testing**: PyTest for unit and integration routes testing.

### Slide 5: Software Engineering Core Concepts
* **Slide Title**: Software Construction Practices Demonstrated
* **Content**:
  - **Agile/Scrum Sprints**: Evolving features from requirements to testing.
  - **Refactoring Spaghetti Code**: Demonstrable comparison of monolithic SQL code vs MVC structured ORM backend.
  - **Exception Handling**: Safe client error notifications on database or API failures.
  - **Automated Verification**: GitHub Actions running PyTest on push commands.
  - **Lehman's Laws**: Practical alignment with software evolution laws.

### Slide 6: Refactoring Highlights (Before & After)
* **Slide Title**: Improving Code Health and Security
* **Content**:
  - **Legacy Spaghetti**: Plaintext passwords, raw SQL string queries, global connection hazards.
  - **Refactored Modular**: bcrypt salts encryption, parameterized ORM classes, separation of routes, blueprints, and database services.
* **Visuals**: Code comparison showing SQLi prevention.

### Slide 7: Interactive Live Demo
* **Slide Title**: Core Application Walkthrough
* **Content**:
  - Registration & Login flow (JWT generated).
  - Adding tasks to the Smart Planner.
  - Linking a task to the Pomodoro timer and starting the focus countdown.
  - Generating and answering a Computer Science Quiz.
  - Prompting the AI Chatbot with the Feynman Technique chip.
  - Inspecting the updated weekly bar charts on the Analytics panel.

### Slide 8: Testing Strategy & Results
* **Slide Title**: Quality Assurance Metrics
* **Content**:
  - **Unit Testing**: PyTest assertions for Auth registration, Quiz generation logic, task CRUD operations, and recommendation priorities.
  - **Automated Testing**: CI/CD config executing checks on every branch merge.
  - **Robustness**: Verifying input check bounds and invalid date formats.

### Slide 9: Project Learning Outcomes
* **Slide Title**: Key Engineering Takeaways
* **Content**:
  - Hands-on experience with Agile sprint scheduling and team role adjustments.
  - Practical understanding of secure backend construction (JWTs, bcrypt).
  - Experience in refactoring legacy codebases to resolve cyclomatic complexity.
  - Implementation of automated CI/CD validation workflows.

### Slide 10: Future Scope & Conclusion
* **Slide Title**: Scalability & Future Directions
* **Content**:
  - Integration with large language models (LLM API connections).
  - Student study groups and peer leaderboard streak sharing.
  - Calendar sync (Google Calendar / Microsoft Outlook).
  - **Conclusion**: A functional, well-structured, and verified system meeting all Software Construction academic requirements.
  - **Q&A**: Opening floor for questions.
