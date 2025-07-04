#!/bin/bash

set -e

echo "Starting messaging app setup..."
python3 manage.py makemigrations
python3 manage.py migrate
echo "Migrations applied successfully."

echo "starting messaging app..."
exec python3 manage.py runserver -p 8000
echo "Messaging app is running on port 8000."
echo "Messaging app setup completed successfully."
trap 'echo "An error occurred. Exiting..."; exit 1' ERR

