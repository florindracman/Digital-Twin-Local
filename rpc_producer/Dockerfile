FROM python:3.11-slim
WORKDIR /mqtt_app
COPY rpc_producer.py ./
RUN pip install paho-mqtt psycopg2-binary
CMD ["python", "-u", "rpc_producer.py"]
