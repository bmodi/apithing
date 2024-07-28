#!/usr/bin/env python3

import argparse
import requests

# Function to get all bookings
def get_all_bookings():
    url = "https://restful-booker.herokuapp.com/booking"
    response = requests.get(url)
    if response.status_code == 200:
        bookings = response.json()
        print("All bookings:")
        for booking in bookings:
            print(booking)
    else:
        print(f"Failed to retrieve bookings. Status code: {response.status_code}")

# Function to get booking details by ID
def get_booking_by_id(booking_id):
    url = f"https://restful-booker.herokuapp.com/booking/{booking_id}"
    response = requests.get(url)
    if response.status_code == 200:
        booking_details = response.json()
        print(f"Details of booking ID {booking_id}:")
        print(booking_details)
    else:
        print(f"Failed to retrieve booking details. Status code: {response.status_code}")

# Main function to parse arguments and execute the appropriate function
def main():
    parser = argparse.ArgumentParser(description="Interact with the booking API")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for the "getall" command
    subparsers.add_parser("getall", help="Get all bookings")

    # Subparser for the "get" command
    get_parser = subparsers.add_parser("get", help="Get booking by ID")
    get_parser.add_argument("id", type=int, help="Booking ID")

    args = parser.parse_args()

    if args.command == "getall":
        get_all_bookings()
    elif args.command == "get":
        get_booking_by_id(args.id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
