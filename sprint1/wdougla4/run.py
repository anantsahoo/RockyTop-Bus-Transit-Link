from flask import Flask, render_template, request, jsonify
import googlemaps

app = Flask(__name__)

# Initialize the Google Maps Client with your API key
gmaps = googlemaps.Client(key='AIzaSyB9xZcHzm8QOnopWvcPuPbdcv5c1yxFcSM')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-directions', methods=['POST'])
def get_directions():
    data = request.get_json()
    start_address = data.get('start')
    end_address = data.get('end')

    # Use the Google Maps API to get directions
    directions_result = gmaps.directions(start_address, end_address)

    return jsonify(directions_result)

if __name__ == '__main__':
    app.run(debug=True)
