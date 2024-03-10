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
r = ""
try:
    r = get(instance + 'api/v1/instance/activity').json()
except:
    print("Unable to connect to the instance.\nPlease ensure that the URL is correct (including ending with '/'), that the instance is **NOT** in whitelist mode, and that you are connected to the internet.")
    exit(1)

unix_timestamp = datetime.timestamp(datetime.now())

while True:
    failed_to_collect = False
    # Get new data via the API
    r = ""
    print("Attempting to collect activity data.\nPlease do NOT terminate during this process.")
    try:
        r = get(instance + 'api/v1/instance/activity').json()
    except:
        print("Unable to collect activity data:", datetime.now())
        failed_to_collect = True

    if not failed_to_collect:
        # Format data to avoid duplicate days
        exists = False
        for x in range(1, len(r)):
            r[x]['week'] = datetime.fromtimestamp(int(r[x]['week'])).strftime("%d/%m/%Y")
            temp = r[x]['week'].split("/")
            r[x]['week'] = int(datetime.timestamp(datetime(int(temp[2]), int(temp[1]), int(temp[0]))))
            for y in range(0, len(data)):
                if r[x]['week'] == data[y]['week']:
                    exists = True
                    break
            if not exists:
                # Add a "count" key == 1
                r[x]['count'] = '1'
                data.append(r[x])
            else:
                # Sum old and new "statuses", "logins" and "registrations", and increment "count"
                # This is used to handle data inconsistencies between requests
                data[y]['statuses'] = str(int(data[y]['statuses']) + int(r[x]['statuses']))
                data[y]['logins'] = str(int(data[y]['logins']) + int(r[x]['logins']))
                data[y]['registrations'] = str(int(data[y]['registrations']) + int(r[x]['registrations']))
                data[y]['count'] = str(int(data[y]['count']) + 1)
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