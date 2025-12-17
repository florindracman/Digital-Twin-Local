import json
import time
import threading
import logging
import sys
from pathlib import Path
import paho.mqtt.client as mqtt
from db import init_db, write_vehicle_data
from time import time

# add project root to sys.path for plugin imports
# ROOT = Path(__file__).resolve().parent.parent
# sys.path.insert(0, str(ROOT))

from plugin_manager import load_plugins

try:
    from db import read_all_vehicle_data
except Exception:
    read_all_vehicle_data = None
    logging.warning("db.read_all_vehicle_data not available; trigger will be a no-op")

BROKER = "mqtt-broker"
TOPIC_VIN = "vehicles/vin"
TOPIC_GIRO = "vehicles/giro"
TOPIC_LOCATION = "vehicles/location"

init_db()

# Temporary storage for partial data
buffer = {}

# How long partial records can live before being cleaned (optional)
EXPIRATION_SECONDS = 30

logging.basicConfig(
    level=logging.INFO,
    format="[%(threadName)s] %(levelname)s: %(message)s",
    force=True
)

context = {"broker": BROKER, "read_all_vehicle_data": read_all_vehicle_data}
# Load plugins using absolute path
config_path = Path(__file__).parent / "listeners.json"
plugins = load_plugins(str(config_path), context)

def merge_and_store(vin):
    """If all parts exist for this VIN, merge and write to DB."""
    record = buffer.get(vin)

    if not record:
        return  # nothing to merge
    
    required_fields = ["location", "giro", "vin"]
    
    if all(key in record for key in required_fields):
        # Merge everything
        final = {
            **record["vin"],
            **record["location"],
            **record["giro"]
        }

        print(f"Final merged record for {vin}: {final}")

        # Write to DB
        write_vehicle_data(final["vin"], final["latitude"], final["longitude"], final["giro"])

        # Remove from buffer
        del buffer[vin]

def ensure_buffer(vin):
    if vin not in buffer:
        buffer[vin] = {"vin": None, "location": None, "giro": None}


def try_merge(vin):
    entry = buffer.get(vin)
    if not entry:
        return

    if entry["vin"] and entry["location"] and entry["giro"]:
        merged = {
            **entry["vin"],
            **entry["location"],
            **entry["giro"]
        }
        print("Merged complete record:", merged)

        # Write to DB (adjust fields as needed)
        write_vehicle_data(
            merged["vin"],
            merged["latitude"],
            merged["longitude"],
            merged["giro"]
        )

        # Remove to start fresh
        del buffer[vin]

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    logging.info(f"Received on {msg.topic}: {payload}")

    vin = None
    if msg.topic == TOPIC_VIN:
        vin = payload["vin"]
        ensure_buffer(vin)
        buffer[vin]["vin"] = payload

    elif msg.topic == TOPIC_LOCATION:
        if not buffer:
            print("WARNING: location received but no VIN known yet")
            return
        vin = list(buffer.keys())[-1]
        ensure_buffer(vin)
        buffer[vin]["location"] = payload

    elif msg.topic == TOPIC_GIRO:
        if not buffer:
            print("WARNING: status received but no VIN known yet")
            return
        vin = list(buffer.keys())[-1]
        ensure_buffer(vin)
        buffer[vin]["giro"] = payload

    if vin:
        try_merge(vin)

def prepare_data():
    print("Preparing data")

def on_trigger_cleanup():
    """Periodically clean up expired buffer entries."""
    while True:
        cleanup_buffer()
        time.sleep(EXPIRATION_SECONDS)

def cleanup_buffer():
    """Remove expired entries from the buffer."""
    current_time = time()
    to_delete = []
    for vin, record in buffer.items():
        if "timestamp" in record:
            if current_time - record["timestamp"] > EXPIRATION_SECONDS:
                to_delete.append(vin)
    for vin in to_delete:
        print(f"Cleaning up expired record for VIN: {vin}")
        del buffer[vin]

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC_VIN)
client.subscribe(TOPIC_GIRO)
client.subscribe(TOPIC_LOCATION)
# client.subscribe(DATA_TOPIC)
print("Consumer running...")

