from services.extractor import Extractor
from services.mapper import Mapper
from services.visualiser import Visualiser
from services.webcrawler import WebCrawler

# Example usage
ORIGIN = "48.783391,9.180221"
DESTINATION = "48.779477,9.179306"


def main():
    # Get the route in json format from Google API
    crawler = WebCrawler()
    extractor = Extractor()
    mapper = Mapper()
    visualiser = Visualiser()

    route_data = crawler.get_route(ORIGIN, DESTINATION, crawler.load_api_key())

    decoded_polyline = extractor.extract_map(route_data)
    print("Decoded polyline:\n", decoded_polyline)

    waypoints = mapper.add_waypoints(decoded_polyline)
    print("Waypoints:\n", waypoints)

    # latitudes, longitudes, waypoint_latitudes, waypoint_longitudes, start_lat, start_lon, end_lat, end_lon
    map_values = mapper.add_map_values(decoded_polyline, waypoints)
    print(map_values)

    # Plot:
    visualiser.plot_map(map_values)


if __name__ == "__main__":
    main()
