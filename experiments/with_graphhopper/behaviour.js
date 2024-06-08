const apiKey = 'be7af08d-d658-48b9-9c98-a42e12bedad8';

const map = L.map('mapContainer').setView([52.5, 13.4], 14);

// L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
//     attribution: '© OpenStreetMap contributors'
// }).addTo(map);

//Use a simple tile layer
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);



const badPolygonCoords = [
    [
        [9.175747952191298, 48.77885842296115],
        [9.171542141928168, 48.77518205059932],
        [9.167851405445795, 48.77812316095479],
        [9.175747952191298, 48.77885842296115]
    ]
]
const mediumPolygonCoords = [
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
const safePlaceCoords = [
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
];

	

let badPolygons = [];
let mediumPolygons = [];
let safePlaces = [];

// Function to flip the coordinates
function flipCoordinates(coords) {
    return coords.map(polygon => polygon.map(([a, b]) => [b, a]));
}

function createHeatmap() {
    // Flip the coordinates for polygons and safe places
    const flippedBadPolygonCoords = flipCoordinates(badPolygonCoords);
    const flippedMediumPolygonCoords = flipCoordinates(mediumPolygonCoords);
    const flippedSafePlaceCoords = safePlaceCoords.map(([a, b]) => [b, a]);

    for (let i in flippedBadPolygonCoords) {
        badPolygons.push(L.polygon(flippedBadPolygonCoords[i], { color: 'red', fillOpacity: 0.3, weight: 0 }).addTo(map));
    }

    for (let i in flippedMediumPolygonCoords) {
        mediumPolygons.push(L.polygon(flippedMediumPolygonCoords[i], { color: 'orange', fillOpacity: 0.3 , weight: 0}).addTo(map));
    }

    for (let i in flippedSafePlaceCoords) {
        safePlaces.push(L.circle(flippedSafePlaceCoords[i], {color: 'green', fillColor: 'green', fillOpacity: 0.5, weight: 0, radius: 40}).addTo(map));
    }
}

let metaShown = true;

function toggleHeatmap() {
	metaShown = !metaShown;

	if (metaShown) {
		for (let i in badPolygons) {
			badPolygons[i].addTo(map);
		}
		for (let i in mediumPolygons) {
			mediumPolygons[i].addTo(map);
		}
		for (let i in safePlaces) {
			safePlaces[i].addTo(map);
		}
	} else {
		for (let i in badPolygons) {
			map.removeLayer(badPolygons[i]);
		}
		for (let i in mediumPolygons) {
			map.removeLayer(mediumPolygons[i]);
		}
		for (let i in safePlaces) {
			map.removeLayer(safePlaces[i]);
		}
	}
}


let targetMarker = null;
const myCoordinates = L.latLng(48.776111, 9.174778);
let myMarker = null;
let routes = [];
const profile = 'foot';

document.getElementById('searchInput').addEventListener('input', () => {
    const query = document.getElementById('searchInput').value;
    if (query.length >= 3) {
        getSuggestions(query);
    } else {
        document.getElementById('suggestions').style.display = 'none';
    }
});

function getSuggestions(query) {
    fetch(`https://graphhopper.com/api/1/geocode?q=${query}&key=${apiKey}`)
        .then(response => response.json())
        .then(data => {
            const suggestions = document.getElementById('suggestions');
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

    document.getElementById('searchInput').value = label;
    document.getElementById('suggestions').style.display = 'none';

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

// Function to change the view position of the map
function changeMapView(coordinates) {
    map.setView(coordinates, map.getZoom());
}

function displayRoutes(routesData) {
    // Clear previous route if exists
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

document.getElementById('toggleMetaButton').addEventListener('click', () => {
	toggleHeatmap();
});

document.getElementById('bringMeHomeButton').addEventListener('click', async() => {
    if (!targetMarker || !myMarker) { return; }

    const query = new URLSearchParams({
        key: apiKey
      }).toString();
      
    const resp = await fetch(
        `https://graphhopper.com/api/1/route?${query}`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(
			{
                "profile": profile,
                "points": [
                    [myCoordinates.lng, myCoordinates.lat], // Source coordinates
					//...safePlaceCoords,
                    [targetMarker.getLatLng().lng, targetMarker.getLatLng().lat] // Target coordinates
                ],
				"ch.disable": true,
				"points_encoded": false,
				//"algorithm": "alternative_route",
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
            })
        }
    );
    
    const data = await resp.json();
    if (data.paths && data.paths.length > 0) {
        displayRoutes(data.paths);
    } else {
        console.log('No route found');
    }
});

showMyMarker();
changeMapView(myCoordinates);
createHeatmap();