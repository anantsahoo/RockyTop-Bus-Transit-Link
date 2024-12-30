from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy with no parameters
db = SQLAlchemy()

class User(db.Model, UserMixin):
    # Database fields
    id = db.Column(db.Integer, primary_key=True)  # Primary key, unique identifier for each user
    username = db.Column(db.String(20), unique=True, nullable=False)  # Username field, must be unique and not nullable
    password_hash = db.Column(db.String(128))  # Stores hashed passwords

    # Set password method to hash plain passwords before storing them
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check password method to verify password against the hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
