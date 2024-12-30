# Hello Plus Flask Application

## Project Overview

This Flask application is a simple user management system designed to demonstrate the basics of web application development using Flask, SQLAlchemy, and Flask-Login. It includes functionalities for user registration, login, and logout, along with a personal dashboard accessible upon successful login.

## Technologies Used

- **Flask**: A micro web framework written in Python.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) system for Python.
- **Flask-Login**: Provides user session management for Flask.
- **SQLite**: Lightweight disk-based database that doesn’t require a separate server process.

## Features

- **User Registration**: Allows new users to register.
- **User Login**: Existing users can log in using their credentials.
- **User Logout**: Logged-in users can safely log out.
- **Protected Dashboard**: Displays a personal dashboard that only authenticated users can access.

## Setup and Installation

### Prerequisites

- Python 3.12.6
- pip (Python package installer)

### Installing Dependencies

To install the required packages, run the following command in your terminal:

```bash
pip install -r requirements.txt 
```

### Running the Application

To run the program, run the following command in your terminal:
```bash
python main.py
```
The application will be available at http://127.0.0.1:5000/ on your web browser.


### Additional Notes

- **Credits**: Tech with tim Flask tutorial video https://www.youtube.com/watch?v=dam0GPOAvVI&t=2485s&ab_channel=TechWithTim