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
print(data)
print("")

# Ask user for instance
instance = input("Please enter the URL of the instance you would like to monitor (such as https://mastodon.social/): ")

while True:

    # Get new data via the API
    r = ""
    try:
        r = get(instance + 'api/v1/instance/activity').json()
    except:
        print("The URL is incorrect.\nPlease ensure that the URL is correct (including ending with '/') and that the instance is **NOT** in whitelist mode.")
        exit(1)
    print(r)
    print("")
    #print(len(r))

    # Format data to avoid duplicate days
    exists = False
    for x in range(1, len(r)):
        #print(r[x])
        r[x]['week'] = datetime.fromtimestamp(int(r[x]['week'])).strftime("%Y/%m/%d")
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
    print(data)

    # Store new data
    write_data = open('data', 'wb')
    dump(data, write_data)
    write_data.close()

    # Ensures that the program only requests data once every 24 hours
    print(datetime.now())
    sleep(86400)