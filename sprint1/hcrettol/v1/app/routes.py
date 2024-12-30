from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, db

main = Blueprint('main', __name__)

@main.route('/')
def welcome():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))  # Assuming 'main.home' is your authenticated homepage
    return render_template('welcome.html')

@main.route('/home')
@login_required
def home():
    return render_template('home.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            # It's a good practice to return to the login page with an error message.
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return 'Username already taken'
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.welcome'))

@main.route('/update_favorites', methods=['POST'])
@login_required
def update_favorites():
    user = current_user
    new_favorite = request.form['favorite']
    if user.favorite_places:
        user.favorite_places += ", " + new_favorite  # Append new favorite place
    else:
        user.favorite_places = new_favorite  # Initialize if empty
    db.session.commit()
    return redirect(url_for('main.home'))