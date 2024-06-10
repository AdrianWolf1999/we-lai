import csv
import os

class Heatmap:
    """
    Represents a heatmap of crime data.

	Attributes:
    ----------
    heatmap_coords : list
        List of bad polygon coordinates.
    safe_place_coords : list
        List of safe place coordinates.
    
    Methods:
    -------
    __init__() : None
        Initializes the Heatmap instance.
    get_heatmap_and_safe_places() : dict
        Returns a dictionary containing the bad polygon coordinates, medium polygon coordinates, and safe place coordinates.
    """

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.heatmap_coords_path = os.path.join(data_dir, 'heatmap_coords.csv')
        self.safety_scores_path = os.path.join(data_dir, 'safety_scores.csv')
        self.safe_place_coords_path = os.path.join(data_dir, 'safe_place_coords.csv')
        self.heatmap_coords = []
        self.safety_scores = []
        self.safe_place_coords = []
        self.load_data_from_csv()

    def add_and_save_new_polygon(self, polygon, safety_score):
        self.heatmap_coords.append(polygon)
        self.safety_scores.append(safety_score)
        self.save_data_to_csv()
    
    def add_and_save_new_safe_place(self, coordinates):
        self.safe_place_coords.append(coordinates)
        self.save_data_to_csv()

    def save_data_to_csv(self):
        # Save heatmap_coords
        with open(self.heatmap_coords_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            for polygon in self.heatmap_coords:
                for coord in polygon:
                    writer.writerow(coord)
                writer.writerow([])  # Empty row to separate polygons

        # Save safety_scores
        with open(self.safety_scores_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            for score in self.safety_scores:
                writer.writerow([score])

        # Save safe_place_coords
        with open(self.safe_place_coords_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            for coord in self.safe_place_coords:
                writer.writerow(coord)

    def load_data_from_csv(self):
        # Load heatmap_coords
        with open(self.heatmap_coords_path, mode='r') as file:
            reader = csv.reader(file)
            polygon = []
            for row in reader:
                if row:
                    polygon.append([float(row[0]), float(row[1])])
                else:
                    self.heatmap_coords.append(polygon)
                    polygon = []

        # Load safety_scores
        with open(self.safety_scores_path, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                self.safety_scores.append(float(row[0]))

        # Load safe_place_coords
        with open(self.safe_place_coords_path, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                self.safe_place_coords.append([float(row[0]), float(row[1])])

    def flip_coordinates(self, coordinates):
        flipped_coords = []
        for coord_set in coordinates:
            if isinstance(coord_set[0], list):  # Check if it's a nested list
                flipped_set = [[b, a] for a, b in coord_set]
                flipped_coords.append(flipped_set)
            else:
                flipped_coords = [[b, a] for a, b in coordinates]
                break
        return flipped_coords

    def get_heatmap_and_safe_places(self):
        data = {
            "heatmap": {
                "coordinates": self.flip_coordinates(self.heatmap_coords),
                "safetyScores": self.safety_scores,
            },
            "safePlaces": {
                "coordinates": self.flip_coordinates(self.safe_place_coords)
            }
        }
        return data
