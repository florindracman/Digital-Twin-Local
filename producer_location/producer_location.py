import json
import time
import random
import paho.mqtt.client as mqtt

BROKER = "mqtt-broker"
TOPIC = "vehicles/location"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.loop_start()

while True:
    message = {
        "latitude": round(random.uniform(-90, 90), 6),
        "longitude": round(random.uniform(-180, 180), 6)
    }

    client.publish(TOPIC, json.dumps(message))
    print(f"{json.dumps(message)}")
    
    time.sleep(5)