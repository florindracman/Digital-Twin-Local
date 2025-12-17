import json
import uuid
import time
import paho.mqtt.client as mqtt

BROKER = "mqtt-broker"
RPC_REQUEST_TOPIC = "rpc/request/read_all_vehicle_data"
RPC_RESPONSE_TOPIC_PREFIX = "rpc/response/"

# Store responses by correlation_id
responses = {}

def on_response(client, userdata, msg):
    """Handle RPC responses."""
    try:
        payload = json.loads(msg.payload.decode())
        correlation_id = payload.get("correlation_id")
        responses[correlation_id] = payload
        print(f"RPC Response (correlation_id={correlation_id}): {payload}")
    except Exception as e:
        print(f"Error parsing response: {e}")

def call_rpc(correlation_id, timeout=5):
    """Call RPC method and wait for response."""
    client = mqtt.Client()
    client.on_message = on_response
    client.connect(BROKER, 1883, 60)
    
    # Subscribe to response topic for this correlation_id
    response_topic = f"{RPC_RESPONSE_TOPIC_PREFIX}{correlation_id}"
    client.subscribe(response_topic)
    client.loop_start()
    
    # Send RPC request
    request = {
        "correlation_id": correlation_id,
        "params": {}
    }
    client.publish(RPC_REQUEST_TOPIC, json.dumps(request))
    print(f"RPC Request sent (correlation_id={correlation_id}): {request}")
    
    # Wait for response with timeout
    start = time.time()
    while correlation_id not in responses and (time.time() - start) < timeout:
        time.sleep(0.1)
    
    if correlation_id in responses:
        result = responses[correlation_id]
        client.loop_stop()
        client.disconnect()
        return result
    else:
        print(f"RPC timeout for correlation_id={correlation_id}")
        client.loop_stop()
        client.disconnect()
        return None

# Example usage
while True:
    correlation_id = str(uuid.uuid4())
    result = call_rpc(correlation_id, timeout=10)
    if result:
        print("\nFinal result:")
        print(json.dumps(result, indent=2))
    time.sleep(10)