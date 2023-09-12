FROM python:3.10
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install gunicorn==20.1.0
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
#RUN python3 manage.py makemigrations
#RUN python3 manage.py migrate
RUN ["chmod", "+x", "/app/entrypoint.sh"]
ENTRYPOINT ["/app/entrypoint.sh"]
