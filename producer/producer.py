import json
import time
import random
import paho.mqtt.client as mqtt

BROKER = "mqtt-broker"
TOPIC = "vehicles/vin"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.loop_start()

while True:
    message = {
        "vin": f"VIN{123456}",
    }

    client.publish(TOPIC, json.dumps(message))
    print(f"{json.dumps(message)}")
    
    time.sleep(5)