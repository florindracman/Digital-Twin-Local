FROM python:3.11-slim
WORKDIR /mqtt_app

# Install Postgres client for pg_isready
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY fleet_digital_twin.py db.py wait-for-db.sh ./
RUN pip install paho-mqtt psycopg2-binary

# Use wait-for-db.sh to start consumer
CMD ["./wait-for-db.sh", "db", "python", "-u", "fleet_digital_twin.py"]
