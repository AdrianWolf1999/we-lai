// Replace with your own HERE API key
const platform = new H.service.Platform({
	apikey: '7Ais4hjOWSGcC71Eb4sTsHejcUqHNEBuyCpsdQIEYPs'
});

const defaultLayers = platform.createDefaultLayers();

const map = new H.Map(
	document.getElementById('mapContainer'),
	defaultLayers.vector.normal.map,
	{
		zoom: 14,
		center: { lat: 52.5, lng: 13.4 }
	}
);

const ui = H.ui.UI.createDefault(map, defaultLayers);
const mapEvents = new H.mapevents.MapEvents(map);
const behavior = new H.mapevents.Behavior(mapEvents);

const geocoder = platform.getSearchService();

let targetCoordinates = null;
const myCoordinates = { lat: 48.776111, lng: 9.174778 };
let route = null;


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

	document.getElementById('searchInput').value = label;
	document.getElementById('suggestions').style.display = 'none';

	onTargetChanged(coordinates);
}

// add a resize listener to make sure that the map occupies the whole container
window.addEventListener('resize', () => map.getViewPort().resize());

function showTargetMarker() {
	if (!targetCoordinates) return;

	map.addObject(new H.map.Marker(targetCoordinates));
}

function showMyPosition(){
	if (!myCoordinates) return;

	// Create the svg mark-up
	var svgMarkup = '<svg  width="24" height="24" xmlns="http://www.w3.org/2000/svg">' +
					'<circle cx="12" cy="12" r="10" stroke="white" stroke-width="2" fill="blue"/>' +
					'</svg>';
	var myPositionIcon = new H.map.Icon(svgMarkup.replace('${FILL}', 'blue').replace('${STROKE}', 'red'));
	map.addObject(new H.map.Marker(myCoordinates, {icon: myPositionIcon}));
}

function showRoute() {
	if (!route) return;

	route.sections.forEach((section) => {
		// Create a linestring to use as a route polyline
		let linestring = H.geo.LineString.fromFlexiblePolyline(section.polyline);			

		// Create a polyline to display the route:
		let routeLine = new H.map.Polyline(linestring, {
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

function onTargetChanged(coordinates) {
	targetCoordinates = coordinates;
	route = null;
	map.removeObjects(map.getObjects());
	showMyPosition();
	showTargetMarker();
}

function onRouteChanged() {
	map.removeObjects(map.getObjects());
	showMyPosition();
	showTargetMarker();
	showRoute();
}

// Function to change the view position of the map
function changeMapView(coordinates) {
    map.setCenter(coordinates);
	map.setZoom(14);
}

// Function to add a marker on right-click
function onRightClickSetMarker(event) {
    if (event.originalEvent.button === 2) { // Check if right-click
        const coordinates = map.screenToGeo(event.viewportX, event.viewportY);
		onTargetChanged(coordinates);
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
		'origin': `${myCoordinates.lat},${myCoordinates.lng}`,
		'destination': `${targetCoordinates.lat},${targetCoordinates.lng}`,
		'return': 'polyline,turnByTurnActions,actions,instructions,travelSummary',
		'avoid[areas]': 'polygon:48.772764,9.165117;48.770764,9.170117;48.765000,9.170117;48.765000,9.160000;48.772764,9.160000'
	};

	function calculateRoute(platform, params) {
		var router = platform.getRoutingService(null, 8);

		router.calculateRoute(
			params,
			onSuccess,
			onError
		);
	}

	function onSuccess(result) {
		route = result.routes[0];
		onRouteChanged();
	}

	function onError(error) {
		console.error('Error:', error);
	}

	calculateRoute(platform, routingParameters);
});

showMyPosition();
changeMapView(myCoordinates);
