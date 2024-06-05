// Replace with your own HERE API key
const platform = new H.service.Platform({
	apikey: '7Ais4hjOWSGcC71Eb4sTsHejcUqHNEBuyCpsdQIEYPs'
});

const defaultLayers = platform.createDefaultLayers();

const map = new H.Map(
	document.getElementById('mapContainer'),
	defaultLayers.vector.normal.map,
	{
		zoom: 10,
		center: { lat: 52.5, lng: 13.4 }
	}
);

const ui = H.ui.UI.createDefault(map, defaultLayers);
const mapEvents = new H.mapevents.MapEvents(map);
const behavior = new H.mapevents.Behavior(mapEvents);

const geocoder = platform.getSearchService();

let targetCoordinates = null;
// Dummy for gps location
const sourceCoordinates = { lat: 48.776111, lng: 9.174778 };

let routeLine = null;
let currentTargetMarker = null;
let myPositionMarker = null;



var polygons = [
	{
		type: 'polygon',
		coordinates: [
			[48.7738, 9.1825],
			[48.7747, 9.1832],
			[48.7739, 9.1838],
			[48.7733, 9.1831],
			[48.7738, 9.1825]
		]
	},
	{
		type: 'polygon',
		coordinates: [
			[48.7762, 9.1801],
			[48.7768, 9.1796],
			[48.7773, 9.1805],
			[48.7765, 9.1810],
			[48.7762, 9.1801]
		]
	}
];

var corridors = [
	{
		type: 'corridor',
		coordinates: [
			[48.7752, 9.1815],
			[48.7760, 9.1803]
		]
	},
	{
		type: 'corridor',
		coordinates: [
			[48.7766, 9.1812],
			[48.7770, 9.1799]
		]
	}
];

function drawPolygons(polygons, corridors) {
	var group = new H.map.Group();
	map.addObject(group);

	// Draw polygons
	polygons.forEach(function(polygon) {
		var strip = new H.geo.Strip();
		polygon.coordinates.forEach(function(coords) {
			strip.pushLatLngAlt(coords[0], coords[1]);
		});
		var polygonShape = new H.map.Polygon(strip);
		group.addObject(polygonShape);
	});

	// Draw corridors
	corridors.forEach(function(corridor) {
		var strip = new H.geo.Strip();
		corridor.coordinates.forEach(function(coords) {
			strip.pushLatLngAlt(coords[0], coords[1]);
		});
		var corridorShape = new H.map.Polyline(strip, { style: { lineWidth: 4, strokeColor: 'blue' } });
		group.addObject(corridorShape);
	});
}

// Example polygons and corridors data similar to the JSON provided earlier
var polygons = [
	{
		type: 'polygon',
		coordinates: [
			[48.775, 9.180],
			[48.775, 9.185],
			[48.770, 9.185],
			[48.770, 9.180],
			[48.775, 9.180]
		]
	}
];


// Call the function to draw polygons and corridors
function drawPolygons(polygons) {
	var group = new H.map.Group();
	map.addObject(group);

	// Draw polygons
	polygons.forEach(function(polygon) {
		var strip = new H.geo.LineString();
		polygon.coordinates.forEach(function(coords) {
			strip.pushLatLngAlt(coords[0], coords[1]);
		});
		var polygonShape = new H.map.Polygon(strip);
		group.addObject(polygonShape);
	});
}

function drawAvoidancePolygon(map) {
	var polygonCoordinates = [
		{ lat: 48.772764, lng: 9.165117 },
		{ lat: 48.770764, lng: 9.170117 },
		{ lat: 48.765000, lng: 9.160000 },
	];


	// Create a LineString and add the polygon coordinates
	var linestring = new H.geo.LineString();
	polygonCoordinates.forEach(point => linestring.pushPoint(point));
	linestring.pushPoint(polygonCoordinates[0]); // Close the polygon

	// Create a polygon and add it to the map
	var polygon = new H.map.Polygon(linestring, {
		style: {
			strokeColor: 'red',
			fillColor: 'rgba(255, 0, 0, 0.5)',
			lineWidth: 2
		}
	});
	map.addObject(polygon);
}

document.getElementById('searchInput').addEventListener('input', () => {
	const query = document.getElementById('searchInput').value;
	if (query.length >= 3) {
		getSuggestions(query);
	} else {
		document.getElementById('suggestions').style.display = 'none';
	}
});

