# LEGACY DEMO: SPAGHETTI APP (POORLY STRUCTURED / HARD TO MAINTAIN)
# WARNING: DO NOT RUN THIS IN PRODUCTION. This is a demonstration of legacy code to be refactored.

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Global connection - not thread safe, prone to corruption
conn = sqlite3.connect('bad_database.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pwd TEXT, streak INT)')
cursor.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT, status TEXT)')
conn.commit()

# PROBLEM 1: Hardcoded credentials and secrets scattered in code
JWT_SECRET = "super-secret-key-that-everyone-knows"

# PROBLEM 2: Business Logic, Database Access, and Route Handlers are completely mixed
@app.route('/reg', methods=['POST'])
def reg():
    # PROBLEM 3: No exception handling. If JSON is missing or database fails, the server crashes with a 500 error
    data = request.json
    name = data['name']
    email = data['email']
    pwd = data['pwd'] # PROBLEM 4: Storing plain text passwords in the database (security vulnerability!)
    
    cursor.execute(f"INSERT INTO users (name, email, pwd, streak) VALUES ('{name}', '{email}', '{pwd}', 0)") # PROBLEM 5: SQL Injection vulnerability!
    conn.commit()
    return jsonify({"status": "user registered"}), 200

@app.route('/login-bad', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    pwd = data['pwd']
    
    # SQL query vulnerable to authentication bypass via injection
    cursor.execute(f"SELECT * FROM users WHERE email = '{email}' AND pwd = '{pwd}'")
    user = cursor.fetchone()
    
    if user:
        return jsonify({"message": "logged in", "user_id": user[0]}), 200
    else:
        return jsonify({"message": "fail"}), 401

@app.route('/add-task', methods=['POST'])
def add():
    # PROBLEM 6: Zero input validation. Can insert empty titles
    data = request.json
    title = data['title']
    
    cursor.execute(f"INSERT INTO tasks (title, status) VALUES ('{title}', 'pending')")
    conn.commit()
    return jsonify({"message": "added"}), 201

# PROBLEM 7: Unused code blocks left commented out or orphaned (Dead code)
# def update_task_bad():
#     # Some old code we forgot to remove
#     pass

@app.route('/get-tasks', methods=['GET'])
def get():
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    
    # PROBLEM 8: Lack of response serialization helper, manually formatting lists
    tasks = []
    for r in rows:
        tasks.append({
            "id": r[0],
            "title": r[1],
            "status": r[2]
        })
    return jsonify(tasks), 200

# PROBLEM 9: Monolithic file structure. Hard to divide work among developers.
# Adding AI Chatbot here directly would bloat this file to 1000 lines of code.

if __name__ == '__main__':
    app.run(port=9999)
