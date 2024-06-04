const form = document.querySelector('form');
const originInput = document.querySelector('#origin');
const destinationInput = document.querySelector('#destination');
const submitButton = document.querySelector('#submit');
const mapDiv = document.querySelector('#map');

submitButton.addEventListener('click', async (e) => {
    e.preventDefault();
    const origin = originInput.value;
    const destination = destinationInput.value;


    try {
        // Construct the URL with query parameters
        const url = new URL('/route', window.location.origin);
        url.searchParams.append('origin', origin);
        url.searchParams.append('destination', destination);

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const routeData = await response.json();
        // Display the route data on the map or in a list format
        console.log(routeData);
    } catch (error) {
        console.error(error);
    }
});