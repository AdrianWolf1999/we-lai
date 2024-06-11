const bringMeHomeButtonElement = document.getElementById('bringMeHomeButton');
const searchInputElement = document.getElementById('searchInput');
const suggestionsElement = document.getElementById('suggestions');
const toggleMetaButtonElement = document.getElementById('toggleMetaButton');
const defaultRadioButtonElement = document.getElementById('defaultRadioButton');
const polygonRadioButtonElement = document.getElementById('polygonRadioButton');
const safePlaceRadioButtonElement = document.getElementById('safePlaceRadioButton');
const safetyScoreInputElement = document.getElementById('safetyScoreInput');
const defaultRadioButtonLabelElement = document.getElementById('defaultRadioButtonLabel');
const polygonRadioButtonLabelElement = document.getElementById('polygonRadioButtonLabel');
const safePlaceRadioButtonLabelElement = document.getElementById('safePlaceRadioButtonLabel');

const map = L.map('mapContainer').setView([52.5, 13.4], 16);

let debounceTimer;

let heatmapPolygonCoords = [];
let safetyScores = [];
let safePlaceCoords = [];
let preferredCoords = [];

let heatmapPolygons = [];
let safePlaces = [];
let preferredPolygons = [];

let metaShown = true;

let targetMarker = null;
const myCoordinates = L.latLng(48.776111, 9.174778);
let myMarker = null;
let routes = [];
const profile = 'foot';

let editMode = 'default'
let editPolygonCoords = []
let editSafePlaceCoords = []






// HEATMAP FUNCTIONS
//--------------------------------------------------------------------------------------------------

// Calls the server to get the heatmap data
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

        if (heatmapData['error'] != undefined) {
            console.error(heatmapData['error']);
            return;
        }
		
		heatmapPolygonCoords = heatmapData.heatmap.coordinates;
		safetyScores = heatmapData.heatmap.safetyScores;
        safePlaceCoords = heatmapData.safePlaces.coordinates;
        preferredCoords = heatmapData.preferred.coordinates;

		createHeatmap();
    } catch (error) {
        console.error(error);
    }
}

// Convert a value to a color. Should be between 0 and 1
function valueToColor(value) {
    value = Math.max(0, Math.min(1, value));
    var hue = value * 60;
    return `hsl(${hue}, 100%, 50%)`;
}

// Adds heatmap elements to the map
function createHeatmap() {
    for (let i in heatmapPolygons) {
        map.removeLayer(heatmapPolygons[i]);
    }
    for (let i in safePlaces) {
        map.removeLayer(safePlaces[i]);
    }
    for (let i in preferredPolygons) {
        map.removeLayer(preferredPolygons[i]);
    }

    heatmapPolygons = [];
    safePlaces = [];
    preferredPolygons = [];
    metaShown = true;

    for (let i in heatmapPolygonCoords) {
        heatmapPolygons.push(L.polygon(heatmapPolygonCoords[i], { color: valueToColor(safetyScores[i]), fillOpacity: 0.3, weight: 0 }).addTo(map));
    }

    for (let i in preferredCoords) {
        preferredPolygons.push(L.polygon(preferredCoords[i], { color: "#28ff65", fillOpacity: 0.3, weight: 0 }).addTo(map));
    }

    for (let i in safePlaceCoords) {
        safePlaces.push(L.circle(safePlaceCoords[i], {color: '#fff', fillColor: '#00ff26', fillOpacity: 0.8, weight: 1, radius: 20}).addTo(map));
    }
}

// Enables/Disables the heatmap elements
function toggleHeatmap() {
	metaShown = !metaShown;

	if (metaShown) {
		for (let i in heatmapPolygons) {
			heatmapPolygons[i].addTo(map);
		}
		for (let i in safePlaces) {
			safePlaces[i].addTo(map);
		}
        for (let i in preferredPolygons) {
			preferredPolygons[i].addTo(map);
		}
	} else {
		for (let i in heatmapPolygons) {
			map.removeLayer(heatmapPolygons[i]);
		}
		for (let i in safePlaces) {
			map.removeLayer(safePlaces[i]);
		}
        for (let i in preferredPolygons) {
			map.removeLayer(preferredPolygons[i]);
		}
	}
}






