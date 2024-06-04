import numpy as np


# encoded_polyline = "a_whHu_`w@KK\\_APm@p@yB|AaGNu@Ia@GWAXUz@]`
# BQx@kAnEUv@gAtCaB`EUn@VX`@j@t@z@~AhBn@l@d@X\\N|APvEZbBXxAd@hBx@LMJUBQa@]{@c@a@M]KJc@Ry@v@mCbAmE"

class Mapper():
    '''
    A class for mapping route data.

    Attributes:
        None

    Methods:
        add_waypoints(decoded_polyline: list) -> list:
            Adds waypoints to a decoded polyline.
        add_map_values(decoded_polyline: list, waypoints: list) -> dict:
            Extracts map values from a decoded polyline and waypoints.
    '''
    
    def __init__(self) -> None:
        pass
    
    def add_waypoints(self, decoded_polyline: list) -> list:
        '''
        Adds waypoints to a decoded polyline.

        Args:
            decoded_polyline (list): A list of tuples representing the decoded polyline.

        Returns:
            list: A list of indices representing the waypoints.
        '''
        
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
        
        return waypoints
    
    def add_map_values(self, decoded_polyline: list, waypoints) -> dict:
        '''
        Extracts map values from a decoded polyline and waypoints.

        Args:
            decoded_polyline (list): A list of tuples representing the decoded polyline.
            waypoints (list): A list of indices representing the waypoints.

        Returns:
            dict: A dictionary containing the map values.
        '''
        
        # Extract latitude and longitude
        latitudes = [point[0] for point in decoded_polyline]
        longitudes = [point[1] for point in decoded_polyline]

        waypoint_latitudes = [decoded_polyline[i][0] for i in waypoints]
        waypoint_longitudes = [decoded_polyline[i][1] for i in waypoints]
        
        # Start and end coordinates
        start_lat, start_lon = decoded_polyline[0]
        end_lat, end_lon = decoded_polyline[-1]
        
        map_values = {
            "latitudes": latitudes,
            "longitudes": longitudes,
            "waypoint_latitudes": waypoint_latitudes,
            "waypoint_longitudes": waypoint_longitudes,
            "start_lat": start_lat,
            "start_lon": start_lon,
            "end_lat": end_lat,
            "end_lon": end_lon
        }
        
        return map_values
