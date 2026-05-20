import random

class AIEngine:
    @staticmethod
    def generate_quiz(subject, topic=None):
        """
        Generates 5 multiple choice questions based on the subject and topic.
        """
        subject_lower = subject.lower() if subject else ""
        topic_lower = topic.lower() if topic else ""
        
        # Default quiz library for standard subjects
        database_quizzes = {
            "computer science": [
                {
                    "question": "What is the time complexity of searching in a balanced Binary Search Tree (BST)?",
                    "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                    "correct": 1,
                    "explanation": "In a balanced BST, the height of the tree is log(n). Therefore, search, insertion, and deletion operations take O(log n) time."
                },
                {
                    "question": "Which data structure uses LIFO (Last In First Out) ordering?",
                    "options": ["Queue", "Stack", "Heap", "Graph"],
                    "correct": 1,
                    "explanation": "A stack is a linear data structure that follows the LIFO principle, where the last element added is the first one to be removed."
                },
                {
                    "question": "What is the primary purpose of an Operating System's kernel?",
                    "options": ["To run web applications", "To manage system resources and communication between hardware and software", "To compile high-level programming code", "To provide database querying interfaces"],
                    "correct": 1,
                    "explanation": "The kernel is the core component of an OS that manages hardware resources (CPU, memory, devices) and acts as a bridge between applications and hardware."
                },
                {
                    "question": "Which of the following is NOT a fundamental OOP concept?",
                    "options": ["Encapsulation", "Inheritance", "Polymorphism", "Compilation"],
                    "correct": 3,
                    "explanation": "The four main pillars of Object-Oriented Programming are Encapsulation, Inheritance, Polymorphism, and Abstraction. Compilation is a translation process."
                },
                {
                    "question": "What does HTTP stand for?",
                    "options": ["High Transfer Text Protocol", "Hypertext Transfer Protocol", "Hyper Terminal Tracking Protocol", "Hosting Tech Transfer Protocol"],
                    "correct": 1,
                    "explanation": "HTTP stands for Hypertext Transfer Protocol, which is the foundation of data communication for the World Wide Web."
                }
            ],
            "software engineering": [
                {
                    "question": "Which Agile/Scrum event is held at the end of a sprint to inspect the progress and adapt the product backlog?",
                    "options": ["Daily Scrum", "Sprint Planning", "Sprint Review", "Sprint Retrospective"],
                    "correct": 2,
                    "explanation": "The Sprint Review is held at the end of the Sprint to inspect the increment and adapt the Product Backlog if needed."
                },
                {
                    "question": "What is the main goal of Lehman's Law of Continuing Change?",
                    "options": ["Software must be completely rewritten every 5 years", "An E-type software system must undergo continuous adaptation or it becomes progressively less useful", "Refactoring should only happen in the testing phase", "Bugs will decrease naturally as software evolves"],
                    "correct": 1,
                    "explanation": "Lehman's First Law (Continuing Change) states that systems must change continuously to remain satisfactory in a changing environment."
                },
                {
                    "question": "Which design pattern ensures a class has only one instance and provides a global point of access to it?",
                    "options": ["Factory Method", "Observer", "Singleton", "Adapter"],
                    "correct": 2,
                    "explanation": "The Singleton pattern restricts the instantiation of a class to one single instance and provides a global access point to it."
                },
                {
                    "question": "In Git, which command is used to combine the histories of two branches?",
                    "options": ["git checkout", "git merge", "git commit", "git push"],
                    "correct": 1,
                    "explanation": "The 'git merge' command lets you take the independent lines of development created by git branch and integrate them into a single branch."
                },
                {
                    "question": "What is the difference between Verification and Validation?",
                    "options": ["Verification is building the right product; Validation is building the product right", "Verification is building the product right; Validation is building the right product", "There is no difference; they are synonyms", "Verification is done by users; Validation is done by developers"],
                    "correct": 1,
                    "explanation": "Verification ensures the software meets specifications ('Are we building the product right?'). Validation ensures the software meets user needs ('Are we building the right product?')."
                }
            ],
            "math": [
                {
                    "question": "What is the derivative of f(x) = x^2 + 3x - 5?",
                    "options": ["2x + 3", "x + 3", "2x - 5", "x^2 + 3"],
                    "correct": 0,
                    "explanation": "Using the power rule, the derivative of x^2 is 2x, and the derivative of 3x is 3. The constant -5 differentiates to 0, giving 2x + 3."
                },
                {
                    "question": "What is the value of log base 2 of 64?",
                    "options": ["5", "6", "7", "8"],
                    "correct": 1,
                    "explanation": "Since 2 raised to the power of 6 is 64 (2^6 = 64), log2(64) equals 6."
                },
                {
                    "question": "In a right-angled triangle, if the sides containing the right angle are 3 and 4, what is the hypotenuse?",
                    "options": ["5", "6", "7", "8"],
                    "correct": 0,
                    "explanation": "According to the Pythagorean theorem, a^2 + b^2 = c^2. Here, 3^2 + 4^2 = 9 + 16 = 25. Thus, c = sqrt(25) = 5."
                },
                {
                    "question": "What is the sum of the angles in a hexagon?",
                    "options": ["360 degrees", "540 degrees", "720 degrees", "900 degrees"],
                    "correct": 2,
                    "explanation": "The sum of interior angles of an n-sided polygon is given by (n-2) * 180. For a hexagon (n=6), (6-2)*180 = 4 * 180 = 720 degrees."
                },
                {
                    "question": "Which of the following numbers is prime?",
                    "options": ["15", "21", "29", "33"],
                    "correct": 2,
                    "explanation": "A prime number is only divisible by 1 and itself. 29 has no other factors, whereas 15 (3x5), 21 (3x7), and 33 (3x11) are composite."
                }
            ]
        }
        
        # Pick relevant quiz set or fall back to generic
        normalized_subject = "computer science"
        if "software" in subject_lower or "agile" in subject_lower or "sdoc" in subject_lower:
            normalized_subject = "software engineering"
        elif "math" in subject_lower or "calc" in subject_lower or "algebra" in subject_lower or "geometry" in subject_lower:
            normalized_subject = "math"
            
        questions = database_quizzes.get(normalized_subject)
        
        # Customize quiz titles based on topic
        title = f"Quick Quiz on {subject if subject else 'General Study'}"
        if topic:
            title += f" ({topic})"
            
        return {
            "title": title,
            "subject": subject,
            "questions": questions,
            "total_questions": len(questions)
        }

    @staticmethod
    def get_chat_response(message):
        """
        Simulates an intelligent study chatbot tutor.
        """
        message_lower = message.lower()
        
        greetings = ["hello", "hi", "hey", "greetings", "yo"]
        study_methods = ["how to study", "pomodoro", "feynman", "spaced repetition", "active recall", "focus"]
        coding_questions = ["code", "programming", "python", "javascript", "bug", "syntax", "api"]
        exam_tips = ["exam", "test", "quiz", "grade", "marks", "preparation", "prepare"]
        
        # Check greeting
        if any(g in message_lower for g in greetings):
            return (
                "Hello! I am your AI Study Buddy Chatbot. 📚🤖\n\n"
                "I can help you with course topics, explaining complex concepts, designing study plans, "
                "giving coding tips, or recommending productivity techniques. What are we studying today?"
            )
            
        # Check study techniques
        elif any(sm in message_lower for sm in study_methods):
            return (
                "Here are the top 3 scientifically-proven study techniques:\n\n"
                "1. **Pomodoro Technique**: Focus for 25 minutes, then take a 5-minute break. It prevents burnout!\n"
                "2. **Feynman Technique**: Explain a concept in simple terms as if you were teaching it to a child. This exposes gaps in your understanding.\n"
                "3. **Spaced Repetition & Active Recall**: Instead of highlighting text, test yourself (e.g., generate a quiz!) and review the material at increasing intervals (1 day, 3 days, 7 days).\n\n"
                "I can generate a practice quiz for you right now. Just type what subject you want!"
            )
            
        # Check coding questions
        elif any(c in message_lower for c in coding_questions):
            return (
                "Ah, a fellow coder! 💻 Here's a quick cheat-sheet for writing clean, professional code:\n\n"
                "- **Keep functions single-purpose**: A function should do one thing and do it well.\n"
                "- **Refactor legacy code**: Don't leave unused code blocks (spaghetti code). Extract modules and write clear docstrings.\n"
                "- **Handle Exceptions**: Always wrap file/database access and network requests in try-except blocks to avoid hard crashes.\n"
                "- **Write Unit Tests**: It validates your logic. We use PyTest in this project to test Auth and Quiz logic!\n\n"
                "Do you have a specific programming concept you want me to explain?"
            )
            
        # Check exams
        elif any(e in message_lower for e in exam_tips):
            return (
                "Exam preparation can be stressful, but planning ahead makes a huge difference! 🎯\n\n"
                "Here is a smart strategy:\n"
                "1. **Create an inventory** of all exam topics.\n"
                "2. **Rate your confidence** on each topic (1 to 5) so you can prioritize weak areas.\n"
                "3. **Do active practice**: Solve sample questions rather than just re-reading slides.\n"
                "4. **Get enough sleep**: Memory consolidation happens during REM sleep. Pulling all-nighters actually decreases performance!\n\n"
                "Let's add your exam preparation tasks to the Smart Planner to track your progress."
            )
            
        # Default fallback
        else:
            return (
                f"That's a great question about '{message}'. Here's an analytical breakdown:\n\n"
                "To master this concept, let's break it down into core steps:\n"
                "1. **Define Core Terms**: Make sure you know the vocabulary.\n"
                "2. **Connect to Prior Knowledge**: How does this relate to other topics you study?\n"
                "3. **Apply the Concept**: Let's try testing it with a quiz. You can use the Quiz Generator module on the sidebar to create custom mock assessments.\n\n"
                "Would you like me to suggest a specific study plan for this subject?"
            )

    @staticmethod
    def get_recommendations(tasks, logs, streak):
        """
        Analyzes tasks, past study logs, and streaks to return tailored recommendation cards.
        """
        recommendations = []
        
        # 1. Streak check
        if streak == 0:
            recommendations.append({
                "category": "Streak",
                "title": "Start Your Streak!",
                "suggestion": "Study for at least 25 minutes (1 Pomodoro session) today to kickstart your daily streak!",
                "priority": "high"
            })
        elif streak < 3:
            recommendations.append({
                "category": "Streak",
                "title": "Keep the Momentum!",
                "suggestion": f"You are on a {streak}-day streak. Log a study session today to maintain it!",
                "priority": "medium"
            })
        else:
            recommendations.append({
                "category": "Streak",
                "title": "Awesome Streak!",
                "suggestion": f"Fire! You've studied {streak} days in a row. Don't break the chain today!",
                "priority": "high"
            })
            
        # 2. Tasks analysis
        pending_tasks = [t for t in tasks if t.status != 'completed']
        if not pending_tasks:
            recommendations.append({
                "category": "Planner",
                "title": "Planner is Empty/Cleared",
                "suggestion": "You have no pending tasks! Take a moment to plan your week and add new learning goals.",
                "priority": "low"
            })
        else:
            # Sort by estimated Pomodoro
            urgent = sorted(pending_tasks, key=lambda x: x.estimated_pomodoros, reverse=True)[0]
            recommendations.append({
                "category": "Planner",
                "title": "Focus Priority",
                "suggestion": f"Your task '{urgent.title}' requires multiple focus sessions. We recommend starting a Pomodoro timer for it now.",
                "priority": "high"
            })
            
        # 3. Quiz & Analytics review
        quiz_logs = [log for log in logs if log.activity_type == 'quiz']
        pomodoro_logs = [log for log in logs if log.activity_type == 'pomodoro']
        
        if len(pomodoro_logs) < 2:
            recommendations.append({
                "category": "Focus",
                "title": "Boost Focus Tracking",
                "suggestion": "Try completing at least two 25-minute Pomodoro sessions today to build deep focus habits.",
                "priority": "medium"
            })
            
        if not quiz_logs:
            recommendations.append({
                "category": "Assessment",
                "title": "Test Your Knowledge",
                "suggestion": "You haven't taken a quiz yet. Generate a quiz on Computer Science or Software Engineering to evaluate your current knowledge.",
                "priority": "medium"
            })
            
        # Fallback to make sure there are always interesting recommendations
        if len(recommendations) < 3:
            recommendations.append({
                "category": "AI Tip",
                "title": "Active Recall Tip",
                "suggestion": "Instead of re-reading study materials, close the book and write down everything you remember in the chatbot to test yourself.",
                "priority": "low"
            })
            
        return recommendations
