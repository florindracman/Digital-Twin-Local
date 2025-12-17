import json
import time
import threading
import logging
from typing import Optional
import paho.mqtt.client as mqtt
from db import init_db, write_vehicle_data

try:
    from db import read_all_vehicle_data
except Exception:
    read_all_vehicle_data = None
    logging.warning("db.read_all_vehicle_data not available; trigger will be a no-op")

BROKER = "mqtt-broker"
DATA_TOPIC = "vehicles/data"

init_db()

# How long partial records can live before being cleaned (optional)
EXPIRATION_SECONDS = 30

logging.basicConfig(
    level=logging.INFO,
    format="[%(threadName)s] %(levelname)s: %(message)s",
    force=True   # important when threading is used
)

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    logging.info(f"Received on {msg.topic}: {payload}")

    if msg.topic == DATA_TOPIC:
        logging.info(f"Processing data message: {payload}")
        vin = payload.get("vin")
        latitude = payload.get("latitude")
        longitude = payload.get("longitude")
        giro = payload.get("giro")
        # to do validation of data - select only unique entries in order to avoid duplicates
        write_vehicle_data(vin, latitude, longitude, giro)

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883, 60)
# client.subscribe(TOPIC_VIN)
# client.subscribe(TOPIC_GIRO)
# client.subscribe(TOPIC_LOCATION)
client.subscribe(DATA_TOPIC)
print("fleet_digital_twin running...")

client.loop_forever()
