# Charting Mastodon Activity

## Installing the required software
- Download the files from the repository.
- Ensure Python is installed. Python 3.12.7 was used to create the programs.
- Install the required Python packages:
    - Using PIP:
        - Install PIP by following these instructions: https://packaging.python.org/en/latest/guides/installing-using-linux-tools/
        - Install the required packages using: `pip3 install -r requirements.txt`.

    - Using APT (Debian and Debian-based Linux distributions):
        - Install the required packages using: `sudo apt install python3-matplotlib python3-numpy python3-pandas python3-requests tkcalendar python3-pathvalidate`.

## Running the programs

### Back-end
The back-end collects the appropriate activity data from a Mastodon instance. It is intended to run uninterrupted on a device connected to the internet.

To run this, use: python3 back-end.py

### Front-end
The front-end takes the activity data collected by the back-end and displays it on a graph.

To run this, use: python3 front-end.py

### Data-conversion
The data-conversion tool converts data collected before v1.3.0 to the new naming scheme, and stores it in the correct directory. If data has already been collected using v1.3.0 or later, this tool will merge the data files.

To run this, use: python3 data-conversion.py
