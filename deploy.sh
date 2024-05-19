#!/bin/bash

# Exit on first error
set -e

# Ensure script is executable
chmod +x deploy.sh

# Install dependencies
python -m pip install -r requirements.txt

# Start the application
gunicorn marmut.wsgi --log-file -
