import requests

def get_current_location():
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()

        if data['status'] == 'success':
            latitude = data['lat']
            longitude = data['lon']
            return latitude, longitude
        else:
            print("Could not get location. Reason:", data['message'])
            return None
    except Exception as e:
        print("Error:", e)
        return None

# Example usage:
start_location = get_current_location()
print("Your current location:", start_location)
