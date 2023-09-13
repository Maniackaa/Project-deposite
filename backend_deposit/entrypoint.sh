#!/bin/sh
sleep 1
python manage.py migrate
python manage.py collectstatic  --noinput
gunicorn --bind 0.0.0.0:$GUNICORN_PORT backend_deposit.wsgi
