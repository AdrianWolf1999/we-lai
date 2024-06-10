import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from geopy.distance import geodesic
from services.heatmap import Heatmap
from shapely.geometry import LineString, Point


class WebCrawler(Heatmap):
    """
    Provides a method to crawl from Google API and return the requested route as json.

    Attributes:
    ----------
    api_key : str
        The loaded API key.
    heatmap_coords : list
        A list of polygons for the heatmap
    safety_scores : list
        A list with a single value between 0 and 1 for the safety of each polygon
    safe_place_coords : list
        A list of coordinates for safe places

    Methods:
    -------
    load_api_key() : str or None
        Loads the API key from a .env file in the current directory.
    api_routing_call(origin, destination, waypoints, profile, optimize, badPolygonCoords, mediumPolygonCoords) : dict
        Makes a routing API call to GraphHopper with the specified origin, destination, waypoints, profile, and optimization settings.
    get_route(origin, destination, profile) : dict
        Crawls the route through GraphHopper's API and returns the route data as json.
    is_within_distance(coord1, coord2, max_distance_km=0.5) : bool
        Checks if two coordinates are within a certain distance of each other.
    find_nearby_safe_places(route, max_distance_for_no_detour=0.1, max_distance_for_detour=0.2) : list
        Finds nearby safe places along a route.
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
        self, origin, destination, waypoints, profile, optimize, heatmap, safety_scores
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

            response = requests.post(
                url, json=data, headers=headers, params=params, timeout=10
            )
            response.raise_for_status()
            ret = response.json()

        except requests.exceptions.RequestException as e:
            print(f"An Exception occured: {e}")
            ret = {}

        return ret

    def get_route(self, origin, destination, profile):
        """
        Crawls the Route through GraphHopper's API and returns the route data as json.

        PARAMETERS
        ----------
        origin : str
            The starting location of the route (e.g., "48.783391,9.180221")
        destination : str
            The ending location of the route (e.g., "48.779477,9.179306")
        profile : str
            The routing profile to use (e.g., "foot")

        RETURNS
        -------
        data : dict
            The route data as a JSON dictionary, or an error message if an exception occurs
        """

        initial_route = self.api_routing_call(
            origin,
            destination,
            [],
            profile,
            "false",
            self.heatmap_coords,
            self.safety_scores,
        )

        # print(initial_route)

        if "paths" in initial_route and initial_route["paths"]:
            waypoints = self.find_nearby_safe_places(
                origin, destination, profile, initial_route
            )

            print("Waypoints:")
            print(waypoints)
            print("###########")

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
    ):
        """
        Find nearby safe places along a route.

        Args:
        - origin (str): Starting point coordinates as a string (e.g., "48.783391,9.180221").
        - destination (str): Destination coordinates as a string (e.g., "48.783391,9.180221").
        - profile (str): Routing profile (e.g., "car", "bike", "foot").
        - route (dict): Route data as a JSON object.
        - additional_percent (float, optional): Allowed percentage increase in distance for detour (default: 0.2).
        - buffer_distance_km (float, optional): Distance in kilometers to buffer around the route for preselecting safe places (default: 0.5).

        Returns:
        - list: Nearby safe places as coordinate strings (e.g., ["48.783391,9.180221"]).
        """
        # Extract route data
        route_data = route["paths"][0]
        with open("test.json", "w") as file:
            json.dump(route, file)

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
                safeplace_str = ",".join(map(str, safeplace))
                route_with_safeplace = self.api_routing_call(
                    origin,
                    destination,
                    [safeplace_str],
                    profile,
                    "false",
                    self.heatmap_coords,
                    self.safety_scores,
                )
                if (
                    route_with_safeplace["paths"][0]["distance"]
                    <= (1 + additional_percent) * total_distance
                ):
                    safeplace_distances.append(
                        [route_with_safeplace["paths"][0]["distance"], safeplace]
                    )

        if not safeplace_distances:
            return []  # or some other default value indicating no safe places found
        print(safeplace_distances)
        nearest_safeplace = min(safeplace_distances, key=lambda x: x[0])
        nearest_safeplace = ",".join(map(str, nearest_safeplace[1]))
        waypoints.append(nearest_safeplace)
        return waypoints

    # TODO: Unused yet
    def calculate_heuristic(
        self, last_coordinate, current_coordinate, prev_segment, current_segment
    ):
        """
        Calculate the additional distance to go over a checkpoint.

        Args:
        - last_coordinate (tuple): Last coordinate
        - current_coordinate (tuple): Current coordinate
        - prev_segment (dict): Previous route segment
        - current_segment (dict): Current route segment

        Returns:
        - float: Additional distance to go over checkpoint in kilometers
        """
        # Calculate the distance from the last coordinate to the current coordinate
        direct_distance = geodesic(last_coordinate, current_coordinate).km

        # Calculate the distance from the last coordinate to the previous segment's end
        # and then from the previous segment's end to the current coordinate
        detour_distance = geodesic(
            last_coordinate, (prev_segment[1], prev_segment[0])
        ).km
        detour_distance += geodesic(
            (prev_segment[1], prev_segment[0]), current_coordinate
        ).km

        # Return the additional distance to go over the checkpoint
        return detour_distance - direct_distance

    # TODO: Unused yet
    def calculate_heuristic3(self, safe_place, route_data):
        """
        Calculate the heuristic value for a safe place.

        Args:
        - safe_place (tuple): Safe place coordinates
        - route (dict): Route data as a JSON object

        Returns:
        - float: Heuristic value
        """
        # Calculate the heuristic value based on the distance from the safe place to the route
        # and other factors (e.g., safety score, distance to destination)
        # For simplicity, let's use a simple distance-based heuristic
        min_distance_to_route = float("inf")
        for i in range(len(route_data["points"]["coordinates"]) - 1):
            segment_start = route_data["points"]["coordinates"][i]
            segment_end = route_data["points"]["coordinates"][i + 1]
            distance_to_segment = self.distance_to_segment(
                safe_place, segment_start, segment_end
            )
            if distance_to_segment < min_distance_to_route:
                min_distance_to_route = distance_to_segment
        return min_distance_to_route


# just for testing:
if __name__ == "__main__":
    crawler = WebCrawler("")
    result = crawler.get_route(
        "48.783391,9.180221",
        "48.779477,9.179306",
        "foot",
    )
    print(result)
