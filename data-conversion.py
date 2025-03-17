'''
The data-conversion tool converts data collected before v1.3.0 to the new
naming scheme, and stores it in the correct directory. If data has already been
collected using v1.3.0 or later, this tool will merge the data files.

To run this, use: python3 data-conversion.py
'''

from pickle import load, dump
from urllib.parse import urlparse
from os import mkdir, path

# Warn the user regarding the dangers of using this program.
print('This tool may break collected data if used incorrectly.')
print('It is recommended to only continue AFTER creating backups.')
start = input('Do you want to continue? If yes, enter \'YES\': ')
if start != 'YES':
    exit()

# Get the data stored in the old format.
try:
    requested_data_file = open('data', 'rb')
    requested_data = load(requested_data_file)
    requested_data_file.close()
except Exception:
    raise SystemExit('Unable to load the old data.')

instance = input('Please enter the URL of the instance this data has been '
                 + 'collected for (such as https://mastodon.social/): ')

# Ensure that the directory 'data_files' exists.
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

for requested_data_entry in range(0, len(requested_data)):
    exists = False
    for data_entry in range(0, len(data)):
        if requested_data[requested_data_entry]['week'] == \
                data[data_entry]['week']:
            exists = True
            break
    if not exists:
        # Add the old data.
        data.append(requested_data[requested_data_entry])
    else:
        # Sum the old and new 'statuses', 'logins', 'registrations', and
        # 'count'.
        data[data_entry]['statuses'] = \
            str(int(data[data_entry]['statuses']) +
                int(requested_data[requested_data_entry]['statuses']))
        data[data_entry]['logins'] = \
            str(int(data[data_entry]['logins']) +
                int(requested_data[requested_data_entry]['logins']))
        data[data_entry]['registrations'] = \
            str(int(data[data_entry]['registrations']) +
                int(requested_data[requested_data_entry]['registrations']))
        data[data_entry]['count'] = \
            str(int(data[data_entry]['count'])
                + int(requested_data[requested_data_entry]['count']))

# Store the data.
try:
    write_data = open('./data_files/' + file_name.netloc, 'wb')
    dump(data, write_data)
    write_data.close()
    print('Successfully updated the activity data.')
except Exception:
    print('Failed to update the activity data.\nPlease try again.')