// LOCATION SEARCH FUNCTIONS
//--------------------------------------------------------------------------------------------------

// Gets location suggestions from graphhopper for the search string
async function getSuggestions(query) {
    try {
        // Construct the URL with query parameters
        const url = new URL('/suggestions', window.location.origin);
        url.searchParams.append('query', query);

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const suggestions = await response.json();

        if (suggestions['error'] != undefined) {
            console.error(suggestions['error']);
            return;
        }

        onReceivedSuggestions(suggestions);
    } catch (error) {
        console.error(error);
    }
}

function onReceivedSuggestions(data) {
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
}

// Sets the input field to the selected location and updates the target coordinates
function selectLocation(lat, lng, label) {
    const coordinates = L.latLng(lat, lng);

    searchInputElement.value = label;
    suggestionsElement.style.display = 'none';

    onTargetChanged(coordinates);
}




// TARGET MARKER FUNCTIONS
//--------------------------------------------------------------------------------------------------

// Shows/moves the marker for the target coordinates
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

// Shows my current position
function showMyMarker() {
    if (!myMarker) {
        myMarker = L.marker(myCoordinates).addTo(map);
    }
}

// Update map view if target marker changed its position
function onTargetChanged(coordinates) {
	removeRoutes();
    showTargetMarker(coordinates);
	changeMapView(coordinates);
}



// MAP VIEW FUNCTIONS
//--------------------------------------------------------------------------------------------------

// Move view on map
function changeMapView(coordinates) {
    map.setView(coordinates, map.getZoom());
}


// ROUTING DISPLAY FUNCTIONS
//--------------------------------------------------------------------------------------------------

// Show routes on map
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

// Remove routes from map
function removeRoutes() {
	if (routes) {
		for (let i in routes) {
			map.removeLayer(routes[i]);
		}
	}
	routes = [];
}



// RIGHT-CLICK HELPER FUNCTIONS
//--------------------------------------------------------------------------------------------------

// Handles right-click event
function onRightClick(e) {
    switch (editMode) {
        case 'default':
            onTargetChanged(e.latlng);
            break;
        case 'polygon':
            editPolygonCoords.push([e.latlng.lng, e.latlng.lat]);
            break;
        case 'safePlace':
            editSafePlaceCoords = [e.latlng.lng, e.latlng.lat];
            break;
        default:
            break;
    }
}


// SERVER ROUTING AND HEATMAP UPDATE CALL FUNCTIONS
//--------------------------------------------------------------------------------------------------

// Handles the press of the bringMeHome-button (routing / adding polygons / adding safe places)
function onBringMeHomeButtonPressed() {
    switch (editMode) {
        case 'default':
            requestRouteFromServer();
            break;
        case 'polygon':
            sendSetPolygonToServer();
            break;
        case 'safePlace':
            sendSetSafePlaceToServer();
            break;
        default:
            break;
    }
}

async function requestRouteFromServer() {
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

        if (routeData['error'] != undefined) {
            console.error(routeData['error']);
            return;
        }

        if (routeData['paths'] != undefined) {
            displayRoutes(routeData['paths']);
        }
    } catch (error) {
        console.error(error);
    }
}

async function sendSetPolygonToServer() {
    if (editPolygonCoords.length === 0) return;

    let input = safetyScoreInputElement.value;
    let safetyScore = 0;
    if (input) {
        safetyScore = parseFloat(input);
    }
    try {
        // Construct the URL with query parameters
        const url = new URL('/add_polygon', window.location.origin);
        url.searchParams.append('polygon', JSON.stringify({"coordinates": editPolygonCoords}));
        url.searchParams.append('safetyScore', safetyScore);

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const heatmapData = await response.json();

        if (heatmapData['error'] != undefined) {
            console.error(heatmapData['error']);
            return;
        }

        heatmapPolygonCoords = heatmapData.heatmap.coordinates;
        safetyScores = heatmapData.heatmap.safetyScores;
        safePlaceCoords = heatmapData.safePlaces.coordinates;
        preferredCoords = heatmapData.preferred.coordinates;

        createHeatmap();

        editPolygonCoords = [];
    } catch (error) {
        console.error(error);
    }
}

