import json
import time
import random
import paho.mqtt.client as mqtt

BROKER = "mqtt-broker"
TOPIC = "vehicles/request"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.loop_start()

while True:
    message = {
        "trigger": "VIN_REQUEST",
    }

    client.publish(TOPIC, json.dumps(message))
    print(f"{json.dumps(message)}")
    
    time.sleep(5)