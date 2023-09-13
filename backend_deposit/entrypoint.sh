#!/bin/sh
sleep 1
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput
python3 manage.py collectstatic  --noinput
gunicorn --bind 0.0.0.0:$GUNICORN_PORT backend_deposit.wsgi
