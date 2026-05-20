import os
import sys

# Ensure backend folder is in sys.path so Gunicorn finds the 'app' module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

