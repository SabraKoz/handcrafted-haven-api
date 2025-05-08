#!/bin/bash

rm db.sqlite3
rm -rf ./handcraftedprojectapi/migrations
python3 manage.py migrate
python3 manage.py makemigrations handcraftedprojectapi
python3 manage.py migrate handcraftedprojectapi
python3 manage.py loaddata users
python3 manage.py loaddata tokens
python3 manage.py loaddata productcategory
python3 manage.py loaddata stores
python3 manage.py loaddata product
python3 manage.py loaddata productreview
python3 manage.py loaddata productfavorite
python3 manage.py loaddata payment
python3 manage.py loaddata order
python3 manage.py loaddata orderproduct
