#!/bin/bash

# Build the project
echo "Building the project..."
python3.12 -m venv venv
source venv/bin/activate
python3.12 -m pip install -r requirements.txt

echo "Make Migration..."
python3.12 manage.py makemigrations --noinput
python3.12 manage.py migrate --noinput

echo "Collect Static..."
python3.12 manage.py collectstatic --noinput --clear