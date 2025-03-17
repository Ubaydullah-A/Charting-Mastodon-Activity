'''
This program collects the appropriate activity data from a Mastodon instance.
It is intended to run uninterrupted on a device connected to the internet.

To run this, use: python3 back-end.py
'''

try:
    from requests import get, exceptions
    from pickle import load, dump
    from datetime import datetime, timedelta, UTC
    from time import sleep
    from urllib.parse import urlparse
    from os import mkdir, path
except Exception:
    raise SystemExit('Please install the required Python packages.\nMore '
                     + 'information can be found at: https://github.com/'
                     + 'Ubaydullah-A/Charting-Mastodon-Activity')

# Ask the user for the URL of an instance.
instance = input('Please enter the URL of the instance you would like to ' +
                 'monitor (such as https://mastodon.social/): ')

# Test that the program can collect new data via the API.
requested_data = ''
try:
    requested_data = get(instance + 'api/v1/instance/activity').json()
except exceptions.RequestException:
    raise SystemExit('Unable to connect to the instance.\nPlease ensure ' +
                     'that the URL is correct (including ending with \'/\'),' +
                     ' that the instance is **NOT** in whitelist mode, and ' +
                     'that you are connected to the internet.')

# Get the previously collected data.
file_name = urlparse(instance)
if not path.exists('./data_files/'):
    mkdir('data_files')
data = []
try:
    data_file = open('./data_files/' + file_name.netloc, 'rb')
    data = load(data_file)
    data_file.close()
except Exception:
    pass

# Calculate when to start collecting new data and wait until that time.
next_collection = datetime.now().astimezone(UTC)
today = next_collection.replace(hour=10, minute=0, second=0, microsecond=0)
if next_collection < today:
    next_collection = today
else:
    tomorrow = next_collection + timedelta(days=1)
    next_collection = tomorrow.replace(hour=10, minute=0, second=0,
                                       microsecond=0)
print('First data collection:', str(next_collection))
sleep(datetime.timestamp(next_collection) - datetime.timestamp(datetime.now()))

# Collect the new data and store it with the previously collected data.
attempts = 0
while True:
    failed_to_collect = False
    # Collect new data via the API.
    requested_data = ''
    print('Attempting to collect activity data.\nPlease do **NOT** terminate '
          + 'the program during this process.')
    try:
        requested_data = get(instance + 'api/v1/instance/activity').json()
    except exceptions.RequestException:
        print('Unable to collect activity data:', datetime.now())
        failed_to_collect = True

    if not failed_to_collect:
        # Format the data to avoid duplicate days.
        exists = False
        for requested_data_entry in range(1, len(requested_data)):
            requested_data[requested_data_entry]['week'] = \
                datetime.fromtimestamp(int(requested_data[requested_data_entry]
                                           ['week'])).strftime('%d/%m/%Y')
            temp = requested_data[requested_data_entry]['week'].split('/')
            requested_data[requested_data_entry]['week'] = \
                int(datetime.timestamp(datetime(int(temp[2]), int(temp[1]),
                    int(temp[0]))))
            for data_entry in range(0, len(data)):
                if requested_data[requested_data_entry]['week'] == \
                        data[data_entry]['week']:
                    exists = True
                    break
            if not exists:
                # Add a 'count' key = 1
                requested_data[requested_data_entry]['count'] = '1'
                data.append(requested_data[requested_data_entry])
            else:
                # Sum the old and new 'statuses', 'logins', and
                # 'registrations', and increment 'count'.
                # This is used to handle data inconsistencies between requests.
                data[data_entry]['statuses'] = \
                    str(int(data[data_entry]['statuses']) +
                        int(requested_data[requested_data_entry]['statuses']))
                data[data_entry]['logins'] = \
                    str(int(data[data_entry]['logins']) +
                        int(requested_data[requested_data_entry]['logins']))
                data[data_entry]['registrations'] = \
                    str(int(data[data_entry]['registrations']) +
                        int(requested_data[requested_data_entry][
                                           'registrations']))
                data[data_entry]['count'] = str(int(data[data_entry]['count']
                                                    ) + 1)
                continue

        # Store the new data.
        try:
            write_data = open('./data_files/' + file_name.netloc, 'wb')
            dump(data, write_data)
            write_data.close()
            print('Successfully collected activity data:', datetime.now())
        except Exception:
            print('Failed to save the collected activity data:',
                  datetime.now())
            failed_to_collect = True

    # Reattempt data collection if it was not successfully collected.
    if failed_to_collect and attempts < 3:
        attempts += 1
        print('Attempt', attempts, 'failed.')
        match attempts:
            case 1:
                # Reattempt data collection 1 hour after the original attempt.
                attempt_1 = next_collection.replace(hour=11)
                print('Retrying data collection in approximately 1 hour.')
                sleep(datetime.timestamp(attempt_1)
                      - datetime.timestamp(datetime.now()))
            case 2:
                # Reattempt data collection 6 hours after the original attempt.
                attempt_2 = next_collection.replace(hour=16)
                print('Retrying data collection in approximately 5 hours.')
                sleep(datetime.timestamp(attempt_2)
                      - datetime.timestamp(datetime.now()))
            case 3:
                # Reattempt data collection 12 hours after the original
                # attempt.
                attempt_3 = next_collection.replace(hour=22)
                print('Retrying data collection in approximately 6 hours.')
                sleep(datetime.timestamp(attempt_3)
                      - datetime.timestamp(datetime.now()))
        continue
    elif failed_to_collect:
        print('Attempt', attempts, 'failed.')
        print('No data collected today.')

    # Ensure that the program only successfully requests data a maximum of once
    # every 24 hours.
    next_collection = next_collection + timedelta(days=1)
    print('Next data collection:', str(next_collection))
    print('')
    attempts = 0
    sleep(datetime.timestamp(next_collection)
          - datetime.timestamp(datetime.now()))
