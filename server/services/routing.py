import requests
from geopy.distance import geodesic


apiKey = 'be7af08d-d658-48b9-9c98-a42e12bedad8'

badPolygonCoords = [
    [
        [9.175747952191298, 48.77885842296115],
        [9.171542141928168, 48.77518205059932],
        [9.167851405445795, 48.77812316095479],
        [9.175747952191298, 48.77885842296115]
    ]
]

mediumPolygonCoords = [
    [
        [9.175747952191298, 48.77885842296115],
        [9.170641017713573, 48.78103625844229],
        [9.163860032298558, 48.77815139444933],
        [9.165362392124628, 48.77532331297032],
        [9.171542141928168, 48.77518205059932],
        [9.167851405445795, 48.77812316095479],
        [9.175747952191298, 48.77885842296115]
    ]
]

safePlaceCoords = [
    [9.159249890299517, 48.77444649574307],
    [9.187272726117374, 48.77693306770287],
    [9.156329042693785, 48.7710887126689],
    [9.180298917741725, 48.78007508188751],
    [9.159835882638732, 48.767181088145],
    [9.15640023061246, 48.77221531087668],
    [9.159523240043916, 48.782386920761266],
    [9.174948636479553, 48.78380328603663],
    [9.179389394336542, 48.776687892051074],
    [9.158339229109123, 48.78011597246679],
    [9.180623616778, 48.77643995678344],
    [9.187026466233697, 48.78243333377855],
    [9.157206388134662, 48.78128244105962],
    [9.161077228440702, 48.77015046354302],
    [9.182000484086038, 48.77925790101291],
    [9.188719423020755, 48.7687548610763],
    [9.182859253678265, 48.7694632435204],
    [9.188118346384632, 48.77429679937542],
    [9.178978010495042, 48.77345608450865],
    [9.183554054267155, 48.78303642103105],
    [9.172950284894076, 48.76717212174704],
    [9.187082059502073, 48.77615780529339],
    [9.184447215585414, 48.78351297745065],
    [9.177494803619134, 48.77487868724905],
    [9.168230330346096, 48.768562708603595],
    [9.176535153479734, 48.768554743000875],
    [9.156988043256021, 48.76751265609192],
    [9.172379460303358, 48.77497910715981],
    [9.174801439769436, 48.78023417874856],
    [9.182755920234292, 48.77584517435605],
    [9.181264536213527, 48.76999240226302],
    [9.17159833967708, 48.77399698203477],
    [9.186437792514426, 48.779033203115716],
    [9.16736858945693, 48.76804513410138],
    [9.173409899493124, 48.77224375582565],
    [9.159023566265644, 48.77544212126839],
    [9.163462388555105, 48.772374113323366]
]

def get_heatmap():
	data = {
		"badPolygonCoords": badPolygonCoords,
		"mediumPolygonCoords": mediumPolygonCoords,
		"safePlaceCoords": safePlaceCoords
	}
	return data


def api_routing_call(origin, destination, waypoints, profile, optimize):
	url = 'https://graphhopper.com/api/1/route'
	headers = {
		'Content-Type': 'application/json'
	}
	data = {
		"profile": profile,
		"points": [
			origin.split(','),  # Source coordinates
			*[wp.split(',') for wp in waypoints], # waypoints
			destination.split(',')  # Target coordinates
		],
		"ch.disable": True,
		"points_encoded": False,		
		"optimize": optimize,
		"custom_model": {
			"priority": [
				{
					"if": "in_bad",
					"multiply_by": "0.01"
				},
				{
					"else_if": "in_medium",
					"multiply_by": "0.3"
				}
			],
			"areas": {
				"type": "FeatureCollection",
				"features": [
					{
						"type": "Feature",
						"id": "bad",
						"properties": {},
						"geometry": {
							"type": "Polygon",
							"coordinates": badPolygonCoords
						}
					},
					{
						"type": "Feature",
						"id": "medium",
						"properties": {},
						"geometry": {
							"type": "Polygon",
							"coordinates": mediumPolygonCoords
						}
					}
				]
			}
		}
	}


	query = {
	"key": apiKey
	}

	try:
		response = requests.post(url, json=data, headers=headers, params=query)

		data = response.json()
	
		if response.ok:
			ret = response.json()
		else:
			ret = {}
	except:
		ret = {}
	
	return ret

def get_route(origin, destination, profile):
	initial_route = api_routing_call(origin, destination, [], profile, "false")

	if 'paths' in initial_route and initial_route['paths']:
		waypoints = find_nearby_safe_places(initial_route, safePlaceCoords, 0.05, 0.1)

		print("Waypoints:")
		print(waypoints)
		print("###########")

		final_route = {}

		if waypoints:		
			final_route = api_routing_call(origin, destination, waypoints, profile, "false")
		else:
			final_route = initial_route

		return final_route

def is_within_distance(coord1, coord2, max_distance_km=0.5):
    return geodesic(coord1, coord2).km <= max_distance_km

def find_nearby_safe_places(route, safe_places, max_distance_for_no_detour=0.1, max_distance_for_detour=0.2):
	route = route['paths'][0]
	total_distance = route['distance']

	waypoints = []

	num_segments = len(route['points']['coordinates'])
	last_coordinate = route['points']['coordinates'][0]
	distance_since_last_checkpoint = 0
	distance_since_start = 0
	checkpoint_interval = 0.5
	i = 0

	while i < num_segments:
		current_coordinate = route['points']['coordinates'][i]
		distance = geodesic(current_coordinate, last_coordinate).kilometers
		distance_since_last_checkpoint = distance_since_last_checkpoint + distance
		distance_since_start = distance_since_start + distance
		last_coordinate = current_coordinate

		more_than_250m_from_finish = (total_distance - distance_since_start) > 0.25
		new_checkpoint_interval_reached = distance_since_last_checkpoint > checkpoint_interval and more_than_250m_from_finish

		if new_checkpoint_interval_reached:
			for safe_place in safe_places:
				waypoint_already_close_enough = False
				if is_within_distance(current_coordinate, safe_place, max_distance_for_no_detour):
					waypoint_already_close_enough = True
					break				
			
			if waypoint_already_close_enough:
				distance_since_last_checkpoint = 0
			else:
				for safe_place in safe_places:
					if is_within_distance(current_coordinate, safe_place, max_distance_for_detour):
						waypoints.append(f"{safe_place[0]},{safe_place[1]}")
						distance_since_last_checkpoint = 0
						break

		i = i + 1
	return list(set(waypoints))