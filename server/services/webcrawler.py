# TODO: Crawl 3 different routes at a time (for now there is only one)

import os
from pathlib import Path
import requests
from dotenv import load_dotenv


class WebCrawler:
    '''
    Provides a method to crawl from Google API and return the requested route as json.
    '''

    def __init__(self):
        pass

    def load_api_key(self):
        '''
        Loads the API key from 'api_key.env' file in the current directory.

        RETURNS
        ----------
        api_key : str or None
            The API key value if found, otherwise `None`.
        '''
        load_dotenv()
        # Try to load environment variables from .env file in the current directory
        env_file_cwd = Path.cwd() / '.env'
        if env_file_cwd.exists():
            # Load environment variables from .env file
            load_dotenv(env_file_cwd)

        # Access the API key
        api_key = os.getenv("API_KEY")
        if api_key is None:
            print(
                "Error: No API key found. Please create a .env file like stated in README")
        return api_key

    def get_route(self, origin, destination, api_key):
        '''
        Crawls the Route through Google's API and returns the route data as json.

        PARAMETERS
        ----------
        origin : str
            The starting location of the route (e.g., "New York, NY")
        destination : str
            The ending location of the route (e.g., "Los Angeles, CA")
        api_key : str
            The API key for accessing the Google Maps API

        RETURNS
        -------
        data : str
            The route data as a JSON dictionary, or an error message if an exception occurs
        '''
        try:
            # Construct the API endpoint URL
            base_url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                "origin": origin,
                "destination": destination,
                "key": api_key
            }

            # Send the API request
            response = requests.get(base_url, params=params, timeout=10)

            # Raise an HTTPError if the HTTP request returned an unsuccessful status code
            response.raise_for_status()

            data = response.json()
            return data

        except requests.exceptions.RequestException as e:
            return f"Error: {e}"

class WebCrawlerHERE():
    
    def __init__(self):
        self.api_key = self.load_api_key()

    def load_api_key(self):
        # Try to load environment variables from .env file in the current directory
        env_file_cwd = Path.cwd() / '.env'
        if env_file_cwd.exists():
            # Load environment variables from .env file
            load_dotenv(env_file_cwd)        
        
        # Load the HERE API key from a file or environment variable
        api_key = os.getenv("HERE_API_KEY")
        if api_key is None:
            print("Error: No HERE API key found")
            return None
        return api_key
    
    def get_route(self, origin, destination):
        # Construct the HERE API request
        api_endpoint = "https://route.ls.hereapi.com/routing/7.2/calculateRoute.json"
        params = {
            "apiKey": self.api_key,
            "waypoint0": origin,
            "waypoint1": destination,
            "mode": "fastest;car;traffic:enabled",
            "representation": "display"
        }

        # Send the API request
        response = requests.get(api_endpoint, params=params)

        # Parse the HERE API response
        if response.status_code == 200:
            data = response.json()
            route = data["response"]["route"][0]
            return route
        else:
            print("Error: Failed to retrieve route data")
            return None

# just for testing:
if __name__ == "__main__":
    crawler = WebCrawlerHERE()
    result = crawler.get_route(
        "48.783391,9.180221", "48.779477,9.179306")
    print(result)
