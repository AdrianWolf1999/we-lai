const bringMeHomeButtonElement = document.getElementById('bringMeHomeButton');
const searchInputElement = document.getElementById('searchInput');
const suggestionsElement = document.getElementById('suggestions');
const toggleMetaButtonElement = document.getElementById('toggleMetaButton');
const defaultRadioButtonElement = document.getElementById('defaultRadioButton');
const polygonRadioButtonElement = document.getElementById('polygonRadioButton');
const safePlaceRadioButtonElement = document.getElementById('safePlaceRadioButton');
    
const map = L.map('mapContainer').setView([52.5, 13.4], 16);

let heatmapPolygonCoords = [];
let safetyScores = [];
let safePlaceCoords = [];

let heatmapPolygons = [];
let safePlaces = [];

let metaShown = true;

let targetMarker = null;
const myCoordinates = L.latLng(48.776111, 9.174778);
let myMarker = null;
let routes = [];
const profile = 'foot';

let editMode = 'default'
let editPolygonCoords = []
let editSafePlaceCoords = []

async function getHeatmapData() {
	try {
        // Construct the URL with query parameters
        const url = new URL('/heatmap', window.location.origin);

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const heatmapData = await response.json();
		
		heatmapPolygonCoords = heatmapData.heatmap.coordinates;
		safetyScores = heatmapData.heatmap.safetyScores;
        safePlaceCoords = heatmapData.safePlaces.coordinates;

		createHeatmap();
    } catch (error) {
        console.error(error);
    }
}

function valueToColor(value) {
    value = Math.max(0, Math.min(1, value));
    var hue = value * 60;
    return `hsl(${hue}, 100%, 50%)`;
}
function createHeatmap() {
    for (let i in heatmapPolygonCoords) {
        heatmapPolygons.push(L.polygon(heatmapPolygonCoords[i], { color: valueToColor(safetyScores[i]), fillOpacity: 0.3, weight: 0 }).addTo(map));
    }

    for (let i in safePlaceCoords) {
        safePlaces.push(L.circle(safePlaceCoords[i], {color: 'green', fillColor: 'green', fillOpacity: 0.5, weight: 0, radius: 40}).addTo(map));
    }
}

function toggleHeatmap() {
	metaShown = !metaShown;

	if (metaShown) {
		for (let i in heatmapPolygons) {
			heatmapPolygons[i].addTo(map);
		}
		for (let i in safePlaces) {
			safePlaces[i].addTo(map);
		}
	} else {
		for (let i in heatmapPolygons) {
			map.removeLayer(heatmapPolygons[i]);
		}
		for (let i in safePlaces) {
			map.removeLayer(safePlaces[i]);
		}
	}
}

searchInputElement.addEventListener('input', () => {
    const query = searchInputElement.value;
    if (query.length >= 3) {
        getSuggestions(query);
    } else {
        suggestionsElement.style.display = 'none';
    }
});


function getSuggestions(query) {
    fetch(`https://graphhopper.com/api/1/geocode?q=${query}&key=${apiKey}`)
        .then(response => response.json())
        .then(data => {
            const suggestions = suggestionsElement;
            suggestions.innerHTML = '';
            if (data.hits && data.hits.length > 0) {
                data.hits.forEach(hit => {
                    const suggestion = document.createElement('div');
                    suggestion.textContent = hit.name;
                    suggestion.addEventListener('click', () => {
                        selectLocation(hit.point.lat, hit.point.lng, hit.name);
                    });
                    suggestions.appendChild(suggestion);
                });
                suggestions.style.display = 'block';
            } else {
                suggestions.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Geocoding error:', error);
        });
}

function selectLocation(lat, lng, label) {
    const coordinates = L.latLng(lat, lng);

    searchInputElement.value = label;
    suggestionsElement.style.display = 'none';

    onTargetChanged(coordinates);
}

function showTargetMarker(coordinates) {
	const redIcon = L.icon({
        iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    if (!targetMarker) {
        targetMarker = L.marker(coordinates, { icon: redIcon }).addTo(map);
    } else {
        targetMarker.setLatLng(coordinates);
    }
}

function showMyMarker() {
    if (!myMarker) {
        myMarker = L.marker(myCoordinates).addTo(map);
    }
}

function onTargetChanged(coordinates) {
	removeRoutes();
    showTargetMarker(coordinates);
	changeMapView(coordinates);
}

function changeMapView(coordinates) {
    map.setView(coordinates, map.getZoom());
}

function displayRoutes(routesData) {
    if (!routesData) { return; }

    removeRoutes();

	for (let i in routesData) {
		// Extracting route geometry
		const routeGeometry = routesData[i].points.coordinates.map(coord => [coord[0], coord[1]]);

		let alpha = 0.5;
		if (i == 0) {
			alpha = 1;
		}

		// Creating GeoJSON object for the route
		let route = L.geoJSON({
			type: 'LineString',
			coordinates: routeGeometry
		}, {
			style: {
				color: 'blue',
				weight: 5,
				opacity: alpha
			}
		}).addTo(map);

		routes.push(route);
	}

	map.fitBounds(routes[routes.length - 1].getBounds());
}

function removeRoutes() {
	if (routes) {
		for (let i in routes) {
			map.removeLayer(routes[i]);
		}
	}
	routes = [];
}

// Function to handle right-click event and set target marker
function addTargetMarker(e) {
    const coordinates = e.latlng;
    onTargetChanged(coordinates);
}

// Add event listener for right-click event on the map
map.on('contextmenu', addTargetMarker);

toggleMetaButtonElement.addEventListener('click', () => {
	toggleHeatmap();
});

bringMeHomeButtonElement.addEventListener('click', async() => {
    if (!targetMarker || !myMarker) { return; }

	const origin = `${myCoordinates.lng},${myCoordinates.lat}`;
	const destination =  `${targetMarker.getLatLng().lng},${targetMarker.getLatLng().lat}`;
	
	try {
        // Construct the URL with query parameters
        const url = new URL('/route', window.location.origin);
        url.searchParams.append('origin', origin);
        url.searchParams.append('destination', destination);
		url.searchParams.append('profile', profile);

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const routeData = await response.json();
		console.log(routeData);

		if (routeData['paths'] != undefined) {
			displayRoutes(routeData['paths']);
		}
    } catch (error) {
        console.error(error);
    }
});

defaultRadioButtonElement.addEventListener("change", function(event) {
    if (event.target.value) {
        editMode = 'default';
        bringMeHomeButtonElement.textContent = "Bring Me Home";
    }
});

polygonRadioButtonElement.addEventListener("change", function(event) {
    if (event.target.value) {
        editMode = 'polygon';
        bringMeHomeButtonElement.textContent = "Add Polygon";
    }    
});

safePlaceRadioButtonElement.addEventListener("change", function(event) {
    if (event.target.value) {
        editMode = 'safePlace';
        bringMeHomeButtonElement.textContent = "Add Safe Place";
    }
});

L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);
showMyMarker();
changeMapView(myCoordinates);
getHeatmapData();