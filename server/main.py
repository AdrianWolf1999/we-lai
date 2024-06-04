# TODO: migrate the bottom half into extractor.py and visualiser.py

from math import asin, cos, radians, sin, sqrt

import matplotlib.pyplot as plt
import numpy as np
from services.extractor import Extractor
from services.webcrawler import WebCrawler

# Example usage
ORIGIN = "48.783391,9.180221"
DESTINATION = "48.779477,9.179306"

if __name__ == "__main__":
    # Get the route in json format from Google API
    crawler = WebCrawler()
    extractor = Extractor()

    route_data = crawler.get_route(ORIGIN, DESTINATION, crawler.load_api_key())

    decoded_polyline = extractor.extract_map(route_data)
    print("Decoded polyline:\n", decoded_polyline)

####################################################################
# TODO: Migrate from here downwards:

# encoded_polyline = "a_whHu_`w@KK\\_APm@p@yB|AaGNu@Ia@GWAXUz@]`
# BQx@kAnEUv@gAtCaB`EUn@VX`@j@t@z@~AhBn@l@d@X\\N|APvEZbBXxAd@hBx@LMJUBQa@]{@c@a@M]KJc@Ry@v@mCbAmE"

# Extract latitude and longitude
latitudes = [point[0] for point in decoded_polyline]
longitudes = [point[1] for point in decoded_polyline]

# Calculate distance between points
distances = [0]
TOTAL_DISTANCE = 0
for i in range(1, len(decoded_polyline)):
    lat1, lon1 = decoded_polyline[i - 1]
    lat2, lon2 = decoded_polyline[i]
    distance = np.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) * 111000
    TOTAL_DISTANCE += distance
    distances.append(TOTAL_DISTANCE)

# Add waypoints every 10 meters
WAYPOINT_DISTANCE = 10
waypoints = []
for i, distance in enumerate(distances):
    if distance >= WAYPOINT_DISTANCE:
        WAYPOINT_DISTANCE += 10
        waypoints.append(i)

waypoint_latitudes = [decoded_polyline[i][0] for i in waypoints]
waypoint_longitudes = [decoded_polyline[i][1] for i in waypoints]

# Start and end coordinates
start_lat, start_lon = decoded_polyline[0]
end_lat, end_lon = decoded_polyline[-1]

# Plot the polyline with waypoints
plt.figure(figsize=(10, 6))
plt.plot(longitudes, latitudes, "b-", linewidth=2)
plt.scatter(
    waypoint_longitudes,
    waypoint_latitudes,
    color="green",
    label="Waypoints (every 10m)",
)
plt.scatter([start_lon, end_lon], [start_lat, end_lat], color="red", label="Start/End")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Decoded Polyline with Waypoints (every 10 meters)")
plt.legend()
plt.grid(True)
plt.show()
