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

/add_polygon (POST)
    Adds a new polygon to the heatmap with the specified safety score.

/add_safe_place (POST)
    Adds a new safe place to the heatmap with the specified coordinates.

/suggestions (GET)
    Returns a list of suggestions based on the specified query.

Notes:
-----
This module is the entry point of the application.
"""

import json
import os
import traceback

from flask import Flask, jsonify, request, send_from_directory
from services.heatmap import Heatmap
from services.webcrawler import WebCrawler

app = Flask(__name__, static_folder="../client", static_url_path="")

heatmap = Heatmap(os.path.join(os.getcwd(), "server/data"))
crawler = WebCrawler(os.path.join(os.getcwd(), "server/data"))


@app.route("/")
def index():
    print("New client on the map!")
    return send_from_directory(app.static_folder, "index.html")


@app.route("/route", methods=["GET"])
def get_safe_route():
    print("Safe route requested and in calculation...")
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
    print("Heatmap requested and sending to the client...")
    try:
        return jsonify(heatmap.get_heatmap_and_safe_places())
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server Error: " + str(e)}), 400


@app.route("/add_polygon", methods=["POST"])
def add_new_polygon():
    print("New polygon added to map by client!")
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
    print("New safe place added to map by client!")
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
    print("Map suggestions requested and sending to the client...")
    try:
        query = request.args.get("query")
        return jsonify(crawler.get_suggestions(query))
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server Error: " + str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
