from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, g, current_app
from flask_login import login_user, logout_user, login_required, current_user
from email_validator import validate_email, EmailNotValidError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import re
import googlemaps
import math as m
import pandas as pd
import networkx as nx
from .models import User, db, RouteHistory
from .graph_utils import build_graph, find_earliest_path, time_to_seconds
from app.forms import ChangePasswordForm
import logging

logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to capture all messages

# Read GTFS data
stops = pd.read_csv('gtfs/stops.txt', dtype={'stop_id': str})
stop_times = pd.read_csv('gtfs/stop_times.txt', dtype={'trip_id': str, 'stop_id': str})
trips = pd.read_csv('gtfs/trips.txt', dtype={'trip_id': str, 'route_id': str})
routes = pd.read_csv('gtfs/routes.txt', dtype={'route_id': str})

# Ensure stop_lat and stop_lon are numeric types
stops['stop_lat'] = stops['stop_lat'].astype(float)
stops['stop_lon'] = stops['stop_lon'].astype(float)

# Parse arrival and departure times
stop_times['arrival_seconds'] = stop_times['arrival_time'].apply(time_to_seconds)
stop_times['departure_seconds'] = stop_times['departure_time'].apply(time_to_seconds)

# Sort stop_times by trip_id and stop_sequence
stop_times.sort_values(['trip_id', 'stop_sequence'], inplace=True)

main = Blueprint('main', __name__)

@main.route('/')
def home():
    current_year = datetime.now().year
    favorite_places = []
    if current_user.is_authenticated:
        # Fetch favorite places from the database
        favorite_places = []
        if current_user.is_authenticated and current_user.favorite_places:
            favorite_places = current_user.get_favorite_places()

    return render_template('home.html', current_year=current_year, favorite_places=favorite_places)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['username_or_email'].strip()
        password = request.form['password']

        # Check if identifier is email or username
        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.map_view'))
        else:
            flash("Invalid username/email or password", 'danger')
            return render_template('home.html')
    return render_template('login.html')

def validate_password(password):
    if len(password) < 8:
        return False
    # Check for letters and numbers
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        # Check if username is already taken
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('register.html')

        # Check if email is already registered
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')

        # Validate email
        try:
            valid = validate_email(email)
            email = valid.email  # Replace with normalized form
        except EmailNotValidError as e:
            flash(str(e), 'danger')
            return render_template('register.html')

        # Validate password
        if not validate_password(password):
            flash('Password must be at least 8 characters long and contain letters and numbers.', 'danger')
            return render_template('register.html')

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # Verify current password
        if not check_password_hash(current_user.password_hash, form.current_password.data):
            flash('Current password is incorrect.', 'danger')
        else:
            # Update the password
            current_user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated successfully.', 'success')
            return redirect(url_for('main.settings'))
    elif form.errors:
        flash('Please correct the errors in the form.', 'danger')
    # Fetch favorite places from the database
    favorite_places = []
    if current_user.is_authenticated and current_user.favorite_places:
        favorite_places = current_user.get_favorite_places()

    return render_template('settings.html', form=form, favorite_places=favorite_places)

