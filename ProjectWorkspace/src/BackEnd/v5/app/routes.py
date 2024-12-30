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
from .graph_utils import build_graph, find_earliest_path, time_to_seconds, get_nearest_stops
from app.forms import ChangePasswordForm
import logging
from difflib import get_close_matches
import requests


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
    results = stops[stops['stop_name'].str.contains(search, case=False, na=False)].head(10)
    suggestions = results['stop_name'].unique().tolist()
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
    
    # Add logging to check stops_list
    print("Number of stops being passed to template:", len(stops_list))

    return render_template('map.html', stops=stops_list, favorite_places=favorite_places)


@main.route('/stop/<stop_id>')
def stop_detail(stop_id):
    import pandas as pd
    import logging

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    # Ensure stop_id is a string and strip any whitespace
    stop_id = str(stop_id).strip()
    logging.debug(f"Received stop_id: '{stop_id}'")

    # Load stops data with stop_id as string
    try:
        stops = pd.read_csv('gtfs/stops.txt', dtype={'stop_id': str})
        logging.debug(f"Loaded stops data with {len(stops)} stops.")
    except FileNotFoundError:
        flash('Stops data not found.', 'danger')
        logging.error("gtfs/stops.txt not found.")
        return redirect(url_for('main.map_view'))
    except Exception as e:
        flash(f'Error reading stops data: {e}', 'danger')
        logging.error(f"Error reading stops.txt: {e}")
        return redirect(url_for('main.map_view'))

    # Find the specific stop
    bus_stop = stops[stops['stop_id'] == stop_id]
    logging.debug(f"Found {len(bus_stop)} stops with stop_id '{stop_id}'.")

    if bus_stop.empty:
        flash('Bus stop not found.', 'danger')
        logging.warning(f"Bus stop with stop_id '{stop_id}' not found.")
        return redirect(url_for('main.map_view'))

    bus_stop = bus_stop.iloc[0].to_dict()
    logging.debug(f"Bus Stop Details: {bus_stop}")

    # For simplicity, we'll skip fetching nearby landmarks and use placeholders
    detailed_stop = {
        "stop_id": bus_stop['stop_id'],
        "stop_name": bus_stop['stop_name'],
        "location": {
            "latitude": bus_stop['stop_lat'],
            "longitude": bus_stop['stop_lon']
        },
        "nearby_landmarks": ["N/A"],  # Simplified
        "accessibility": "Wheelchair accessible",
        "shelter_availability": "Available",
        "recent_notices": "Construction on nearby roads until May.",
        "upcoming_arrivals": [
            {"bus_number": "5A", "destination": "Downtown", "arrival_time": "10:15 AM"},
            {"bus_number": "12B", "destination": "Uptown", "arrival_time": "10:20 AM"}
        ],
        "bus_routes": ["5A", "12B", "7C"]
    }

    logging.debug(f"Rendering template with bus_stop: {detailed_stop}")

    return render_template('stop_detail.html', bus_stop=detailed_stop)


@main.route('/list_stops')
def list_stops():
    import pandas as pd
    try:
        stops = pd.read_csv('gtfs/stops.txt', dtype={'stop_id': str})
        stop_ids = stops['stop_id'].unique().tolist()
        return jsonify({'stop_ids': stop_ids})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_nearby_landmarks(latitude, longitude, radius=500):
    """
    Fetch nearby landmarks using OpenStreetMap's Overpass API.
    :param latitude: Latitude of the bus stop
    :param longitude: Longitude of the bus stop
    :param radius: Search radius in meters
    :return: List of landmark names
    """
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node(around:{radius},{latitude},{longitude})["tourism"~"museum|park|attraction"];
      way(around:{radius},{latitude},{longitude})["tourism"~"museum|park|attraction"];
      relation(around:{radius},{latitude},{longitude})["tourism"~"museum|park|attraction"];
    );
    out center;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    if response.status_code != 200:
        print("Error fetching landmarks:", response.status_code)
        return []
    
    data = response.json()
    landmarks = set()
    for element in data['elements']:
        if 'tags' in element and 'name' in element['tags']:
            landmarks.add(element['tags']['name'])
    return list(landmarks)[:5]  # Limit to top 5 landmarks



