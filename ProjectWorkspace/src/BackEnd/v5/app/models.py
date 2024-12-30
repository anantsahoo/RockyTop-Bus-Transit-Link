from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

class RouteHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_stop = db.Column(db.String(255), nullable=False)
    end_stop = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('route_histories', lazy=True))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # New field
    password_hash = db.Column(db.String(128))
    favorite_places = db.Column(db.Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_favorite_places(self):
        if self.favorite_places:
            try:
                return json.loads(self.favorite_places)
            except json.JSONDecodeError:
                # Handle the case where data is in the old comma-separated format
                return [place.strip() for place in self.favorite_places.split(',')]
        else:
            return []

    def add_favorite_place(self, place):
        places = self.get_favorite_places()
        if place not in places:
            places.append(place)
            self.favorite_places = json.dumps(places)
            db.session.commit()

    def remove_favorite_place(self, place):
        places = self.get_favorite_places()
        if place in places:
            places.remove(place)
            self.favorite_places = json.dumps(places) if places else None
            db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