@main.route('/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    data = request.get_json()
    if not data or 'favorite_place' not in data:
        return jsonify({'success': False, 'message': 'No favorite place provided'}), 400

    new_place = data['favorite_place'].strip()
    #print("New Place: " + str(new_place) + "    Type: " + str(type(new_place)))
    if new_place:
        if new_place not in current_user.get_favorite_places():
            current_user.add_favorite_place(new_place)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Favorite place already exists'}), 400
    else:
        return jsonify({'success': False, 'message': 'Please enter a valid location.'}), 400

@main.route('/remove_favorite', methods=['POST'])
@login_required
def remove_favorite():
    data = request.get_json()
    if not data or 'place_to_remove' not in data:
        return jsonify({'success': False, 'message': 'No place to remove provided'}), 400

    place_to_remove = data['place_to_remove'].strip()
    if place_to_remove in current_user.get_favorite_places():
        current_user.remove_favorite_place(place_to_remove)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Location not found in your favorites.'}), 400


@main.route('/get_favorites', methods=['GET'])
@login_required
def get_favorites():
    favorite_places = []
    if current_user.favorite_places:
        favorite_places = current_user.get_favorite_places()
    return jsonify({'favorite_places': favorite_places})


@main.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = current_user
    db.session.delete(user)
    db.session.commit()
    logout_user()
    flash('Your account has been deleted.', 'success')
    return redirect(url_for('main.home'))

@main.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('term', '')
    results = stops[stops['stop_name'].str.contains(search, case=False, na=False)]
    suggestions = [
        {'label': row['stop_name'], 'value': row['stop_id']}
        for idx, row in results.iterrows()
    ]
    return jsonify(suggestions)

@main.route('/map')
def map_view():
    # Filter stops within a bounding box or limit to the first N stops
    # Example: Limit to stops within certain latitude and longitude bounds
    lat, lon = 35.958530, -83.924637
    bound = .02
    lat_min, lat_max = lat-bound, lat+bound
    lon_min, lon_max = lon-bound, lon+bound

    filtered_stops = stops[
        (stops['stop_lat'] >= lat_min) &
        (stops['stop_lat'] <= lat_max) &
        (stops['stop_lon'] >= lon_min) &
        (stops['stop_lon'] <= lon_max)
    ]
    print("Stops: " + str(len(stops)))
    print("Filtered Stops: " + str(len(filtered_stops)))
    stops_list = filtered_stops.to_dict('records')

    favorite_places = []
    if current_user.is_authenticated and current_user.favorite_places:
        favorite_places = current_user.get_favorite_places()

    return render_template('map.html', stops=stops_list, favorite_places=favorite_places)


@main.route('/stop/<stop_id>')
def stop_detail(stop_id):
    def seconds_to_time_str(seconds):
        h = int(seconds // 3600) % 24
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    # Load GTFS data
    stops = pd.read_csv('gtfs/stops.txt', dtype={'stop_id': str})
    stop_times = pd.read_csv('gtfs/stop_times.txt', dtype={'trip_id': str, 'stop_id': str})
    trips = pd.read_csv('gtfs/trips.txt', dtype={'trip_id': str, 'route_id': str})
    routes = pd.read_csv('gtfs/routes.txt', dtype={'route_id': str})
    calendar = pd.read_csv('gtfs/calendar.txt', dtype={'service_id': str})
    calendar_dates = pd.read_csv('gtfs/calendar_dates.txt', dtype={'service_id': str})

    # Get stop details
    stop = stops[stops['stop_id'] == stop_id].iloc[0]

    # Get trips that serve this stop
    stop_trips = stop_times[stop_times['stop_id'] == stop_id]['trip_id'].unique()
    trips_serving_stop = trips[trips['trip_id'].isin(stop_trips)]

    # Get routes serving the stop
    routes_serving_stop = routes[routes['route_id'].isin(trips_serving_stop['route_id'].unique())].to_dict('records')

    # Get upcoming arrivals
    now = datetime.now()
    current_time_seconds = now.hour * 3600 + now.minute * 60 + now.second

    # Convert times to seconds since midnight
    stop_times['arrival_seconds'] = stop_times['arrival_time'].apply(time_to_seconds)
    stop_times['departure_seconds'] = stop_times['departure_time'].apply(time_to_seconds)

    # Filter for the selected stop and times after current time
    upcoming_arrivals = stop_times[
        (stop_times['stop_id'] == stop_id) &
        (stop_times['departure_seconds'] >= current_time_seconds)
    ].sort_values('departure_seconds')

    # Merge with trips to get route information
    upcoming_arrivals = upcoming_arrivals.merge(trips, on='trip_id')
    upcoming_arrivals = upcoming_arrivals.merge(routes, on='route_id')

    # Limit to next 10 arrivals
    upcoming_arrivals = upcoming_arrivals.head(10)

    # Format arrival times
    upcoming_arrivals['formatted_departure'] = upcoming_arrivals['departure_seconds'].apply(seconds_to_time_str)

    # Prepare data for template
    arrivals_list = upcoming_arrivals.to_dict('records')

    return render_template(
        'stop_detail.html',
        stop=stop,
        routes=routes_serving_stop,
        arrivals=arrivals_list
    )


@main.route('/find_route', methods=['POST'])
def find_route():
    logging.debug("Received request to find route.")
    # Get the start and end stop names from the form
    start_stop_name = request.form['start_stop']
    end_stop_name = request.form['end_stop']

    # Find the stop IDs based on the stop names
    start_stop = stops[stops['stop_name'] == start_stop_name]
    end_stop = stops[stops['stop_name'] == end_stop_name]

    if start_stop.empty or end_stop.empty:
        return jsonify({'error': 'One or both stops not found.'}), 400

    start_stop_id = start_stop['stop_id'].iloc[0]
    end_stop_id = end_stop['stop_id'].iloc[0]

    # Get current time in seconds since midnight
    now = datetime.now()
    current_time_seconds = now.hour * 3600 + now.minute * 60 + now.second

    # Access the graph
    G = current_app.config.get('graph')
    if G is None:
        G = build_graph()
        current_app.config['graph'] = G

    logging.debug(f"Finding path from {start_stop_id} to {end_stop_id} at time {current_time_seconds}.")

    # Call find_earliest_path
    path = find_earliest_path(G, start_stop_id, end_stop_id, current_time_seconds)
    if path is None:
        logging.debug("No path found.")
        return jsonify({'error': 'No available path found.'}), 400

    logging.debug("Path found successfully.")

    # Save route history if user is logged in
    if current_user.is_authenticated:
        new_history = RouteHistory(
            user_id=current_user.id,
            start_stop=start_stop_name,
            end_stop=end_stop_name
        )
        db.session.add(new_history)
        db.session.commit()

    # Extract trip segments
    trip_segments = []
    for i in range(len(path) - 1):
        from_node = path[i]
        to_node = path[i + 1]

        from_stop_id, departure_time = from_node
        to_stop_id, arrival_time = to_node

        from_stop_data = stops[stops['stop_id'] == from_stop_id].iloc[0]
        to_stop_data = stops[stops['stop_id'] == to_stop_id].iloc[0]

        # Get edge data
        edge_data = G.get_edge_data(from_node, to_node)
        # Since it's a MultiDiGraph, edge_data is a dict
        edge_attrs = edge_data[list(edge_data.keys())[0]]

        segment = {
            'from_stop_id': str(from_stop_id),
            'to_stop_id': str(to_stop_id),
            'from_stop_name': str(from_stop_data['stop_name']),
            'to_stop_name': str(to_stop_data['stop_name']),
            'departure_time': int(departure_time % (24 * 3600)), # Modulo for times beyond midnight
            'arrival_time': int(arrival_time % (24 * 3600)),
            'duration': int((arrival_time - departure_time) % (24 * 3600)),
            'from_stop_lat': float(from_stop_data['stop_lat']),
            'from_stop_lon': float(from_stop_data['stop_lon']),
            'to_stop_lat': float(to_stop_data['stop_lat']),
            'to_stop_lon': float(to_stop_data['stop_lon']),
            'trip_id': str(edge_attrs.get('trip_id')) if edge_attrs.get('trip_id') else None,
            'transfer': bool(edge_attrs.get('transfer', False))
        }

        '''
        # Debug statements to print out the types
        for key, value in segment.items():
            print(f"{key}: {value} ({type(value)})")
        '''

        trip_segments.append(segment)

    # Return the route information as JSON
    return jsonify({
        'trip_segments': trip_segments
    })

@main.route('/plan_trip', methods=['POST'])
def plan_trip():
    start_stop_name = request.form['start_stop']
    end_stop_name = request.form['end_stop']

    # Query the stops to find IDs based on names
    stops = pd.read_csv('gtfs/stops.txt')
    start_stop = stops[stops['stop_name'] == start_stop_name].iloc[0]
    end_stop = stops[stops['stop_name'] == end_stop_name].iloc[0]

    # For simplicity, we'll just return the IDs
    return f"Start Stop ID: {start_stop['stop_id']}, End Stop ID: {end_stop['stop_id']}"


@main.route('/send-route-info', methods=['POST'])
def send_route_info():
    # Logic here
    return jsonify({'success': True})

@main.route('/get_history', methods=['GET'])
@login_required
def get_history():
    histories = RouteHistory.query.filter_by(user_id=current_user.id).order_by(RouteHistory.timestamp.desc()).limit(10).all()
    history_list = []
    for history in histories:
        history_list.append({
            'start_stop': history.start_stop,
            'end_stop': history.end_stop,
            'timestamp': history.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify({'success': True, 'history': history_list})


@main.route('/send-real-time-location', methods=['POST'])
def send_real_time_location():
    # Logic here
    data = request.get_json()
    if not data or 'latitude' not in data or 'longitude' not in data:
        return jsonify({'success': False, 'message': 'Location data missing'}), 400

    latitude = data['latitude']
    longitude = data['longitude']
    # You could log or store the current location here if needed, e.g., in the database.

    return jsonify({'success': True, 'latitude': latitude, 'longitude': longitude})
    # return jsonify({'success': True})


@main.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')

    # Verify current password
    if not check_password_hash(current_user.password_hash, current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('main.settings'))

    # Check if new passwords match
    if new_password != confirm_new_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('main.settings'))

    # Validate new password strength (optional but recommended)
    if len(new_password) < 8:
        flash('New password must be at least 8 characters long.', 'danger')
        return redirect(url_for('main.settings'))
    # Add more password strength validations as needed

    # Update the user's password
    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    flash('Your password has been updated successfully.', 'success')
    return redirect(url_for('main.settings'))