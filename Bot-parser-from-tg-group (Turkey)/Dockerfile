FROM python:3.10
WORKDIR /app
RUN apt-get update && apt-get install libpq-dev libgl1 tesseract-ocr -y
COPY requirements.txt .
#RUN pip install -r requirements.txt --no-cache-dir
RUN pip install -r requirements.txt
COPY . .
COPY rus.traineddata /usr/share/tesseract-ocr/5/tessdata/
COPY rus.traineddata /usr/share/tesseract-ocr/4.00/tessdata/
CMD ["python3", "main.py"]
