# Charting Mastodon Activity

## Installing the required software
1. Download the files from the repository.
2. Ensure Python is installed. Python 3.12.7 was used to create the programs.
3. Install the required Python packages:
    - Using PIP:
        1. Install PIP by following these instructions: https://packaging.python.org/en/latest/guides/installing-using-linux-tools/
        2. Install the required packages using: **pip3 install -r requirements.txt**.
    - Using APT (Debian and Debian-based Linux distributions):
        1. Install the required packages using: **sudo apt install python3-matplotlib python3-numpy python3-pandas python3-requests tkcalendar**.

## Running the programs

### Back-end
The back-end collects the appropriate activity data from a Mastodon instance. It is intended to run uninterrupted on a device connected to the internet.

To run this, use: python3 back-end.py

### Front-end
The front-end takes the activity data collected by the back-end and displays it in a graph.

To run this, use: python3 front-end.py
