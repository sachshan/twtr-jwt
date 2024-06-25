import googlemaps
import json, os, time
import dotenv

dotenv.load_dotenv()

def get_places(location, radius, place_type):
    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_API_KEY'))
    places_data = []
    response = gmaps.places_nearby(location={'lat':location[0], 'lng':location[1]}, radius=radius, type=place_type)
    places_data.extend(response['results'])

    locations = []
    for place in places_data:
        name = place.get('name')
        lat = place['geometry']['location']['lat']
        lng = place['geometry']['location']['lng']
        locations.append({"user_name": name, "location":[lat, lng]})

    return locations

    
# print(get_places([42.34580914708963, -71.07590585947037], 15000, 'restaurant'))