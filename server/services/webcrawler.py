import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from geopy.distance import geodesic
from services.heatmap import Heatmap
from shapely.geometry import LineString, Point, Polygon


class WebCrawler(Heatmap):
    """
    WebCrawler class.

    Provides a method to crawl from Google API and return the requested route as json.

    Attributes:
    ----------
    api_key : str
        The loaded API key.

    heatmap_coords : list
        A list of polygons for the heatmap

    safety_scores : list
        A list with a single value between 0 and 1 for the safety of each polygon
    
    preferred_coords : list
        A list with polygons of prefferred roads

    safe_place_coords : list
        A list of coordinates for safe places

    Methods:
    ----------
    load_api_key() : str or None
        Loads the API key from a.env file in the current directory.

    api_routing_call(origin, destination, waypoints, profile, optimize, heatmap, safety_scores, preferred_coords) : dict
        Makes a routing API call to GraphHopper with the specified origin, destination, waypoints, profile, and optimization settings.

    get_route(origin, destination, profile) : dict
        Crawls the route through GraphHopper's API and returns the route data as json.

    is_within_distance(coord1, coord2, max_distance_km=0.5) : bool
        Checks if two coordinates are within a certain distance of each other.

    find_nearby_safe_places(route, max_distance_for_no_detour=0.1, max_distance_for_detour=0.2) : list
        Finds nearby safe places along a route.

    get_suggestions(query) : dict
        Returns a list of suggestions based on the specified query.

    Notes:
    -----
    This class is responsible for crawling route data from GraphHopper's API and finding nearby safe places.
    """

    def __init__(self, data_dir):
        self.api_key = self.load_api_key()
        super().__init__(data_dir)

    def load_api_key(self):
        """
        Loads the API key from 'api_key.env' file in the current directory.

        RETURNS
        ----------
        api_key : str or None
            The API key value if found, otherwise `None`.
        """

        # Try to load environment variables from .env file in the current directory
        env_file_cwd = Path.cwd() / ".env"
        if env_file_cwd.exists():
            # Load environment variables from .env file
            load_dotenv(env_file_cwd)

        # Load the HERE API key from a file or environment variable
        api_key = os.getenv("GEO_API_KEY")
        if api_key is None:
            print(
                "Error: No HERE API key found. Please create a .env file like stated in README"
            )
            return None
        return api_key

    def api_routing_call(
        self, origin, destination, waypoints, profile, optimize, heatmap, safety_scores, preferred_coords
    ):
        """
        Makes a routing API call to GraphHopper.

        PARAMETERS
        ----------
        origin : str
            The starting location of the route (e.g., "48.783391,9.180221")
        destination : str
            The ending location of the route (e.g., "48.779477,9.179306")
        waypoints : list
            A list of waypoints to include in the route
        profile : str
            The routing profile to use (e.g., "foot")
        optimize : str
            Whether to optimize the route (e.g., "false")
        heatmap : list
            A list of polygon coordinates to avoid
        safety_scores :
            A safety score for every polygon in the heatmap

        RETURNS
        -------
        data : dict
            The route data as a JSON dictionary, or an empty dictionary if an exception occurs
        """
        try:
            url = "https://graphhopper.com/api/1/route"
            headers = {"Content-Type": "application/json"}
            params = {"key": self.api_key}
            data = {
                "profile": profile,
                "points": [
                    origin.split(","),  # Source coordinates
                    *[wp.split(",") for wp in waypoints],  # waypoints
                    destination.split(","),  # Target coordinates
                ],
                "ch.disable": True,
                "points_encoded": False,
                "optimize": optimize,
                "custom_model": {
                    "priority": [
                        {"if": "in_init", "multiply_by": "1"},
                    ],
                    "areas": {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "id": "init",
                                "properties": {},
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [
                                        [
                                            [9.179079392366791, 48.77928985002192],
                                            [9.178403533981024, 48.77848548812847],
                                            [9.180537608035477, 48.77835052681645],
                                            [9.179079392366791, 48.77928985002192],
                                        ]
                                    ],
                                },
                            },
                        ],
                    },
                },
            }

            # Add polygons with lower priority to api call
            for i, polygon in enumerate(heatmap):
                feature = {
                    "type": "Feature",
                    "id": f"bad{i}",
                    "properties": {},
                    "geometry": {"type": "Polygon", "coordinates": [polygon]},
                }
                priority = {
                    "else_if": f"in_bad{i}",
                    "multiply_by": f"{safety_scores[i]}",
                }
                data["custom_model"]["areas"]["features"].append(feature)
                data["custom_model"]["priority"].append(priority)
            
            # Add polygons with higher priority (but no loop this time as this is an inverse operation (it sets the priority of everythin else lower))
            feature = {
                "type": "Feature",
                "id": "good",
                "properties": {},
                "geometry": {"type": "Polygon", "coordinates": preferred_coords},
            }
            priority = {
                "if": "!in_good",
                "multiply_by": "0.5",
            }
            data["custom_model"]["areas"]["features"].append(feature)
            data["custom_model"]["priority"].append(priority)

            # Post request
            response = requests.post(
                url, json=data, headers=headers, params=params, timeout=10
            )
            response.raise_for_status()
            ret = response.json()

        except requests.exceptions.RequestException as e:
            print(f"An Exception occured: {e}")
            ret = {}

        return ret

    def get_suggestions(self, query):
        """
        Returns a list of suggestions based on the specified query.

        Parameters:
        ----------
        query : str
            The search query for which suggestions are to be returned.

        Returns:
        ----------
        dict
            A dictionary containing a list of suggestions.

        Notes:
        -----
        This method uses GraphHopper's API to fetch suggestions based on the query.
        """
        try:
            url = "https://graphhopper.com/api/1/geocode"
            params = {"q": query, "key": self.api_key}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            ret = response.json()
        except requests.exceptions.RequestException as e:
            print(f"An Exception occured: {e}")
            ret = {}

        return ret

    def get_route(self, origin, destination, profile):
        """
        Crawls the Route through GraphHopper's API and returns the route data as json.

        Parameters:
        ----------
        origin : str
            The starting location of the route (e.g., "48.783391,9.180221")
        destination : str
            The ending location of the route (e.g., "48.779477,9.179306")
        profile : str
            The routing profile to use (e.g., "foot")

        Returns:
        ----------
        data : dict
            The route data as a JSON dictionary, or an error message if an exception occurs

        Notes:
        -----
        This method first makes an initial API call to get the route, then finds nearby safe places and adds them as waypoints to the route.
        """

        initial_route = self.api_routing_call(
            origin,
            destination,
            [],
            profile,
            "false",
            self.heatmap_coords,
            self.safety_scores,
            self.preferred_coords,
        )

        if "paths" in initial_route and initial_route["paths"]:
            waypoints = self.find_nearby_safe_places(
                origin, destination, profile, initial_route
            )

            print("Waypoint added to route:", waypoints)
            final_route = {}

            if waypoints:
                final_route = self.api_routing_call(
                    origin,
                    destination,
                    waypoints,
                    profile,
                    "false",
                    self.heatmap_coords,
                    self.safety_scores,
                    self.preferred_coords,
                )
            else:
                final_route = initial_route

            return final_route

    def find_nearby_safe_places(
        self,
        origin,
        destination,
        profile,
        route,
        additional_percent=0.2,
        buffer_distance_km=0.5,
        ignore_range_km=0.2,
    ):
        """
        Find nearby safe places along a route.

        Parameters:
        ----------
        origin : str
            Starting point coordinates as a string (e.g., "48.783391,9.180221")
        destination : str
            Destination coordinates as a string (e.g., "48.783391,9.180221")
        profile : str
            Routing profile (e.g., "car", "bike", "foot")
        route : dict
            Route data as a JSON object
        additional_percent : float, optional
            Allowed percentage increase in distance for detour (default: 0.2)
        buffer_distance_km : float, optional
            Distance in kilometers to buffer around the route for preselecting safe places (default: 0.5)
        ignore_range_km : float, optional
            Distance in kilometers to ignore around the start and end points (default: 0.2)

        Returns:
        ----------
        list
            Nearby safe places as coordinate strings (e.g., ["48.783391,9.180221"])
        """
        # Extract route data
        route_data = route["paths"][0]

        # Create a LineString from route coordinates
        coordinates = route_data["points"]["coordinates"]
        route_line = LineString(coordinates)

        # Define a buffer distance in degrees (approximate conversion from km)
        buffer_distance_degrees = buffer_distance_km / 111.32  # 1 degree ≈ 111.32 km

        # Create a buffer around the route
        route_buffer = route_line.buffer(buffer_distance_degrees)

        # Initialize variables
        total_distance = route_data["distance"]
        safeplace_distances = []
        waypoints = []

        # Filter safe places within the buffer
        for safeplace in self.safe_place_coords:
            safeplace_point = Point(safeplace)
            if route_buffer.contains(safeplace_point):

                # Check if the safe place is within the ignore range of start or end points
                start_coords = tuple(map(float, origin.split(",")[::-1]))
                end_coords = tuple(map(float, destination.split(",")[::-1]))
                safeplace_coords = tuple(safeplace)[::-1]

                if (
                    geodesic(start_coords, safeplace_coords).km < ignore_range_km
                    or geodesic(end_coords, safeplace_coords).km < ignore_range_km
                ):
                    continue  # skip this safe place if it's within the ignore range

                safeplace_str = ",".join(map(str, safeplace))
                route_with_safeplace = self.api_routing_call(
                    origin,
                    destination,
                    [safeplace_str],
                    profile,
                    "false",
                    self.heatmap_coords,
                    self.safety_scores,
                    self.preferred_coords,
                )
                if (
                    route_with_safeplace["paths"][0]["distance"]
                    <= (1 + additional_percent) * total_distance
                ):
                    # Calculate the heuristic value for this safe place
                    heuristic_value = self.calculate_heuristic(route_with_safeplace)
                    safeplace_distances.append([heuristic_value, safeplace])

        if not safeplace_distances:
            return []  # or some other default value indicating no safe places found

        nearest_safeplace = min(safeplace_distances, key=lambda x: x[0])
        nearest_safeplace = ",".join(map(str, nearest_safeplace[1]))
        waypoints.append(nearest_safeplace)
        return waypoints

    def calculate_heuristic(self, route):
        """
        Calculate a heuristic value for a route based on its length and safety score.

        Args:
        - route_data (dict): Route data as a JSON object

        Returns:
        - float: Heuristic value
        """

        route_data = route["paths"][0]

        # Calculate the total distance of the route
        total_distance = route_data["distance"]

        # Initialize the badness score
        badness_score = 0

        # Iterate over the route segments
        for i in range(len(route_data["points"]["coordinates"]) - 1):
            segment_start = route_data["points"]["coordinates"][i]
            segment_end = route_data["points"]["coordinates"][i + 1]

            # Check if the segment passes through any polygon areas with low safety scores
            for polygon, safety_score in zip(self.heatmap_coords, self.safety_scores):
                if self.is_segment_in_polygon(segment_start, segment_end, polygon):
                    badness_score += (1 - safety_score) * self.segment_length(
                        segment_start, segment_end
                    )

        # Calculate the heuristic value as a weighted sum of the total distance and badness score
        heuristic_value = total_distance + badness_score
        # maybe add a weight value =! 1 for badness_score

        return heuristic_value

    def is_segment_in_polygon(self, segment_start, segment_end, polygon):
        """
        Check if a segment is inside a polygon.

        Args:
        - segment_start (list of long and lat): Start point of the segment
        - segment_end (list of long and lat): End point of the segment
        - polygon (list): Polygon coordinates

        Returns:
        - bool: True if the segment is inside the polygon, False otherwise
        """

        # Create a LineString object from the segment
        line = LineString([segment_start, segment_end])

        # Create a Polygon object from the polygon coordinates
        poly = Polygon(polygon)

        # Check if the LineString intersects with the Polygon
        return poly.intersects(line)

    def segment_length(self, segment_start, segment_end):
        """
        Calculate the length of a segment.

        Args:
        - segment_start (tuple): Start point of the segment
        - segment_end (tuple): End point of the segment

        Returns:
        - float: Length of the segment
        """
        # Calculate the distance between the two points using the geodesic distance
        return geodesic(segment_start, segment_end).km
