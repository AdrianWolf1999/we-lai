import csv
import os


class Heatmap:
    """
    Heatmap class.

    Represents a heatmap of crime data.

    Attributes:
    ----------
    heatmap_coords : list
        List of bad polygon coordinates.
    safety_scores : list
        List of safety scores corresponding to the bad polygon coordinates.
    safe_place_coords : list
        List of safe place coordinates.

    Methods:
    ----------
    __init__(data_dir) : None
        Initializes the Heatmap instance with the specified data directory.
    add_and_save_new_polygon(polygon, safety_score) : None
        Adds a new polygon to the heatmap with the specified safety score and saves the data to CSV.
    add_and_save_new_safe_place(coordinates) : None
        Adds a new safe place to the heatmap with the specified coordinates and saves the data to CSV.
    save_data_to_csv() : None
        Saves the heatmap data to CSV files.
    load_data_from_csv() : None
        Loads the heatmap data from CSV files.
    flip_coordinates(coordinates) : list
        Flips the coordinates (i.e., swaps latitude and longitude) for the specified coordinates.
    get_heatmap_and_safe_places() : dict
        Returns a dictionary containing the bad polygon coordinates, medium polygon coordinates, and safe place coordinates.

    Notes:
    -----
    This class is responsible for managing the heatmap data, including loading and saving to CSV files.
    """

    def __init__(self, data_dir):
        """
        Initializes the Heatmap instance with the specified data directory.

        Parameters:
        ----------
        data_dir : str
            The directory where the CSV files are stored.
        """
        self.data_dir = data_dir
        self.heatmap_coords_path = os.path.join(data_dir, "heatmap_coords.csv")
        self.safety_scores_path = os.path.join(data_dir, "safety_scores.csv")
        self.safe_place_coords_path = os.path.join(data_dir, "safe_place_coords.csv")
        self.preferred_coords_path = os.path.join(data_dir, "preferred_coords.csv")
        self.heatmap_coords = []
        self.safety_scores = []
        self.safe_place_coords = []
        self.preferred_coords = []
        self.load_data_from_csv()

    def add_and_save_new_polygon(self, polygon, safety_score):
        """
        Adds a new polygon to the heatmap with the specified safety score and saves the data to CSV.

        Parameters:
        ----------
        polygon : list
            The list of coordinates defining the polygon.
        safety_score : float
            The safety score associated with the polygon.
        """
        if isinstance(safety_score, str):
            safety_score = float(safety_score)
            
        if safety_score > 1: # Higher priority areas
            polygon.append(
                polygon[0]
            )  # Add first element to polygons end because routing call  expects closed loops
            self.preferred_coords.append(polygon)
        else: # Lower priority areas
            polygon.append(
                polygon[0]
            )  # Add first element to polygons end because routing call  expects closed loops
            self.heatmap_coords.append(polygon)
            self.safety_scores.append(safety_score)
        self.save_data_to_csv()

    def add_and_save_new_safe_place(self, coordinates):
        """
        Adds a new safe place to the heatmap with the specified coordinates and saves the data to CSV.

        Parameters:
        ----------
        coordinates : list
            The list of coordinates defining the safe place.
        """
        self.safe_place_coords.append(coordinates)
        self.save_data_to_csv()

    def save_data_to_csv(self):
        """
        Saves the heatmap data to CSV files.
        """
        # Save heatmap_coords
        with open(
            self.heatmap_coords_path, mode="w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            for polygon in self.heatmap_coords:
                for coord in polygon:
                    writer.writerow(coord)
                writer.writerow([])  # Empty row to separate polygons

        # Save safety_scores
        with open(
            self.safety_scores_path, mode="w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            for score in self.safety_scores:
                writer.writerow([score])

        # Save safe_place_coords
        with open(
            self.safe_place_coords_path, mode="w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            for coord in self.safe_place_coords:
                writer.writerow(coord)
        
        # Save preferred_coords
        with open(
            self.preferred_coords_path, mode="w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            for polygon in self.preferred_coords:
                for coord in polygon:
                    writer.writerow(coord)
                writer.writerow([])  # Empty row to separate polygons

    def load_data_from_csv(self):
        """
        Loads the heatmap data from CSV files.
        """
        self.heatmap_coords = []
        self.safe_place_coords = []
        self.safety_scores = []
        self.preferred_coords = []
        # Load heatmap_coords
        with open(self.heatmap_coords_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            polygon = []
            for row in reader:
                if row:
                    polygon.append([float(row[0]), float(row[1])])
                else:
                    self.heatmap_coords.append(polygon)
                    polygon = []

        # Load safety_scores
        with open(self.safety_scores_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                self.safety_scores.append(float(row[0]))

        # Load safe_place_coords
        with open(self.safe_place_coords_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                self.safe_place_coords.append([float(row[0]), float(row[1])])

        # Load heatmap_coords
        with open(self.preferred_coords_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            polygon = []
            for row in reader:
                if row:
                    polygon.append([float(row[0]), float(row[1])])
                else:
                    self.preferred_coords.append(polygon)
                    polygon = []


    def flip_coordinates(self, coordinates):
        """
        Flips the coordinates (i.e., swaps latitude and longitude) for the specified coordinates.

        Parameters:
        ----------
        coordinates : list
            The list of coordinates to flip.

        Returns:
        ----------
        list
            The flipped coordinates.
        """
        flipped_coords = []
        for coord_set in coordinates:
            if not coord_set:
                continue
            if isinstance(coord_set[0], list):  # Check if it's a nested list
                flipped_set = [[b, a] for a, b in coord_set]
                flipped_coords.append(flipped_set)
            else:
                flipped_coords = [[b, a] for a, b in coordinates]
                break
        return flipped_coords

    def get_heatmap_and_safe_places(self):
        """
        Returns a dictionary containing the bad polygon coordinates, medium polygon coordinates, and safe place coordinates.

        Returns:
        ----------
        dict
            A dictionary with the heatmap and safe place data.
        """
        data = {
            "heatmap": {
                "coordinates": self.flip_coordinates(self.heatmap_coords),
                "safetyScores": self.safety_scores,
            },
            "safePlaces": {
                "coordinates": self.flip_coordinates(self.safe_place_coords)
            },
            "preferred": {
                "coordinates": self.flip_coordinates(self.preferred_coords)
            }
        }
        return data