function getSuggestions(query) {
	geocoder.geocode({ q: query }, (result) => {
		const suggestions = document.getElementById('suggestions');
		suggestions.innerHTML = '';
		if (result.items.length > 0) {
			result.items.forEach((item) => {
				const suggestion = document.createElement('div');
				suggestion.textContent = item.address.label;
				suggestion.addEventListener('click', () => {
					selectLocation(item.position, item.address.label);
				});
				suggestions.appendChild(suggestion);
			});
			suggestions.style.display = 'block';
		} else {
			suggestions.style.display = 'none';
		}
	}, (error) => {
		console.error('Geocoding error: ' + error.toString());
	});
}

function selectLocation(position, label) {
	const coordinates = {
		lat: position.lat,
		lng: position.lng
	};
	map.setCenter(coordinates);
	map.setZoom(14);

	showMeAndTarget(coordinates);

	document.getElementById('searchInput').value = label;
	document.getElementById('suggestions').style.display = 'none';
}

function showMeAndTarget(coordinates) {
	showMyPosition(map);

	targetCoordinates = coordinates;

	if (routeLine) {
		map.removeObject(routeLine);
	}

	if (currentTargetMarker) {
		map.removeObject(currentTargetMarker);
	}
	currentTargetMarker = new H.map.Marker(coordinates);
	map.addObject(currentTargetMarker);
}

// add a resize listener to make sure that the map occupies the whole container
window.addEventListener('resize', () => map.getViewPort().resize());

function showMyPosition(map){
	let coordinates = sourceCoordinates;
	// Create the svg mark-up
	var svgMarkup = '<svg  width="24" height="24" xmlns="http://www.w3.org/2000/svg">' +
					'<circle cx="12" cy="12" r="10" stroke="white" stroke-width="2" fill="blue"/>' +
					'</svg>';

	var myPositionIcon = new H.map.Icon(svgMarkup.replace('${FILL}', 'blue').replace('${STROKE}', 'red'));

	if (myPositionMarker) {
		map.removeObject(myPositionMarker);
	}

	myPositionMarker = new H.map.Marker(coordinates, {icon: myPositionIcon});

	map.addObject(myPositionMarker);
}

// Function to change the view position of the map
function changeMapView(coordinates) {
    map.setCenter(coordinates);
}

// Function to add a marker on right-click
function onRightClickSetMarker(event) {
    if (event.originalEvent.button === 2) { // Check if right-click
        const coordinates = map.screenToGeo(event.viewportX, event.viewportY);
		showMeAndTarget(coordinates);
    }
}

map.addEventListener('contextmenu', function(evt) {
    evt.preventDefault(); // Prevent the default context menu from appearing
    onRightClickSetMarker(evt);
});

document.getElementById('bringMeHomeButton').addEventListener('click', () => {
	if (!targetCoordinates) { return; }

	const routingParameters = {
		'routingMode': 'fast',
		'transportMode': 'pedestrian',
		'origin': `${sourceCoordinates.lat},${sourceCoordinates.lng}`,
		'destination': `${targetCoordinates.lat},${targetCoordinates.lng}`,
		'return': 'polyline,turnByTurnActions,actions,instructions,travelSummary',
		'avoid[areas]': 'polygon:48.772764,9.165117;48.770764,9.170117;48.765000,9.170117;48.765000,9.160000;48.772764,9.160000'
	};
	console.log(routingParameters);
	function calculateRouteFromAtoB(platform, params) {
		var router = platform.getRoutingService(null, 8);

		router.calculateRoute(
			params,
			onSuccess,
			onError
		);
	}

	function onSuccess(result) {
		var route = result.routes[0];
		addRouteShapeToMap(route);
	}

	function onError(error) {
		console.error('Error:', error);
	}

	function addRouteShapeToMap(route) {
		route.sections.forEach((section) => {
			// Create a linestring to use as a route polyline
			let linestring = H.geo.LineString.fromFlexiblePolyline(section.polyline);

			if (map.getObjects().indexOf(routeLine) !== -1) {
				console.log(routeLine);
				map.removeObject(routeLine);
			}
			

			// Create a polyline to display the route:
			routeLine = new H.map.Polyline(linestring, {
				style: { strokeColor: 'blue', lineWidth: 5 }
			});

			// Add the route polyline and the two markers to the map:
			map.addObject(routeLine);

			const boundingBox =  routeLine.getBoundingBox();

			// Zoom the map to the polyline:
			map.getViewModel().setLookAtData({
				bounds: boundingBox
			});			
		});
	}

	calculateRouteFromAtoB(platform, routingParameters);
});

showMyPosition(map);
changeMapView(sourceCoordinates);
drawAvoidancePolygon(map);