# def trigger_on_message(client: mqtt.Client, userdata, msg):
#     """Handle trigger requests: read DB and publish data."""
#     try:
#         payload_raw = msg.payload.decode()
#     except Exception:
#         payload_raw = None
#     logging.info("Trigger received on %s: %s", msg.topic, payload_raw)

#     if read_all_vehicle_data is None:
#         logging.error("No DB read function available; cannot fulfill trigger")
#         return

#     # Optional: support a JSON payload with parameters (e.g., specific VIN)
#     vin_filter: Optional[str] = None
#     try:
#         if payload_raw:
#             parsed = json.loads(payload_raw)
#             vin_filter = parsed.get("vin")
#     except Exception:
#         vin_filter = None

#     try:
#         if vin_filter:
#             rows = read_all_vehicle_data(vin_filter)  # expected to support filtering
#         else:
#             rows = read_all_vehicle_data()
#     except Exception as e:
#         logging.exception("Error reading DB for trigger: %s", e)
#         return
#     for row in rows:
#         vin, lat, lon, giro = row
#         message = {
#             "vin": vin,
#             "latitude": lat,
#             "longitude": lon,
#             "giro": giro
#         }

#         logging.info("Read data in response to trigger: %s", message)
#         client.publish(DATA_TOPIC, json.dumps(message))

# def trigger_listener():
#     """Dedicated thread: separate mqtt client listens for trigger requests."""
#     logging.info("Starting trigger listener thread ...")
#     tclient = mqtt.Client()
#     tclient.on_message = trigger_on_message
#     try:
#         tclient.connect(BROKER, 1883, 60)
#     except Exception as e:
#         logging.exception("Trigger client failed to connect: %s", e)
#         return
#     tclient.subscribe(TRIGGER_TOPIC)
#     logging.info("Trigger listener subscribed to %s", TRIGGER_TOPIC)
#     tclient.loop_forever()

# def on_rpc_request(client, userdata, msg):
#     """Handle RPC requests: read DB and respond with data."""
#     try:
#         payload = json.loads(msg.payload.decode())
#     except Exception as e:
#         logging.exception("Failed to parse RPC request: %s", e)
#         return
    
#     correlation_id = payload.get("correlation_id")
#     if not correlation_id:
#         logging.error("RPC request missing correlation_id")
#         return
    
#     logging.info("RPC request received: %s", payload)
    
#     if read_all_vehicle_data is None:
#         response = {"error": "DB read function not available"}
#     else:
#         try:
#             rows = read_all_vehicle_data()
#             response = {
#                 "correlation_id": correlation_id,
#                 "result": [{"vin": row[0], "latitude": row[1], "longitude": row[2], "giro": row[3]} for row in rows]
#             }
#         except Exception as e:
#             response = {"correlation_id": correlation_id, "error": str(e)}
    
#     response_topic = f"{RPC_RESPONSE_TOPIC_PREFIX}{correlation_id}"
#     client.publish(response_topic, json.dumps(response))
#     logging.info("RPC response published to %s", response_topic)

# def rpc_server():
#     """Dedicated thread: RPC server listens for method calls."""
#     logging.info("Starting RPC server thread ...")
#     rpc_client = mqtt.Client()
#     rpc_client.on_message = on_rpc_request
#     try:
#         rpc_client.connect(BROKER, 1883, 60)
#     except Exception as e:
#         logging.exception("RPC client failed to connect: %s", e)
#         return
#     rpc_client.subscribe(RPC_REQUEST_TOPIC)
#     logging.info("RPC server subscribed to %s", RPC_REQUEST_TOPIC)
#     rpc_client.loop_forever()

# start trigger thread (daemon so it won't block shutdown)
# threading.Thread(target=trigger_listener, name="trigger-listener", daemon=True).start()

# start RPC server thread
# threading.Thread(target=rpc_server, name="rpc-server", daemon=True).start()

client.loop_forever()
