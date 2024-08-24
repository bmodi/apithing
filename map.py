#!/usr/bin/env python3

import requests
import argparse

def get_lati_longi(api_key, latlng):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        "latlng": latlng,
        "key": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            return data["results"][0]["formatted_address"]
            location = data["results"][0]["geometry"]["location"]
            return location
            # lat = location["lat"]
            # lng = location["lng"]
            # return lat, lng
        else:
            print(f"Error: {data['error_message']}")
            return 0, 0
    else:
        print("Failed to make the request.")
        return 0, 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get address for a given lat and lon using the Google Maps API.")
    parser.add_argument('api_key', type=str, help='Google Maps API key')
    parser.add_argument('latlng', type=str, help='Address to geocode')

    args = parser.parse_args()

    # lati, longi = get_lati_longi(args.api_key, args.address)
    jsonInfo = get_lati_longi(args.api_key, args.latlng)
    print(jsonInfo)
    # print(f"Latitude: {lati}")
    # print(f"Longitude: {longi}")
