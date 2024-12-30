import pandas as pd
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return redirect(url_for('main.map_view'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.map_view'))
        else:
            # It's a good practice to return to the login page with an error message.
            flash("Invalid username or password", 'danger')
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
    stops = pd.read_csv('gtfs/stops.txt')
    results = stops[stops['stop_name'].str.contains(search, case=False, na=False)]
    suggestions = [
        {'label': row['stop_name'], 'value': row['stop_id']}
        for idx, row in results.iterrows()
    ]
    return jsonify(suggestions)

@main.route('/map')
def map_view():
    # Read stops.txt
    stops = pd.read_csv('gtfs/stops.txt')

    # Filter stops within a bounding box or limit to the first N stops
    # Example: Limit to stops within certain latitude and longitude bounds
    lat, lon = 35.958530, -83.924637
    bound = .01
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

# This adds a method of finding a route between two bus stops.
# If either of the inputs are not in KAT's system of bus stops,
# Google Maps's API will be used to find a geocode, and then 
# locate the nearest KAT bus stop.
@main.route('/find_route', methods=['POST'])
def find_route():
    # Get the start and end stop names from the form
    start_stop_name = request.form['start_stop']
    end_stop_name = request.form['end_stop']

    # Load the stops data
    stops = pd.read_csv('gtfs/stops.txt')

    # setting up googlemaps api
    import googlemaps
    gmaps = googlemaps.Client(key='AIzaSyB9xZcHzm8QOnopWvcPuPbdcv5c1yxFcSM')

    # turn user input of addresses into geocodes, 
    # then use that as lat1, lon1
    # these only get used if the user inputs places not in the KAT system
    user_start = gmaps.geocode(start_stop_name)
    user_end = gmaps.geocode(end_stop_name)
    print(user_start, user_end)
    # checking if addresses are valid.
    if user_start == []:
        return jsonify({'error': 'Starting point could not be found.'}), 400
    if user_end == []:
        return jsonify({'error': 'Ending point could not be found.'}), 400

    # gets info for start and end stops
    import math as m
    startdist = 2000000000
    end_stop = pd.Series
    start_stop = pd.Series

    # start address's closest bus stop:
    if not(start_stop_name in stops['stop_name'].values):
        # loop through the stop data, save the lowest distance's name.
        lat1 = m.radians(user_start[0]['geometry']['location']['lat'])
        lon1 = m.radians(user_start[0]['geometry']['location']['lng'])
        print(lat1)
        print(lon1)
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
                start_stop = stops[stops['stop_name'] == s].iloc[0]

        print(f"Start:{start_stop_name}")
    else:
        start_stop = stops[stops['stop_name'] == start_stop_name].iloc[0]
        
    # end address's closest bus stop:
    enddist = 2000000000
    if not(end_stop_name in stops['stop_name'].values):
        # loop through the stop data, save the lowest
        # distance's name.
        lat1 = m.radians(user_end[0]['geometry']['location']['lat'])
        lon1 = m.radians(user_end[0]['geometry']['location']['lng'])
        print(lat1)
        print(lon1)
        for s in stops['stop_name'].values:
            # need to convert to radians
            lon2 = m.radians(stops[stops['stop_name'] == s]['stop_lon'].iloc[0])
            lat2 = m.radians(stops[stops['stop_name'] == s]['stop_lat'].iloc[0])
            # distance calculation in miles, this gets compared against current minDist
            dist = m.acos(m.sin(lat1)*m.sin(lat2)+m.cos(lat1)*m.cos(lat2)*m.cos(lon2-lon1))*3958.8
            # compare distance against the current min, adjust variables as needed
            if dist < enddist:
                enddist = dist
                end_stop_name = s
                end_stop = stops[stops['stop_name'] == s].iloc[0]
        print(f"End:{end_stop_name}")

    else:
        end_stop = stops[stops['stop_name'] == end_stop_name].iloc[0]

    #
    ## Possible Sprint 3 item:
    ## we should add directions to moving from start to bus 
    ## and from other bus stop to the final destination.
    #

    try:
        # no matter what happens, we end up with a bus stop.
        # these strings of bus stops have lat and long, which
        # can be passed into gmaps.directions()
        startGeo = (float(stops[stops['stop_name'] == start_stop_name]['stop_lat'].iloc[0]),
                    float(stops[stops['stop_name'] == start_stop_name]['stop_lon'].iloc[0]))
        endGeo =   (float(stops[stops['stop_name'] == end_stop_name]['stop_lat'].iloc[0]),
                    float(stops[stops['stop_name'] == end_stop_name]['stop_lon'].iloc[0]))
        
        # gets the current time b/c route calc changes with time.
        from datetime import datetime
        now = datetime.now()

        # directions takes parameter for travelMode and transitMode.
        # directions can also take (latitude, longitude) tuples for arguments.
        # Possible Sprint 3 item:
        # this line will need to be adjusted to ensure that the user only takes KAT routes.
        # this may mean creating our own method of creating directions.
        directions = gmaps.directions(startGeo, endGeo, departure_time=now, mode='transit')
        if directions == []:
            return jsonify({'error': 'Could not find route'}), 400
        
        route = directions[0]
        # Grab general information
        leg = route['legs'][0]
        distance = leg['distance']['text']
        duration = leg['duration']['text']
    
        # need to get directions:
        ways = []
        for steps in leg['steps']:
            ways.append(steps['html_instructions']+ '<br>')

        # Return the route information as JSON
        route_info = {
            'start_stop': start_stop_name,
            'end_stop': end_stop_name,
            'start_id': int(start_stop['stop_id']),
            'end_id': int(end_stop['stop_id']),
            'distance': distance,
            'time': duration,
            'directions': '\n'.join(ways)
        }
        
        return jsonify(route_info)

    except IndexError:
        return jsonify({'error': 'One or both stops not found.'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
