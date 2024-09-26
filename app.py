from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import numpy as np
import pickle

app = Flask(__name__)

# Load the saved model
model=pickle.load(open('./models/gradient_boosting_model.pkl','rb'))

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

@app.route('/')
def index():
    return render_template('one.html')  

@app.route('/predict', methods=['POST'])
def predict():
    # Get JSON data from the request
    data = request.get_json()

    # Extract necessary information from the request
    selected_food_item = data.get('food_item')
    pickup_location = (17.496654, 78.373186)  # Fixed pickup location

    # Load the restaurant data (make sure you provide the correct path)
    restaurant_data = pd.read_csv('./data/restaurant_data.csv')  # Adjust the path if needed

    # Initialize results
    results = []

    for index, row in restaurant_data.iterrows():
        if row['food_item'].lower() == selected_food_item.lower():  # Case-insensitive match
            restaurant_location = (row['latitude'], row['longitude'])
            distance = calculate_distance(pickup_location[0], pickup_location[1], restaurant_location[0], restaurant_location[1])
            
            # Calculate estimated time of arrival (6 minutes per kilometer)
            estimated_arrival_time = distance * 6
            
            # Check if the estimated arrival time is greater than or equal to the preparation time
            if estimated_arrival_time >= row['prep_time'] and row['is_on_route'] == 'Yes':
                results.append({
                    'restaurant_name': row['restaurant_name'],
                    'estimated_time_of_arrival': estimated_arrival_time
                })

    # Return the results as JSON
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
