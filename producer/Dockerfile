FROM python:3.11-slim
WORKDIR /mqtt_app
COPY producer.py db.py ./
RUN pip install paho-mqtt psycopg2-binary
CMD ["python", "-u", "producer.py"]
