#!/bin/bash

rm db.sqlite3
rm -rf ./handcraftedprojectapi/migrations
python3 manage.py migrate
python3 manage.py makemigrations handcraftedprojectapi
python3 manage.py migrate handcraftedprojectapi
python3 manage.py loaddata users
python3 manage.py loaddata tokens

