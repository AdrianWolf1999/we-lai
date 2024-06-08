from flask import Flask, request, jsonify, send_from_directory
from services.routing import get_route, get_heatmap

app = Flask(__name__, static_folder="../client", static_url_path="")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route('/route', methods=['GET'])
def get_safe_route():
    
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    profile = request.args.get('profile')
    
    if origin and destination:
        return jsonify(get_route(origin, destination, profile))
    else:
        return jsonify({'error': 'Missing origin or destination'}), 400
    
@app.route('/heatmap', methods=['GET'])
def get_heatmap_data():
    return jsonify(get_heatmap())


if __name__ == "__main__":
    app.run(debug=True)
    