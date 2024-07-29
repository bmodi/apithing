import requests
import argparse

def get_lati_longi(api_key, address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        "address": address,
        "key": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            lat = location["lat"]
            lng = location["lng"]
            return lat, lng
        else:
            print(f"Error: {data['error_message']}")
            return 0, 0
    else:
        print("Failed to make the request.")
        return 0, 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get latitude and longitude for a given address using the Google Maps API.")
    parser.add_argument('api_key', type=str, help='Google Maps API key')
    parser.add_argument('address', type=str, help='Address to geocode')

    args = parser.parse_args()

    lati, longi = get_lati_longi(args.api_key, args.address)
    print(f"Latitude: {lati}")
    print(f"Longitude: {longi}")