@main.route('/find_route', methods=['POST'])
def find_route():
    logging.debug("Received request to find route.")

    def find_closest(start_stop_name):
        # calculate using the haversine formula:
        
        # Get the start and end stop names from the form
        #start_stop_name = request.form['start_stop']
        #end_stop_name = request.form['end_stop']

        # Load the stops data
        stops = pd.read_csv('gtfs/stops.txt')

        # setting up googlemaps api
        import googlemaps
        # how do we hide this?
        gmaps = googlemaps.Client(key='AIzaSyB9xZcHzm8QOnopWvcPuPbdcv5c1yxFcSM')

        # turn user input of addresses into geocodes, 
        # then use that as lat1, lon1
        # these only get used if the user inputs places not in the KAT system
        user_start = gmaps.geocode(start_stop_name)
        
        # checking if addresses are valid.
        if user_start == []:
            return pd.DataFrame()
        # gets info for start and end stops
        import math as m
        startdist = 2000000000
        start_stop = pd.Series

        # start address's closest bus stop:
        if not(start_stop_name in stops['stop_name'].values):
            # loop through the stop data, save the lowest distance's name.
            lat1 = m.radians(user_start[0]['geometry']['location']['lat'])
            lon1 = m.radians(user_start[0]['geometry']['location']['lng'])
            logging.debug(lat1)
            logging.debug(lon1)
            # iterate thru the stops, calculating the distance using 
            # a modified version of the haversine formula found here:
            # https://community.fabric.microsoft.com/t5/Desktop/How-to-calculate-lat-long-distance/td-p/1488227
            for s in stops['stop_name'].values:
                # need to convert to radians
                lon2 = m.radians(stops[stops['stop_name'] == s]['stop_lon'].iloc[0])
                lat2 = m.radians(stops[stops['stop_name'] == s]['stop_lat'].iloc[0])
                # distance in miles
                dist = m.acos(m.sin(lat1)*m.sin(lat2)+m.cos(lat1)*m.cos(lat2)*m.cos(lon2-lon1))*3958.8
                # compare distance against the current min, adjust variables as needed
                if dist < startdist:
                    startdist = dist
                    start_stop_name = s
                    start_stop = stops[stops['stop_name'] == s]

            print(f"Start: {start_stop_name}")
            print(f"Start ID: {stops[stops['stop_name'] == start_stop_name]['stop_id'].iloc[0]}")

        else:
            start_stop = stops[stops['stop_name'] == start_stop_name]

        return start_stop
    

    # Get the start and end stop names from the form
    start_stop_name = request.form['start_stop'].strip()
    end_stop_name = request.form['end_stop'].strip()
    first_name = start_stop_name
    last_name = end_stop_name
    # Prepare a list of all stop names in lowercase
    stop_names = stops['stop_name'].str.lower().tolist()

    # Function to find the best matching stop name
    def get_best_match(input_name):
        exact_matches = stops[stops['stop_name'].str.lower() == input_name.lower()]
        if not exact_matches.empty:
            return exact_matches
        else:
            close_matches = get_close_matches(input_name.lower(), stop_names, n=1, cutoff=0.7)
            if close_matches:
                matched_name = close_matches[0]
                return stops[stops['stop_name'].str.lower() == matched_name]
            else:
                return pd.DataFrame()  # Empty DataFrame

    # Get start stop
    start_stop = get_best_match(start_stop_name)
    
    changed_start_stop = False
    changed_end_stop = False

    if start_stop.empty:
        # add another stop using important piped into from google maps.
        start_stop = find_closest(start_stop_name=start_stop_name)
        if start_stop.empty:
            flash('Start stop not found.', 'danger')
            return redirect(url_for('main.map_view'))
        changed_start_stop = True
    
    start_stop_id = start_stop['stop_id'].iloc[0]
    start_stop_name = start_stop['stop_name'].iloc[0]  # Update to matched name

    # Get end stop
    end_stop = get_best_match(end_stop_name)
    if end_stop.empty:
        end_stop = find_closest(start_stop_name=end_stop_name)
        if end_stop.empty:
            flash('End stop not found.', 'danger')
            return redirect(url_for('main.map_view'))
        changed_end_stop = True
        
    end_stop_id = end_stop['stop_id'].iloc[0]
    end_stop_name = end_stop['stop_name'].iloc[0]  # Update to matched name

    # Get current time in seconds since midnight
    now = request.form['time_input']
    current_time_seconds = 0
    if now == '':
        now = datetime.now()
        current_time_seconds = now.hour * 3600 + now.minute * 60 + now.second
    else:
        now = datetime.strptime(now, "%H:%M").time()
        current_time_seconds = now.hour * 3600 + now.minute * 60

    # Access the graph
    G = current_app.config.get('graph')
    if G is None:
        G = build_graph()
        current_app.config['graph'] = G

    # Initialize variables
    path = None
    attempts = 0
    max_attempts = 20

    # Get the list of nearest stops to the start_stop_id (excluding the original stop)
    nearest_stops = get_nearest_stops(str(start_stop_id), stops, num_stops=max_attempts)
    # Include the original stop at the beginning
    candidate_start_stops = [str(start_stop_id)] + nearest_stops

    for candidate_start_stop_id in candidate_start_stops:
        attempts += 1
        logging.debug(f"Attempt {attempts}: Trying start stop ID {candidate_start_stop_id}.")
        path = find_earliest_path(G, candidate_start_stop_id, str(end_stop_id), current_time_seconds)
        if path is not None:
            logging.debug(f"Path found starting from stop ID {candidate_start_stop_id}.")
            # Update start_stop_id and start_stop_name to the one we actually used
            start_stop_id = candidate_start_stop_id
            start_stop_name = stops[stops['stop_id'] == start_stop_id]['stop_name'].iloc[0]
            break
        else:
            logging.debug(f"No path found from stop ID {candidate_start_stop_id}.")
        if attempts >= max_attempts:
            break

    if path is None:
        logging.debug("No path found after multiple attempts.")
        flash('No available path found from nearby stops.', 'danger')
        return redirect(url_for('main.map_view'))

    # Save route history if user is logged in
    if current_user.is_authenticated:
        new_history = RouteHistory(
            user_id=current_user.id,
            start_stop=start_stop_name,
            end_stop=end_stop_name
        )
        db.session.add(new_history)
        db.session.commit()

    # Define helper functions
    def seconds_to_time_str(seconds):
        h = int(seconds // 3600) % 24
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def format_duration(duration_in_seconds):
        hours = duration_in_seconds // 3600
        minutes = (duration_in_seconds % 3600) // 60
        seconds = duration_in_seconds % 60
        if hours > 0:
            return f"{hours} hr {minutes} min {seconds} sec"
        elif minutes > 0:
            return f"{minutes} min {seconds} sec"
        else:
            return f"{seconds} sec"



    # Extract trip segments
    trip_segments = []

    # Add travel to from actual start/end location to nearest stop, if needed.
    # Time travel will be zero; However, we should indicate the user should
    # be at the first stop by the set time.
    
    if changed_start_stop:
 
        #from_stop_id, departure_time = from_node
        to_stop_id, arrival_time = path[0]

        #from_stop_data = stops[stops['stop_id'] == from_stop_id].iloc[0]
        
        to_stop_data = stops[stops['stop_id'] == to_stop_id].iloc[0]

        segment = {
            'from_stop_id': str(0),
            'to_stop_id': str(path[0]),
            'from_stop_name': first_name,
            'to_stop_name': str(to_stop_data['stop_name']),
            'departure_time': 0,
            'arrival_time': int(arrival_time % (24 * 3600)),
            'duration': 0,
            'from_stop_lat': float(start_stop['stop_lat'].iloc[0]),
            'from_stop_lon': float(start_stop['stop_lon'].iloc[0]),
            'to_stop_lat': float(to_stop_data['stop_lat']),
            'to_stop_lon': float(to_stop_data['stop_lon']),
            'trip_id': None,
            'transfer': True, #bool(edge_attrs.get('transfer', False)),
            'departure_time_str': 'Arrive by:',
            'arrival_time_str': seconds_to_time_str(arrival_time % (24 * 3600)),
        }

        trip_segments.append(segment)


    total_travel_time = 0
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
            'departure_time': int(departure_time % (24 * 3600)),
            'arrival_time': int(arrival_time % (24 * 3600)),
            'duration': int((arrival_time - departure_time) % (24 * 3600)),
            'from_stop_lat': float(from_stop_data['stop_lat']),
            'from_stop_lon': float(from_stop_data['stop_lon']),
            'to_stop_lat': float(to_stop_data['stop_lat']),
            'to_stop_lon': float(to_stop_data['stop_lon']),
            'trip_id': str(edge_attrs.get('trip_id')) if edge_attrs.get('trip_id') else None,
            'transfer': bool(edge_attrs.get('transfer', False)),
            'departure_time_str': seconds_to_time_str(departure_time % (24 * 3600)),
            'arrival_time_str': seconds_to_time_str(arrival_time % (24 * 3600)),
        }

        total_travel_time += segment['duration']
        trip_segments.append(segment)

    if changed_end_stop:
        size = len(path)-1

        from_stop_id, departure_time = path[size]
        from_stop_data = stops[stops['stop_id'] == from_stop_id].iloc[0]

        segment = {
            'from_stop_id': str(0),
            'to_stop_id': str(path[size]),
            'from_stop_name': str(from_stop_data['stop_name']),
            'to_stop_name': last_name,
            'departure_time': int(departure_time % (24 * 3600)),
            'arrival_time': 0,
            'duration': 0,
            'from_stop_lat': float(from_stop_data['stop_lat']),
            'from_stop_lon': float(from_stop_data['stop_lon']),
            'to_stop_lat': float(end_stop['stop_lat'].iloc[0]),
            'to_stop_lon': float(end_stop['stop_lon'].iloc[0]),
            'trip_id': None,
            'transfer': True, #bool(edge_attrs.get('transfer', False)),
            'departure_time_str': seconds_to_time_str(departure_time % (24 * 3600)),
            'arrival_time_str': 'Continue on...',
        }

        trip_segments.append(segment)

    # Convert total_travel_time to a string
    total_travel_time_str = format_duration(total_travel_time)

    return render_template('trip_plan.html', trip_segments=trip_segments, total_travel_time=total_travel_time_str)




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
            'id': history.id,  # Include the ID
            'start_stop': history.start_stop,
            'end_stop': history.end_stop,
            'timestamp': history.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify({'success': True, 'history': history_list})

@main.route('/delete_history_item', methods=['POST'])
@login_required
def delete_history_item():
    data = request.get_json()
    if not data or 'history_id' not in data:
        return jsonify({'success': False, 'message': 'No history ID provided'}), 400
    
    history_id = data['history_id']
    history_item = RouteHistory.query.filter_by(id=history_id, user_id=current_user.id).first()
    if history_item:
        db.session.delete(history_item)
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'History item not found.'}), 404


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