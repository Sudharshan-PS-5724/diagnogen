import streamlit as st
import pymongo
import openrouteservice

# MongoDB setup
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["hospital_finder"]
hospitals_collection = db["hospitals"]

# OpenRouteService API setup
ORS_API_KEY = "5b3ce3597851110001cf624837b70452bcba4a858f61802bdcc59194"  # Replace with your OpenRouteService API key
ors_client = openrouteservice.Client(key=ORS_API_KEY)

# Function to get distance and duration between two locations
def get_distance_and_duration(origin, destination):
    coordinates = [[origin[1], origin[0]], [destination[1], destination[0]]]
    route = ors_client.directions(coordinates=coordinates, profile='driving-car', format='geojson')
    distance = route['features'][0]['properties']['segments'][0]['distance']
    duration = route['features'][0]['properties']['segments'][0]['duration']
    return distance, duration

# Function to find the nearest hospital using A* search (simplified version)
def find_nearest_hospital(user_location):
    hospitals = list(hospitals_collection.find())  # Retrieve all hospitals from MongoDB
    closest_hospital = None
    min_distance = float('inf')
    min_duration = float('inf')

    for hospital in hospitals:
        hospital_location = (hospital["latitude"], hospital["longitude"])
        distance, duration = get_distance_and_duration(user_location, hospital_location)
        
        if distance < min_distance:  # Check if this hospital is closer
            min_distance = distance
            min_duration = duration
            closest_hospital = hospital

    return closest_hospital, min_distance, min_duration

# Streamlit UI
st.title("Find Nearest Hospital")

# Input from the user
latitude = st.number_input("Enter your Latitude:", value=12.9716)
longitude = st.number_input("Enter your Longitude:", value=77.5946)

user_location = (latitude, longitude)

if st.button("Find Nearest Hospital"):
    closest_hospital, distance, duration = find_nearest_hospital(user_location)
    
    if closest_hospital:
        st.write(f"**Nearest Hospital**: {closest_hospital['name']}")
        st.write(f"**Distance**: {distance / 1000:.2f} km")
        st.write(f"**Duration**: {duration / 60:.2f} minutes")
    else:
        st.error("No hospitals found in the database.")
