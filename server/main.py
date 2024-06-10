"""
Main application module.

This module contains the main application logic, including the Flask app instance and routes.

Attributes:
----------
app : Flask
    The Flask app instance.

heatmap : Heatmap
    The Heatmap instance used to generate heatmap data.

crawler : WebCrawler
    The WebCrawler instance used to fetch route data.

Routes:
------
/ (GET)
    Serves the index.html file from the client directory.

/route (GET)
    Returns a safe route between the specified origin and destination for the specified profile.

/heatmap (GET)
    Returns the heatmap data, including bad polygon coordinates, medium polygon coordinates, and safe place coordinates.

Notes:
-----
This module is the entry point of the application.
"""

from flask import Flask, request, jsonify, send_from_directory
from services.heatmap import Heatmap
from services.webcrawler import WebCrawler
import os

app = Flask(__name__, static_folder="../client", static_url_path="")

heatmap = Heatmap(os.path.join(os.getcwd(), "server/data"))
crawler = WebCrawler(os.path.join(os.getcwd(), "server/data"))

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route('/route', methods=['GET'])
def get_safe_route():
    
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    profile = request.args.get('profile')
    
    if origin and destination and profile:
        return jsonify(crawler.get_route(origin, destination, profile))
    else:
        return jsonify({'error': 'Missing origin or destination or profile'}), 400
    
@app.route('/heatmap', methods=['GET'])
def get_heatmap_data():
    return jsonify(heatmap.get_heatmap_and_safe_places())

@app.route('/heatmap', methods=['SET'])
def add_new_polygon():
    polygon = request.args.get('polygon')
    safety_score = request.args.get('safetyScore')
    heatmap.add_and_save_new_polygon(polygon, safety_score)
    crawler.load_data_from_csv()
    return jsonify({"status": "success"})

@app.route('/safe_place', methods=['SET'])
def add_new_safe_place():
    coordinates = request.args.get('coordinates')
    heatmap.add_and_save_new_safe_place(coordinates)
    crawler.load_data_from_csv()
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(debug=True)
    