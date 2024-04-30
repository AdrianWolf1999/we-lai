import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import numpy as np
import polyline
import requests
from math import radians, cos, sin, asin, sqrt

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv("API_KEY")

def get_route(origin, destination, api_key):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    return data

# Example usage
# origin = "48.783391,9.180221"
# destination = "48.779477,9.179306"


# route_data = get_route(origin, destination, api_key)
# print(route_data)


# Encoded polyline string
encoded_polyline = "a_whHu_`w@KK\\_APm@p@yB|AaGNu@Ia@GWAXUz@]`BQx@kAnEUv@gAtCaB`EUn@VX`@j@t@z@~AhBn@l@d@X\\N|APvEZbBXxAd@hBx@LMJUBQa@]{@c@a@M]KJc@Ry@v@mCbAmE"

# Decode the polyline
decoded_polyline = polyline.decode(encoded_polyline)

# Extract latitude and longitude
latitudes = [point[0] for point in decoded_polyline]
longitudes = [point[1] for point in decoded_polyline]

# Calculate distance between points
distances = [0]
total_distance = 0
for i in range(1, len(decoded_polyline)):
    lat1, lon1 = decoded_polyline[i - 1]
    lat2, lon2 = decoded_polyline[i]
    distance = np.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) * 111000
    total_distance += distance
    distances.append(total_distance)

# Add waypoints every 10 meters
waypoint_distance = 10
waypoints = []
for i, distance in enumerate(distances):
    if distance >= waypoint_distance:
        waypoint_distance += 10
        waypoints.append(i)

waypoint_latitudes = [decoded_polyline[i][0] for i in waypoints]
waypoint_longitudes = [decoded_polyline[i][1] for i in waypoints]

# Start and end coordinates
start_lat, start_lon = decoded_polyline[0]
end_lat, end_lon = decoded_polyline[-1]

# Plot the polyline with waypoints
plt.figure(figsize=(10, 6))
plt.plot(longitudes, latitudes, 'b-', linewidth=2)
plt.scatter(waypoint_longitudes, waypoint_latitudes, color='green', label='Waypoints (every 10m)')
plt.scatter([start_lon, end_lon], [start_lat, end_lat], color='red', label='Start/End')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Decoded Polyline with Waypoints (every 10 meters)')
plt.legend()
plt.grid(True)
plt.show()



