import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from .graph_utils import build_graph

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    # Build the graph when the app starts
    with app.app_context():
        # Build and cache the graph
        app.config['graph'] = build_graph()
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Context processor to add current_year
    @app.context_processor
    @app.context_processor
    def inject_favorite_places():
        favorite_places = []
        if current_user.is_authenticated:
            favorite_places = current_user.get_favorite_places()
        return {'favorite_places': favorite_places}


    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Ensure this is set

    @app.context_processor
    def inject_favorite_places():
        favorite_places = []
        if current_user.is_authenticated:
            if current_user.favorite_places:
                favorite_places = [place.strip() for place in current_user.favorite_places.split(',')]
        return {'favorite_places': favorite_places}

    migrate = Migrate(app, db)

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
