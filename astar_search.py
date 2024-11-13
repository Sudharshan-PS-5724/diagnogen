import openrouteservice
from db import get_coordinates

ORS_API_KEY = "5b3ce3597851110001cf624837b70452bcba4a858f61802bdcc59194"  # Obtain a free API key from OpenRouteService

def get_distance_and_duration(origin, destination):
    client = openrouteservice.Client(key=ORS_API_KEY)
    coordinates = [[origin[1], origin[0]], [destination[1], destination[0]]]
    route = client.directions(coordinates=coordinates, profile='driving-car', format='geojson')
    distance = route['features'][0]['properties']['segments'][0]['distance']
    duration = route['features'][0]['properties']['segments'][0]['duration']
    return distance, duration

def a_star_search(hospitals, start_location, goal_location):
    open_set = {start_location: 0}
    came_from = {}
    cost_from_start = {start_location: 0}

    goal_lat, goal_lng = get_coordinates(goal_location)

    def calculate_cost(current_location, hospital):
        hospital_location = (hospital["latitude"], hospital["longitude"])
        distance, duration = get_distance_and_duration(current_location, hospital_location)

        distance_weight = 0.5
        duration_weight = 0.3
        availability_weight = 0.2

        availability_cost = (1 / hospital["availability"]) if hospital["availability"] > 0 else float('inf')

        return (distance_weight * distance) + (duration_weight * duration) + (availability_weight * availability_cost)

    while open_set:
        current_location = min(open_set, key=lambda k: open_set[k])

        if current_location == (goal_lat, goal_lng):
            return reconstruct_path(came_from, current_location)

        open_set.pop(current_location)

        for hospital in hospitals:
            neighbor_location = (hospital["latitude"], hospital["longitude"])
            tentative_cost_from_start = cost_from_start.get(current_location, 0) + calculate_cost(current_location, hospital)

            if tentative_cost_from_start < cost_from_start.get(neighbor_location, float('inf')):
                came_from[neighbor_location] = current_location
                cost_from_start[neighbor_location] = tentative_cost_from_start

                estimated_cost_to_goal = calculate_cost(neighbor_location, {"latitude": goal_lat, "longitude": goal_lng, "availability": hospital["availability"]})
                open_set[neighbor_location] = tentative_cost_from_start + estimated_cost_to_goal

    return []

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path