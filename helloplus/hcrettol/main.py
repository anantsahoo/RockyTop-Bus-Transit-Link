from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
from sqlalchemy.orm import Session

# Create a Flask application instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey123'  # A secret key required to keep the client-side sessions secure
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Database URI that should be used for the connection
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications to save resources

# Initialize database with app configuration
db.init_app(app)

# Initialize login manager with app configuration
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Specify what view logs the user in (for @login_required)

# Function to load the user object from the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    session = Session(bind=db.engine)  # Create a session to interact with the database
    return session.get(User, int(user_id))  # Retrieve the user by ID

_app_started = False
# Ensure database tables are created before the first request is processed
@app.before_request
def before_first_request():
    global _app_started  # Use a global flag to make sure this runs only once
    if not _app_started:
        with app.app_context():
            db.create_all()  # Create all tables
        _app_started = True

# Home route that requires the user to be logged in
@app.route('/')
@login_required
def home():
    return render_template('home.html')

# Login route that handles showing the login form and logging in users
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()  # Query the database for the user
        if user and user.check_password(password):  # Check if the user exists and the password is correct
            login_user(user)  # Log in the user
            return redirect(url_for('home'))  # Redirect to the home page
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

# Register route for registering new users
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():  # Check if username is already taken
            return render_template('register.html', error="Username already taken")
        new_user = User(username=username)
        new_user.set_password(password)  # Hash and set password
        db.session.add(new_user)  # Add new user to database
        db.session.commit()  # Commit changes
        return redirect(url_for('login'))  # Redirect to login page
    return render_template('register.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Log out the user
    return redirect(url_for('login'))  # Redirect to login page

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
