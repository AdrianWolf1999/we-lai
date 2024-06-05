# we-lai

## Setup

1. Create a `.env` file and add `API_KEY=...`

2. Install requirements:

    pip install -r requirements.txt

3. Start the server with:

    python3 server/main.py

4. The client can be accessed via your browser:

   https://localhost:5000/

5. To call the server function get_safe_map() simply insert in the coordinates for origin and destination.
   This way a GET request should be sent to https://localhost:5000/route?origin={origin}&destination={destination}
   
   Example:
   ORIGIN = "48.783391,9.180221"
   DESTINATION = "48.779477,9.179306"

6. The return of this request is map_values (json format), which can be found in the browsers javascript console (type F12 and go to "Console")

7. TODO: Visualise these map_values on the frontend most likely.
