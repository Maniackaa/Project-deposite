#!/bin/sh
gunicorn --bind 0.0.0.0:$GUNICORN_PORT backend_deposit.wsgi
