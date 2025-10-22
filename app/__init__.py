# app/__init__.py

import logging
from flask import Flask

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

def create_app():
    app = Flask(__name__)
    
    # Import and set up controllers
    from app.api.controllers import setup_controllers
    setup_controllers(app)
    
    return app
