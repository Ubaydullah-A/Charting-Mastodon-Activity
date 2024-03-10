"""
This program collects the appropriate activity data from a Mastodon instance.
It is intended to run uninterrupted on a device connected to the internet.

To run this, use: python3 back-end.py
"""

from requests import get
from pickle import load, dump
from datetime import datetime
from sys import exit
from time import sleep

# Get the previously collected data
file_check = open("data", "a")
file_check.close()
data_file = open("data", "rb")
data = []
try:
    data = load(data_file)
except:
    pass
data_file.close()

# Ask user for instance
instance = input("Please enter the URL of the instance you would like to monitor (such as https://mastodon.social/): ")

# Get new data via the API
requested_data = ""
try:
    requested_data = get(instance + 'api/v1/instance/activity').json()
except:
    print("Unable to connect to the instance.\nPlease ensure that the URL is correct (including ending with '/'), that the instance is **NOT** in whitelist mode, and that you are connected to the internet.")
    exit(1)

unix_timestamp = datetime.timestamp(datetime.now())

while True:
    failed_to_collect = False
    # Get new data via the API
    requested_data = ""
    print("Attempting to collect activity data.\nPlease do NOT terminate during this process.")
    try:
        requested_data = get(instance + 'api/v1/instance/activity').json()
    except:
        print("Unable to collect activity data:", datetime.now())
        failed_to_collect = True

    if not failed_to_collect:
        # Format data to avoid duplicate days
        exists = False
        for requested_data_entry in range(1, len(requested_data)):
            requested_data[requested_data_entry]['week'] = datetime.fromtimestamp(int(requested_data[requested_data_entry]['week'])).strftime("%d/%m/%Y")
            temp = requested_data[requested_data_entry]['week'].split("/")
            requested_data[requested_data_entry]['week'] = int(datetime.timestamp(datetime(int(temp[2]), int(temp[1]), int(temp[0]))))
            for data_entry in range(0, len(data)):
                if requested_data[requested_data_entry]['week'] == data[data_entry]['week']:
                    exists = True
                    break
            if not exists:
                # Add a "count" key == 1
                requested_data[requested_data_entry]['count'] = '1'
                data.append(requested_data[requested_data_entry])
            else:
                # Sum old and new "statuses", "logins" and "registrations", and increment "count"
                # This is used to handle data inconsistencies between requests
                data[data_entry]['statuses'] = str(int(data[data_entry]['statuses']) + int(requested_data[requested_data_entry]['statuses']))
                data[data_entry]['logins'] = str(int(data[data_entry]['logins']) + int(requested_data[requested_data_entry]['logins']))
                data[data_entry]['registrations'] = str(int(data[data_entry]['registrations']) + int(requested_data[requested_data_entry]['registrations']))
                data[data_entry]['count'] = str(int(data[data_entry]['count']) + 1)
                continue

        # Store new data
        try:
            write_data = open('data', 'wb')
            dump(data, write_data)
            write_data.close()
            print("Successfully collected activity data:", datetime.now())
        except:
            print("Failed to save the collected activity data:", datetime.now())

    # Ensures that the program only requests data once every 24 hours
    unix_timestamp += (24 * 60 * 60)
    sleep(unix_timestamp - datetime.timestamp(datetime.now()))