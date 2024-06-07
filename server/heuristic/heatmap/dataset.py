import pandas as pd

class Dataset():

    def __init__(self) -> None:
        
        try:
            self.polygons = pd.read_pickle("server/heuristic/data/heatmap_polygons.pkl")
        except FileNotFoundError:
            self.polygons = pd.DataFrame(columns=['polygon_id', 'polygon_coords', 'badness_score'])
            self.polygons.to_pickle("server/heuristic/data/heatmap_polygons.pkl")
        
        try:
            self.checkpoints = pd.read_pickle("server/heuristic/data/heatmap_checkpoints.pkl")
        except FileNotFoundError:
            self.checkpoints = pd.DataFrame(columns=['checkpoint_id', 'checkpoint_coords'])
            self.checkpoints.to_pickle("server/heuristic/data/heatmap_checkpoints.pkl")
            
    def create_polygons(self):
        
        self.polygons = pd.DataFrame({
            "polygon_id": [0, 1, 2],
            "polygon_coords": [
                [(48.783391, 9.180221), (48.779477, 9.179306), (48.785123, 9.181234), (48.791111, 9.183456)],
                [(48.795555, 9.185678), (48.801234, 9.187890), (48.806789, 9.190123), (48.812345, 9.192456)],
                [(48.780898, 9.175520), (48.780319, 9.173664), (48.781716, 9.172209), (48.781881, 9.172511), (48.782292, 9.172168), (48.782469, 9.173005), (48.782142, 9.173448), (48.782359, 9.174192), (48.781981, 9.174477)],
            ],
            "badness_score": [0.8, 0.5, 0.9]
        })

        self.polygons.to_pickle("server/heuristic/data/heatmap_polygons.pkl")
        
    def create_checkpoints(self):
        
        self.checkpoints = pd.DataFrame({
            "checkpoint_id": [0, 1, 2],
            "checkpoint_coords": [
                (48.783391, 9.180221),
                (48.795555, 9.185678),
                (48.818901, 9.194678)
            ]
        })
        
        self.checkpoints.to_pickle("server/heuristic/data/heatmap_checkpoints.pkl")
        
    def add_polygon(self, polygon_coords, badness_score, polygon_id=0):
        
        if not self.polygons.empty:
            polygon_id = self.polygons['polygon_id'].max() + 1
            
        new_polygon = pd.DataFrame({
            "polygon_id": [polygon_id],
            "polygon_coords": [polygon_coords],
            "badness_score": [badness_score]
        })
        self.polygons = pd.concat([self.polygons, new_polygon], ignore_index=True)
        self.polygons.to_pickle("server/heuristic/data/heatmap_polygons.pkl")

    def add_checkpoint(self, checkpoint_coords, checkpoint_id=0):
        if not self.checkpoints.empty:
            checkpoint_id = self.checkpoints['checkpoint_id'].max() + 1
        
        new_checkpoint = pd.DataFrame({
            "checkpoint_id": [checkpoint_id],
            "checkpoint_coords": [checkpoint_coords]
        })
        self.checkpoints = pd.concat([self.checkpoints, new_checkpoint], ignore_index=True)
        self.checkpoints.to_pickle("server/heuristic/data/heatmap_checkpoints.pkl")
        
if __name__ == "__main__":
    heatmap = Dataset()
    
    # Only used one time:
    # heatmap.create_checkpoints()
    # heatmap.create_polygons()