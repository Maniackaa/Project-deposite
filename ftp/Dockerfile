FROM python:3.10
WORKDIR /app
RUN apt-get update && apt-get install android-sdk-platform-tools android-tools-adb usbutils -y
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install setuptools && pip install adbutils robotframework
COPY . .
#RUN adb start-server
#CMD ["python3", "ftp_grabber.py"]
