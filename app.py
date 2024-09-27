from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import requests

app = Flask(__name__)

# Function to calculate distance based on latitude and longitude
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat / 2) ** 2 +
         np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c
    return distance

# Function to get latitude and longitude from a location name using Nominatim API
def get_lat_lon(location_name):
    response = requests.get(f'https://nominatim.openstreetmap.org/search?q={location_name}&format=json')
    if response.status_code == 200 and response.json():
        location = response.json()[0]
        return float(location['lat']), float(location['lon'])
    return None, None

@app.route('/')
def index():
    return render_template('one.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    selected_food_item = data.get('food_item')
    pickup_location_name = data.get('pickup_location')
    destination_name = data.get('destination')

    # Get pickup latitude and longitude
    pickup_lat, pickup_lon = get_lat_lon(pickup_location_name)
    
    # Get destination latitude and longitude
    destination_lat, destination_lon = get_lat_lon(destination_name)

    if pickup_lat is None or pickup_lon is None:
        return jsonify({'error': 'Invalid pickup location'}), 400
    
    if destination_lat is None or destination_lon is None:
        return jsonify({'error': 'Invalid destination'}), 400

    # Load the restaurant data
    restaurant_data = pd.read_csv('./data/restaurant_data.csv')  # Adjust the path if needed

    results = []

    for index, row in restaurant_data.iterrows():
        if row['food_item'].lower() == selected_food_item.lower():
            restaurant_location = (row['latitude'], row['longitude'])
            distance = calculate_distance(pickup_lat, pickup_lon, restaurant_location[0], restaurant_location[1])
            
            # Calculate estimated time of arrival (6 minutes per kilometer)
            estimated_arrival_time = distance * 6
            
            # Check if the estimated arrival time is greater than or equal to the preparation time
            if estimated_arrival_time >= row['prep_time'] and row['is_on_route'] == 'Yes':
                results.append({
                    'restaurant_name': row['restaurant_name'],
                    'estimated_time_of_arrival': estimated_arrival_time
                })

    return jsonify(results)

if __name__ == '_main_':
    app.run(debug=True)