import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from geopy.distance import geodesic
from services.heatmap import Heatmap


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
        self,
        origin,
        destination,
        waypoints,
        profile,
        optimize,
        heatmap,
        safety_scores
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
                                            [9.179079392366791, 48.77928985002192]
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
                priority = {"else_if": f"in_bad{i}", "multiply_by": f"{safety_scores[i]}"}
                data["custom_model"]["areas"]["features"].append(feature)
                data["custom_model"]["priority"].append(priority)

            response = requests.post(url, json=data, headers=headers, params=params)
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
            self.safety_scores
        )

        # print(initial_route)

        if "paths" in initial_route and initial_route["paths"]:
            waypoints = self.find_nearby_safe_places(initial_route, 0.05, 0.1)

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
                    self.safety_scores
                )
            else:
                final_route = initial_route

            return final_route

# TODO: do you really need a function for this?
    def is_within_distance(self, coord1, coord2, max_distance_km=0.5):
        """
        Checks if two coordinates are within a certain distance of each other.

        PARAMETERS
        ----------
        coord1 : tuple
            The first coordinate (e.g., (48.783391, 9.180221))
        coord2 : tuple
            The second coordinate (e.g., (48.779477, 9.179306))
        max_distance_km : float
            The maximum distance in kilometers (default: 0.5)

        RETURNS
        -------
        bool
            True if the coordinates are within the maximum distance, False otherwise
        """
        
        return geodesic(coord1, coord2).km <= max_distance_km

    def find_nearby_safe_places(
        self, route, max_distance_for_no_detour=0.1, max_distance_for_detour=0.2
    ):
        """
        Finds nearby safe places along a route.

        PARAMETERS
        ----------
        route : dict
            The route data as a JSON dictionary
        max_distance_for_no_detour : float
            The maximum distance for no detour in kilometers (default: 0.1)
        max_distance_for_detour : float
            The maximum distance for detour in kilometers (default: 0.2)

        RETURNS
        -------
        list
            A list of nearby safe places as strings (e.g., ["48.783391,9.180221", ...])
        """

        route = route["paths"][0]
        total_distance = route["distance"]

        waypoints = []

        num_segments = len(route["points"]["coordinates"])
        last_coordinate = route["points"]["coordinates"][0]
        distance_since_last_checkpoint = 0
        distance_since_start = 0
        checkpoint_interval = 0.5
        i = 0

        while i < num_segments:
            current_coordinate = route["points"]["coordinates"][i]
            distance = geodesic(current_coordinate, last_coordinate).kilometers
            distance_since_last_checkpoint = distance_since_last_checkpoint + distance
            distance_since_start = distance_since_start + distance
            last_coordinate = current_coordinate

            more_than_250m_from_finish = (total_distance - distance_since_start) > 0.25
            new_checkpoint_interval_reached = (
                distance_since_last_checkpoint > checkpoint_interval
                and more_than_250m_from_finish
            )

            if new_checkpoint_interval_reached:
                for safe_place in self.safe_place_coords:
                    waypoint_already_close_enough = False
                    if self.is_within_distance(
                        current_coordinate, safe_place, max_distance_for_no_detour
                    ):
                        waypoint_already_close_enough = True
                        break

                if waypoint_already_close_enough:
                    distance_since_last_checkpoint = 0
                else:
                    for safe_place in self.safe_place_coords:
                        if self.is_within_distance(
                            current_coordinate, safe_place, max_distance_for_detour
                        ):
                            waypoints.append(f"{safe_place[0]},{safe_place[1]}")
                            distance_since_last_checkpoint = 0
                            break

            i = i + 1
        return list(set(waypoints))


# just for testing:
if __name__ == "__main__":
    crawler = WebCrawler("")
    result = crawler.get_route(
        "48.783391,9.180221",
        "48.779477,9.179306",
        "foot",
    )
    print(result)
