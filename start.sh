#!/bin/sh
/wait-for-it.sh db:5432 -- python manage.py makemigrations api && python manage.py migrate api && python manage.py runserver 0.0.0.0:8000
