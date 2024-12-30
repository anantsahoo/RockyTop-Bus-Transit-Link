from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, g, current_app
from flask_login import login_user, logout_user, login_required, current_user
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, timedelta
import re
import pandas as pd
import networkx as nx
from .models import User, db
from .graph_utils import build_graph, find_earliest_path, time_to_seconds


# Read GTFS data
stops = pd.read_csv('gtfs/stops.txt', dtype={'stop_id': str})
stop_times = pd.read_csv('gtfs/stop_times.txt', dtype={'trip_id': str, 'stop_id': str})
trips = pd.read_csv('gtfs/trips.txt', dtype={'trip_id': str, 'route_id': str})
routes = pd.read_csv('gtfs/routes.txt', dtype={'route_id': str})

# Parse arrival and departure times
stop_times['arrival_seconds'] = stop_times['arrival_time'].apply(time_to_seconds)
stop_times['departure_seconds'] = stop_times['departure_time'].apply(time_to_seconds)

# Sort stop_times by trip_id and stop_sequence
stop_times.sort_values(['trip_id', 'stop_sequence'], inplace=True)

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return redirect(url_for('main.map_view'))

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
            return render_template('login.html')
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

@main.route('/settings', methods=['GET'])
@login_required
def settings():
    # Retrieve user's favorite places
    if current_user.favorite_places:
        favorite_places = [place.strip() for place in current_user.favorite_places.split(',')]
    else:
        favorite_places = []
    return render_template('settings.html', favorite_places=favorite_places)

