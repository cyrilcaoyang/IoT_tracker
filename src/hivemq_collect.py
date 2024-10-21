# Imports
# This code is not done yet
# TODO

import json
import paho.mqtt.client as paho

from settings.HiveMQ_secrets import (
    HIVEMQ_HOST,
    HIVEMQ_PASSWORD,
    HIVEMQ_USERNAME
)

# Define your HiveMQ details
broker = HIVEMQ_HOST
port = 8883  # Standard port for secure MQTT communication
topic = "Sensors"
client_id = "DataReader"
username = HIVEMQ_USERNAME
password = HIVEMQ_PASSWORD


# Define the callback for when a message is received
def on_message(client, userdata, message):
    print(f"Received message from topic '{message.topic}': {message.payload.decode()}")
    try:
        # Decode the payload from bytes to string
        payload_str = message.payload.decode('utf-8')
        print("Decoded payload:", payload_str)

        # Parse the payload if it's in JSON format
        message_json = json.loads(payload_str)
        print("Message content:", json.dumps(message_json, indent=4))  # Pretty print the JSON message

        # Write the message to a file
        with open('received_messages.json', 'a') as f:
            json.dump(message_json, f)
            f.write('\n')
    except json.JSONDecodeError as e:
        print("Failed to decode JSON message:", e)


# Create an MQTT client instance
client = paho.Client(paho.CallbackAPIVersion.VERSION1)

# Set username and password
client.username_pw_set(username, password)

# Enable TLS for secure connection
client.tls_set()

# Assign the on_message callback function
client.on_message = on_message

# Connect to the broker
print(f"Connecting to broker {broker}...")
client.connect(HIVEMQ_HOST, 1883)


# Subscribe to the topic
print(f"Subscribing to topic '{topic}'...")
client.subscribe(topic)

# Start the loop to process received messages
print("Waiting for messages. Press Ctrl+C to exit.")
client.loop_forever()