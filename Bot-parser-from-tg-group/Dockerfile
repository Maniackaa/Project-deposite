FROM python:3.10
WORKDIR /app
#RUN apk update && \
#    apk add libpq-dev python-dev
RUN apt-get update
RUN apt-get install libpq-dev libgl1 tesseract-ocr -y
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
COPY rus.traineddata /usr/share/tesseract-ocr/5/tessdata/
CMD ["python3", "main.py"]
