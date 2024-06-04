# TODO

import matplotlib.pyplot as plt


class Visualiser():
    '''
    A class for visualising route data.

    Attributes:
        None

    Methods:
        plot_map(map_values: dict) -> None:
            Plots a map with the route and waypoints.
    '''
    
    def __init__(self):
        pass
    
    def plot_map(self, map_values: dict):
        '''
        Plots a map with the route and waypoints.

        Args:
            map_values (dict): A dictionary containing the map values.
        '''
        
        # Plot the polyline with waypoints
        plt.figure(figsize=(10, 6))
        plt.plot(map_values["longitudes"], map_values["latitudes"], "b-", linewidth=2)
        plt.scatter(
            map_values["waypoint_longitudes"],
            map_values["waypoint_latitudes"],
            color="green",
            label="Waypoints (every 10m)",
        )
        plt.scatter([map_values["start_lon"], map_values["end_lon"]], [map_values["start_lat"], map_values["end_lat"]], color="red", label="Start/End")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title("Decoded Polyline with Waypoints (every 10 meters)")
        plt.legend()
        plt.grid(True)
        plt.show()
