FROM python:3.11-slim
WORKDIR /mqtt_app

# Install Postgres client for pg_isready
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy required files from parent directory
COPY plugin_manager.py listener_base.py listeners.json ./
COPY plugins/ ./plugins/

COPY vehicle_digital_twin.py db.py wait-for-db.sh ./
RUN pip install paho-mqtt psycopg2-binary

# Use wait-for-db.sh to start consumer
CMD ["./wait-for-db.sh", "db", "python", "-u", "vehicle_digital_twin.py"]
