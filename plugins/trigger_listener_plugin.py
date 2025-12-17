import json
import threading
import logging
import paho.mqtt.client as mqtt
from listener_base import MqttListenerPlugin

class TriggerListenerPlugin(MqttListenerPlugin):
    def validate(self):
        for k in ("trigger_topic", "data_topic"):
            if k not in self.config:
                raise ValueError(f"{k} is required")
        if self.context.get("read_all_vehicle_data") is None:
            logging.warning("read_all_vehicle_data not available; trigger will be no-op")

    def start(self):
        broker = self.context["broker"]
        trigger_topic = self.config["trigger_topic"]
        data_topic = self.config["data_topic"]
        read_all_vehicle_data = self.context.get("read_all_vehicle_data")

        def on_message(client, userdata, msg):
            payload_raw = None
            try:
                payload_raw = msg.payload.decode()
                payload = json.loads(payload_raw) if payload_raw else {}
            except Exception:
                payload = {}
            vin_filter = payload.get("vin")

            if read_all_vehicle_data is None:
                logging.error("[%s] No DB read available", self.name)
                return

            try:
                rows = read_all_vehicle_data(vin_filter) if vin_filter else read_all_vehicle_data()
            except Exception as e:
                logging.exception("[%s] DB read failed: %s", self.name, e)
                return

            for r in rows:
                msg_out = {"vin": r[0], "latitude": r[1], "longitude": r[2], "giro": r[3]}
                client.publish(data_topic, json.dumps(msg_out))
            logging.info("[%s] Published %d records to %s", self.name, len(rows), data_topic)

        def run():
            c = mqtt.Client()
            c.on_message = on_message
            c.connect(broker, 1883, 60)
            c.subscribe(trigger_topic)
            logging.info("[%s] Trigger listener on %s", self.name, trigger_topic)
            c.loop_forever()

        threading.Thread(target=run, name=f"{self.name}-trigger", daemon=True).start()