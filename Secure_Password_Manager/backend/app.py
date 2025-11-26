import os
import sys
import webbrowser
import socket
from threading import Timer
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.models import db
from backend.routes.auth import auth_bp
from backend.routes.passwords import passwords_bp

def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='/')
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    CORS(app, supports_credentials=True) # Allow credentials for session cookie

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(passwords_bp, url_prefix='/api/passwords')

    # Serve React App
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    # Create tables
    with app.app_context():
        db.create_all()

    return app

def find_available_port(start_port=5000):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
            port += 1

def open_browser(port):
    webbrowser.open_new(f'http://localhost:{port}')

if __name__ == '__main__':
    app = create_app()
    port = find_available_port()
    
    # Open browser after 1.5 seconds to ensure server is up
    Timer(1.5, open_browser, args=[port]).start()
    
    print(f"Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
