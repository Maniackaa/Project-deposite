FROM python:3.10
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install gunicorn==20.1.0
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
COPY rus.traineddata /usr/share/tesseract-ocr/5/tessdata/
COPY rus.traineddata /usr/share/tesseract-ocr/4.00/tessdata/
RUN ["chmod", "+x", "/app/entrypoint.sh"]
ENTRYPOINT ["/app/entrypoint.sh"]
