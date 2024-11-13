import hashlib
from geopy.geocoders import Nominatim

# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Helper function to verify password
def verify_password(stored_password, input_password):
    return stored_password == hash_password(input_password)

# Helper function to get coordinates from location using Geopy
def get_coordinates(location):
    """Fetches latitude and longitude for the specified location using Nominatim API."""
    geolocator = Nominatim(user_agent="hospital_finder")
    location_obj = geolocator.geocode(location)
    if location_obj:
        return location_obj.latitude, location_obj.longitude
    else:
        return None
