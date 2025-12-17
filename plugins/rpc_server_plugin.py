import json
import threading
import logging
import paho.mqtt.client as mqtt
from listener_base import MqttListenerPlugin

class RpcServerPlugin(MqttListenerPlugin):
    def validate(self):
        if "request_topic" not in self.config:
            raise ValueError("request_topic is required")
        if "response_topic_prefix" not in self.config:
            raise ValueError("response_topic_prefix is required")
        if self.context.get("read_all_vehicle_data") is None:
            logging.warning("read_all_vehicle_data not available; RPC will return error")

    def start(self):
        broker = self.context["broker"]
        req_topic = self.config["request_topic"]
        resp_prefix = self.config["response_topic_prefix"]
        read_all_vehicle_data = self.context.get("read_all_vehicle_data")

        def on_message(client, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode())
            except Exception as e:
                logging.exception("[%s] bad RPC payload: %s", self.name, e)
                return
            corr = payload.get("correlation_id")
            params = payload.get("params", {}) or {}
            if not corr:
                logging.error("[%s] missing correlation_id", self.name)
                return

            if read_all_vehicle_data is None:
                response = {"correlation_id": corr, "error": "DB read function not available"}
            else:
                try:
                    rows = read_all_vehicle_data(**params) if params else read_all_vehicle_data()
                    result = [{"vin": r[0], "latitude": r[1], "longitude": r[2], "giro": r[3]} for r in rows]
                    response = {"correlation_id": corr, "result": result}
                except Exception as e:
                    response = {"correlation_id": corr, "error": str(e)}

            client.publish(f"{resp_prefix}{corr}", json.dumps(response))

        def run():
            c = mqtt.Client()
            c.on_message = on_message
            c.connect(broker, 1883, 60)
            c.subscribe(req_topic)
            logging.info("[%s] RPC server listening on %s", self.name, req_topic)
            c.loop_forever()
        logging.info(f"Starting thread {self.name}-rpc")
        threading.Thread(target=run, name=f"{self.name}-rpc", daemon=True).start()