import polyline
import flexpolyline as fp

class Extractor():
    '''
    Provides a method to extract a polyline from given route in json
    '''

    def __init__(self):
        pass

    def extract_map(self, route_data):
        '''
        Extracts usable map data from route in json format.

        PARAMETERS
        ----------
        route_data : str
            The route data as a JSON dictionary

        RETURNS
        -------
        decoded_polyline : str
            (for now)
        '''
        # Extract the overview polyline
        encoded_polyline = route_data["routes"][0]["overview_polyline"]["points"]

        # Decode the polyline
        decoded_polyline = polyline.decode(encoded_polyline)

        return decoded_polyline

class ExtractorHERE():
    '''
    Provides a method to extract a polyline from given route in json
    '''

    def __init__(self):
        pass

    def extract_map(self, route_data):
        '''
        Extracts usable map data from route in json format.

        PARAMETERS
        ----------
        route_data : str
            The route data as a JSON dictionary

        RETURNS
        -------
        decoded_polyline : str
            (for now)
        '''
        # Extract the overview polyline
        encoded_polyline = route_data["routes"][0]["sections"][0]["polyline"]
        print("Encoded Polyline:", encoded_polyline)

        # Decode the polyline
        decoded_polyline = fp.decode(encoded_polyline)

        return decoded_polyline

# just for testing:
if __name__ == "__main__":
    extractor = Extractor()
    map_data = extractor.extract_map(route_data)
