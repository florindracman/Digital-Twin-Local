FROM python:3.11-slim
WORKDIR /mqtt_app
COPY producer_trigger.py ./
RUN pip install paho-mqtt psycopg2-binary
CMD ["python", "-u", "producer_trigger.py"]
