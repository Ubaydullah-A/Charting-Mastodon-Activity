# Charting Mastodon Activity

## Installing the required software
- Download the files from the repository.
- Ensure Python is installed. Python 3.10.12 was used to create the programs.
- Install the required packages using: pip3 install -r requirements.txt

## Running the programs

### Back-end
The back-end collects the appropriate activity data from a Mastodon instance. It is intended to run uninterrupted on a device connected to the internet.

To run this, use: python3 back-end.py

### Front-end
The front-end takes the activity data collected by the back-end and displays it in a graph.

To run this, use: python3 front-end.py