async function sendSetSafePlaceToServer() {
    if (editSafePlaceCoords.length === 0) return;

    try {
        // Construct the URL with query parameters
        const url = new URL('/add_safe_place', window.location.origin);
        url.searchParams.append('coordinates', editSafePlaceCoords);

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const heatmapData = await response.json();

        if (heatmapData['error'] != undefined) {
            console.error(heatmapData['error']);
            return;
        }

        heatmapPolygonCoords = heatmapData.heatmap.coordinates;
        safetyScores = heatmapData.heatmap.safetyScores;
        safePlaceCoords = heatmapData.safePlaces.coordinates;
        preferredCoords = heatmapData.preferred.coordinates;

        createHeatmap();

        editSafePlaceCoords = [];
    } catch (error) {
        console.error(error);
    }
}


// EVENT LISTENERS
//--------------------------------------------------------------------------------------------------

// Right-click event on the map
map.on('contextmenu', onRightClick);

// Toggle heatmap
toggleMetaButtonElement.addEventListener('click', () => {
	toggleHeatmap();
});

// Search input
searchInputElement.addEventListener('input', () => {
    const query = searchInputElement.value;

    // Clear the previous timer if there is one
    clearTimeout(debounceTimer);

    // Set a new timer
    debounceTimer = setTimeout(() => {
        if (query.length >= 3) {
            getSuggestions(query);
        } else {
            suggestionsElement.style.display = 'none';
        }
    }, 500); // 500 milliseconds = 0.5 seconds
});

// Bring me home button
bringMeHomeButtonElement.addEventListener('click', () => {onBringMeHomeButtonPressed()});

// Radio button default
defaultRadioButtonElement.addEventListener("change", function(event) {
    if (event.target.value) {
        safePlaceRadioButtonLabelElement.style.backgroundColor = "#676666";
        polygonRadioButtonLabelElement.style.backgroundColor = "#676666";
        defaultRadioButtonLabelElement.style.backgroundColor = "#2c19f4";
        editMode = 'default';
        bringMeHomeButtonElement.textContent = "Bring Me Home";
        safetyScoreInputElement.style.display = 'none';
        editPolygonCoords = [];
        editSafePlaceCoords = [];
    }
});

// Radio button add polygon
polygonRadioButtonElement.addEventListener("change", function(event) {
    if (event.target.value) {
        safePlaceRadioButtonLabelElement.style.backgroundColor = "#676666";
        polygonRadioButtonLabelElement.style.backgroundColor = "#2c19f4";
        defaultRadioButtonLabelElement.style.backgroundColor = "#676666";
        editMode = 'polygon';
        bringMeHomeButtonElement.textContent = "Add Polygon";
        safetyScoreInputElement.style.display = 'block';
        editPolygonCoords = [];
        editSafePlaceCoords = [];
    }    
});

// Radio button add safe place
safePlaceRadioButtonElement.addEventListener("change", function(event) {
    if (event.target.value) {
        safePlaceRadioButtonLabelElement.style.backgroundColor = "#2c19f4";
        polygonRadioButtonLabelElement.style.backgroundColor = "#676666";
        defaultRadioButtonLabelElement.style.backgroundColor = "#676666";
        editMode = 'safePlace';
        bringMeHomeButtonElement.textContent = "Add Safe Place";
        safetyScoreInputElement.style.display = 'none';
        editPolygonCoords = [];
        editSafePlaceCoords = [];
    }
});




L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);
showMyMarker();
changeMapView(myCoordinates);
getHeatmapData();