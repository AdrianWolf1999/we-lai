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

import os
import json
import traceback
from flask import Flask, request, jsonify, send_from_directory
from services.heatmap import Heatmap
from services.webcrawler import WebCrawler

app = Flask(__name__, static_folder="../client", static_url_path="")

heatmap = Heatmap(os.path.join(os.getcwd(), "server/data"))
crawler = WebCrawler(os.path.join(os.getcwd(), "server/data"))


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/route", methods=["GET"])
def get_safe_route():
    try:
        origin = request.args.get("origin")
        destination = request.args.get("destination")
        profile = request.args.get("profile")

        if origin and destination and profile:
            return jsonify(crawler.get_route(origin, destination, profile))
        else:
            return jsonify({"error": "Missing origin or destination or profile"}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server Error: " + str(e)}), 400


@app.route("/heatmap", methods=["GET"])
def get_heatmap_data():
    try:
        return jsonify(heatmap.get_heatmap_and_safe_places())
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server Error: " + str(e)}), 400


@app.route("/add_polygon", methods=["POST"])
def add_new_polygon():
    try:
        polygon = json.loads(request.args.get("polygon"))["coordinates"]
        safety_score = request.args.get("safetyScore")
        heatmap.add_and_save_new_polygon(polygon, safety_score)
        crawler.load_data_from_csv()
        return jsonify(heatmap.get_heatmap_and_safe_places())
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server Error: " + str(e)}), 400


@app.route("/add_safe_place", methods=["POST"])
def add_new_safe_place():
    try:
        coordinates_string_array = request.args.get("coordinates").split(",")
        coordinates = [float(coord) for coord in coordinates_string_array]
        heatmap.add_and_save_new_safe_place(coordinates)
        crawler.load_data_from_csv()
        return jsonify(heatmap.get_heatmap_and_safe_places())
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server Error: " + str(e)}), 400
    
@app.route("/suggestions", methods=["GET"])
def get_suggestions():
    try:
        query = request.args.get("query")
        d = crawler.get_suggestions(query)
        print(d)
        return jsonify(d)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server Error: " + str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
