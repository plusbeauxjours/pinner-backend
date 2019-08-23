import requests
import json
from django.conf import settings


def reverse_place(placeId):
    url = ('https://maps.googleapis.com/maps/api/geocode/json?&language=en&place_id={}&key={}'
           .format(placeId, settings.GOOGLE_MAPS_KEY))
    try:
        response = requests.get(url)
        resp_json_payload = response.json()
        lat = resp_json_payload['results'][0]['geometry']['location']['lat']
        lng = resp_json_payload['results'][0]['geometry']['location']['lng']
        for component in resp_json_payload['results'][0]['address_components']:
            if component['types'][0] == 'country':
                country_code = component['short_name']
                # return country_code
        for components in resp_json_payload['results']:
            for component in components['address_components']:

                if component['types'][0] == 'locality' or component['types'][0] == 'sublocality' or component['types'][0] == 'colloquial_area':
                    city_name = component['long_name']
                    # return city_name
        return lat, lng, city_name,  country_code
    except:
        lat = 0
        lng = 0
        city_name = ""
        country_code = ""
    return lat, lng, city_name,  country_code
