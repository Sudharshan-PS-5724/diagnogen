import pymongo
from bson.objectid import ObjectId
import re
from geopy.geocoders import Nominatim
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["hospital_finder"]

# Hospital and User collections
hospital_collection = db["hospitals"]
user_collection = db["users"]

def get_coordinates(location):
    """Fetches latitude and longitude for the specified location using Nominatim API."""
    geolocator = Nominatim(user_agent="hospital_finder")
    location_obj = geolocator.geocode(location)
    
    if location_obj:
        return location_obj.latitude, location_obj.longitude
    else:
        return None

### Hospital Schema and CRUD Operations ###

def register_hospital(name, locality, availability, latitude, longitude):
    hospital = {
        "name": name,
        "locality": locality,
        "availability": availability,
        "latitude": latitude,
        "longitude": longitude
    }
    hospital_id = hospital_collection.insert_one(hospital).inserted_id
    print(f"Hospital registered with ID: {hospital_id}")

def update_hospital(hospital_id, name=None, locality=None, availability=None, latitude=None, longitude=None):
    """Updates an existing hospital's details by its ID."""
    update_data = {k: v for k, v in {
        "name": name,
        "locality": locality,
        "availability": availability,
        "latitude": latitude,
        "longitude": longitude
    }.items() if v is not None}
    
    result = hospital_collection.update_one(
        {"_id": ObjectId(hospital_id)},
        {"$set": update_data}
    )
    if result.modified_count > 0:
        print(f"Hospital updated with ID: {hospital_id}")
    return result.modified_count > 0

def delete_hospital(hospital_id):
    """Deletes a hospital from the database by its ID."""
    hospital = hospital_collection.find_one({"_id": ObjectId(hospital_id)})
    if hospital:
        hospital_collection.delete_one({"_id": ObjectId(hospital_id)})
        print(f"Hospital deleted with ID: {hospital_id}")
    else:
        print(f"Hospital ID {hospital_id} not found.")

def get_all_hospitals():
    """Retrieves all hospitals from the database."""
    hospitals = list(hospital_collection.find({}))
    for hospital in hospitals:
        hospital["_id"] = str(hospital["_id"])
    return hospitals

def get_hospitals_by_locality(locality):
    """Retrieves hospitals filtered by locality."""
    hospitals = list(hospital_collection.find({"locality": locality}))
    for hospital in hospitals:
        hospital["_id"] = str(hospital["_id"])
    return hospitals

def get_hospital_by_name(name):
    """Fetches a hospital by name."""
    hospital = hospital_collection.find_one({"name": name})
    if hospital:
        hospital["_id"] = str(hospital["_id"])
    return hospital

# Find nearby hospitals
'''def get_nearby_hospitals(latitude, longitude, search_radius):
    """Finds nearby hospitals using R-tree."""
    hospital_ids = find_nearby_hospitals_rtree(latitude, longitude, search_radius)

    nearby_hospitals = []
    if hospital_ids:
        for hospital_id in hospital_ids:
            hospital = hospital_collection.find_one({'_id': ObjectId(hospital_id)})
            if hospital:
                nearby_hospitals.append({
                    'id': str(hospital['_id']),
                    'name': hospital['name'],
                    'locality': hospital['locality'],
                    'availability': hospital['availability'],
                    'latitude': hospital['latitude'],
                    'longitude': hospital['longitude']
                })
    return nearby_hospitals'''

### User Schema and CRUD Operations ###

def update_user(user_id, username=None, email=None, password=None, location=None):
    """Updates an existing user's details by their ID."""
    update_data = {k: v for k, v in {
        "username": username,
        "email": email,
        "password": password,  # Apply hashing if password is updated
        "location": location
    }.items() if v is not None}
    
    result = user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0

def delete_user(user_id):
    """Deletes a user from the database by their ID."""
    result = user_collection.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0

def get_user_by_email(email):
    """Fetches a user by email."""
    user = user_collection.find_one({"email": email})
    if user:
        user["_id"] = str(user["_id"])
    return user

def get_all_users():
    """Retrieves all users from the database."""
    users = list(user_collection.find({}))
    for user in users:
        user["_id"] = str(user["_id"])
    return users

def validate_email(email):
    """Validate the email format."""
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def register_user(name, email, password):
    """Registers a new user in the database after validating constraints."""
    
    # Check if all fields are filled
    if not name or not email or not password:
        return "All fields are required."
    
    # Validate email
    if not validate_email(email):
        return "Invalid email format."
    
    # Check if user already exists
    if user_collection.find_one({"email": email}):
        return "Email already registered."

    # Insert user if constraints are met
    user_data = {
        "name": name,
        "email": email,
        "password": password  # Consider hashing the password before storing it
    }
    result = user_collection.insert_one(user_data)
    return str(result.inserted_id)