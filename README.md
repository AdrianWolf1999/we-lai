# we-lai

## Setup

1. Create a `.env` file and add `GEO_API_KEY=...`

2. Install requirements:

    pip install -r requirements.txt

3. Start the server with:

    python3 server/main.py

4. The client can be accessed via your browser:

   https://localhost:5000/

5. To call the server function get_safe_map() simply insert in the coordinates for origin, destination and profile.
   This way a GET request should be sent to https://localhost:5000/route?origin={origin}&destination={destination}&profile={profile}
   
   Example:
   ORIGIN = "48.783391,9.180221"
   DESTINATION = "48.779477,9.179306"
   PROFILE = "foot"

6. The return of this request is the route in json format, which is then displayed by the frontend
