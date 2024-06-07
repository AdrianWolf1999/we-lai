import pandas as pd
from shapely.geometry import Polygon
import folium


class Heatmap:
    def __init__(self):
        self.polygons = pd.read_pickle("server/heuristic/data/heatmap_polygons.pkl")
        self.checkpoints = pd.read_pickle("server/heuristic/data/heatmap_checkpoints.pkl")

    def create_map(self):
        
        m = folium.Map(location=[48.783391, 9.180221], zoom_start=12)

        # Add polygons to the map
        for index, row in self.polygons.iterrows():
            
            try:
                polygon = Polygon(row["polygon_coords"])
                folium.Polygon(polygon.exterior.coords, color='red', opacity=0.5).add_to(m)
            except Exception as e:
                print(f"Error adding polygon: {e}")

        # Add checkpoints to the map
        for index, row in self.checkpoints.iterrows():
            folium.Marker(location=row["checkpoint_coords"], icon=folium.Icon(color='green')).add_to(m)

        # Display the map
        m.save("server/heuristic/data/heatmap_map.html")
        
    def load_map(self):
        pass

if __name__ == "__main__":
    dataset = Heatmap()
    dataset.create_map()
    