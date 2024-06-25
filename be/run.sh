#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

pip install --upgrade pip

# Install the required packages
pip install -r requirements.txt

export REDIS_HOST='localhost'
export REDIS_PORT=6379
export GOOGLE_MAPS_API_KEY='AIzaSyC-YxsZvVyRZFTbIGJ5g8q-o8luhek-bDw'

# Run the Flask app
flask --app flaskr run
# gunicorn --threads=3 --bind 0.0.0.0:5000 wsgi:app 