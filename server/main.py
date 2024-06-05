from flask import Flask, request, jsonify, send_from_directory
from services.extractor import Extractor
from services.mapper import Mapper
from services.visualiser import Visualiser
from services.webcrawler import WebCrawler

# Example usage
ORIGIN = "48.783391,9.180221"
DESTINATION = "48.779477,9.179306"

app = Flask(__name__, static_folder="../client", static_url_path="")


# Initialize services
crawler = WebCrawler()
extractor = Extractor()
mapper = Mapper()
visualiser = Visualiser()

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route('/route', methods=['GET'])
def get_safe_route():
    
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    
    if origin and destination:
        route_data = crawler.get_route(origin, destination, crawler.load_api_key())
        decoded_polyline = extractor.extract_map(route_data)
        waypoints = mapper.add_waypoints(decoded_polyline)
        map_values = mapper.add_map_values(decoded_polyline, waypoints)
        
        # TODO: Return a map and not only map_values -> Visualiser
        # OR BETTER: visualise the map_values on client side
        return jsonify({'route': map_values})
    else:
        return jsonify({'error': 'Missing origin or destination'}), 400


if __name__ == "__main__":
    app.run(debug=True)
    