@main.route('/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    new_place = request.form['favorite_place'].strip()
    if new_place:
        # Add the new place to the user's favorite_places
        if current_user.favorite_places:
            places = [place.strip() for place in current_user.favorite_places.split(',')]
            if new_place not in places:
                places.append(new_place)
                current_user.favorite_places = ', '.join(places)
        else:
            current_user.favorite_places = new_place
        db.session.commit()
        flash('Favorite location added.', 'success')
    else:
        flash('Please enter a valid location.', 'danger')
    return redirect(url_for('main.settings'))

@main.route('/remove_favorite', methods=['POST'])
@login_required
def remove_favorite():
    place_to_remove = request.form['place_to_remove'].strip()
    if current_user.favorite_places:
        places = [place.strip() for place in current_user.favorite_places.split(',')]
        if place_to_remove in places:
            places.remove(place_to_remove)
            current_user.favorite_places = ', '.join(places) if places else None
            db.session.commit()
            flash('Favorite location removed.', 'success')
        else:
            flash('Location not found in your favorites.', 'danger')
    else:
        flash('You have no favorite locations to remove.', 'danger')
    return redirect(url_for('main.settings'))

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
    bound = .05
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
        favorite_places = [place.strip() for place in current_user.favorite_places.split(',')]

    return render_template('map.html', stops=stops_list, favorite_places=favorite_places)

@main.route('/plan_trip', methods=['POST'])
def plan_trip():
    start_stop_id = request.form.get('start_stop_id')
    end_stop_id = request.form.get('end_stop_id')

    if not start_stop_id or not end_stop_id:
        flash('Please select valid start and end stops from the suggestions.', 'danger')
        return redirect(url_for('main.map_view'))

    # Convert current time to seconds since midnight
    now = datetime.now()
    current_time_seconds = now.hour * 3600 + now.minute * 60 + now.second

    # Build or load the graph (cache it to improve performance)
    if 'graph' not in g:
        g.graph = build_graph()
    G = current_app.config['graph']

    # Find the earliest path
    path = find_earliest_path(G, start_stop_id, end_stop_id, current_time_seconds)

    if not path:
        flash('No available routes found.', 'danger')
        return redirect(url_for('main.map_view'))

    # Extract trip segments and stops
    trip_segments = []
    for i in range(len(path) - 1):
        from_node = path[i]
        to_node = path[i + 1]
        edge_data = G.get_edge_data(from_node, to_node)
        trip_segments.append({
            'from_stop_id': from_node[0],
            'to_stop_id': to_node[0],
            'departure_time': from_node[1],
            'arrival_time': to_node[1],
            'duration': edge_data['weight']
        })

    # Prepare data for rendering
    # Load stops data (you can cache this as well)
    stops = pd.read_csv('gtfs/stops.txt', dtype={'stop_id': str})
    stop_details = stops.set_index('stop_id').to_dict('index')

    # Convert times back to HH:MM:SS format
    for segment in trip_segments:
        segment['from_stop_name'] = stop_details[segment['from_stop_id']]['stop_name']
        segment['to_stop_name'] = stop_details[segment['to_stop_id']]['stop_name']
        segment['departure_time_str'] = str(timedelta(seconds=segment['departure_time']))
        segment['arrival_time_str'] = str(timedelta(seconds=segment['arrival_time']))
        segment['from_stop_lat'] = stop_details[segment['from_stop_id']]['stop_lat']
        segment['from_stop_lon'] = stop_details[segment['from_stop_id']]['stop_lon']
        segment['to_stop_lat'] = stop_details[segment['to_stop_id']]['stop_lat']
        segment['to_stop_lon'] = stop_details[segment['to_stop_id']]['stop_lon']

    # Calculate total travel time
    total_travel_time = int(path[-1][1] - path[0][1])
    total_travel_time_str = str(timedelta(seconds=total_travel_time))

    return render_template('trip_plan.html', trip_segments=trip_segments, total_travel_time=total_travel_time_str)


@main.route('/stop/<stop_id>')
def stop_detail(stop_id):
    #print(f"Received stop_id: {stop_id} (type: {type(stop_id)})")

    # Read stop_id as string
    stop = stops[stops['stop_id'] == stop_id]

    #print(f"DataFrame stop_id types: {stops['stop_id'].dtype}")
    #print(f"Available stop_ids: {stops['stop_id'].unique()}")

    if stop.empty:
        flash('Stop not found.', 'danger')
        return redirect(url_for('main.map_view'))

    stop = stop.iloc[0].to_dict()

    # Read stop_times.txt with stop_id and trip_id as strings
    stop_times = pd.read_csv('gtfs/stop_times.txt', dtype={'stop_id': str, 'trip_id': str})
    trips = stop_times[stop_times['stop_id'] == stop_id]['trip_id'].unique()

    # Read trips.txt with trip_id and route_id as strings
    trips_df = pd.read_csv('gtfs/trips.txt', dtype={'trip_id': str, 'route_id': str})
    routes = trips_df[trips_df['trip_id'].isin(trips)]['route_id'].unique()

    # Read routes.txt with route_id as string
    routes_df = pd.read_csv('gtfs/routes.txt', dtype={'route_id': str})
    route_details = routes_df[routes_df['route_id'].isin(routes)]

    route_list = route_details.to_dict('records')

    return render_template('stop_detail.html', stop=stop, routes=route_list)


def time_to_seconds(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s


def parse_time(time_str):
    h, m, s = map(int, time_str.split(':'))
    if h >= 24:
        h -= 24
        return datetime.combine(datetime.today() + timedelta(days=1), datetime.min.time()) + timedelta(hours=h, minutes=m, seconds=s)
    else:
        return datetime.combine(datetime.today(), datetime.min.time()) + timedelta(hours=h, minutes=m, seconds=s)

def find_routes(start_stop_id, end_stop_id, current_time):
    # Convert current time to seconds since midnight
    current_time_seconds = time_to_seconds(current_time)

    # Filter stop_times for the starting stop
    start_stop_times = stop_times[stop_times['stop_id'] == start_stop_id]
    start_stop_times['arrival_seconds'] = start_stop_times['arrival_time'].apply(time_to_seconds)

    # Filter for times after the current time
    future_start_times = start_stop_times[start_stop_times['arrival_seconds'] >= current_time_seconds]

    # Get trips that start at the start_stop after the current time
    possible_trips = future_start_times['trip_id'].unique()

    valid_trips = []
    for trip_id in possible_trips:
        trip_stop_times = stop_times[stop_times['trip_id'] == trip_id]
        trip_stop_times = trip_stop_times.sort_values('stop_sequence')
        stop_ids = trip_stop_times['stop_id'].tolist()

        # Check if the end_stop comes after the start_stop in the trip
        if start_stop_id in stop_ids and end_stop_id in stop_ids:
            start_index = stop_ids.index(start_stop_id)
            end_index = stop_ids.index(end_stop_id)
            if end_index > start_index:
                valid_trips.append(trip_id)

    return valid_trips

