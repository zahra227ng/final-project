import os
import requests
from flask import Flask, request, jsonify, Response, send_from_directory

app = Flask(__name__)

# Static files folder mapping
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend'))

# Service URLs
SERVICES = {
    'auth': 'http://127.0.0.1:5001',
    'planner': 'http://127.0.0.1:5002',
    'quiz': 'http://127.0.0.1:5003',
    'ai': 'http://127.0.0.1:5004'
}


# Generic proxy handler
def proxy_request(service_url, path):
    url = f"{service_url}/{path}"
    
    # Forward headers (excluding Host)
    headers = {key: value for key, value in request.headers if key.lower() != 'host'}
    
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            params=request.args,
            allow_redirects=False,
            timeout=5
        )
        
        # Exclude headers that Gunicorn/WSGI will rewrite
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers_items = [
            (k, v) for k, v in resp.headers.items()
            if k.lower() not in excluded_headers
        ]
        
        return Response(resp.content, resp.status_code, headers_items)
    except requests.exceptions.RequestException as e:
        return jsonify({'message': f'Gateway Service routing error: {str(e)}'}), 502

# Proxy Routes
@app.route('/api/auth/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_auth(path):
    return proxy_request(SERVICES['auth'], path)

@app.route('/api/tasks', methods=['GET', 'POST', 'OPTIONS'])
@app.route('/api/tasks/<path:path>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_tasks(path=None):
    subpath = f"tasks/{path}" if path else "tasks"
    return proxy_request(SERVICES['planner'], subpath)

@app.route('/api/quiz/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_quiz(path):
    return proxy_request(SERVICES['quiz'], f"quiz/{path}")

@app.route('/api/ai/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_ai(path):
    return proxy_request(SERVICES['ai'], path)

# SPA Static serving
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if path != "" and os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    else:
        return send_from_directory(FRONTEND_DIR, 'index.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
