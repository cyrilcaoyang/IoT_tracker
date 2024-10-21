# Imports
import sys
import json
from pymongo import MongoClient
from awscrt import mqtt
from awsiot import mqtt_connection_builder
from settings.mongodb_settings import CLIENT, DATABASE

# AWS IoT configuration
from settings.aws_iot_settings import (CLIENT_ID, ENDPOINT, TOPIC, PORT,
                                    PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY)

# This sample shows how to create a MQTT connection using a certificate file and key file.
# This sample is intended to be used as a reference for making MQTT connections.

# Access a specific database
client = MongoClient(CLIENT)
db = client[DATABASE]
collection = db['20241021-2']


# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}\n".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}'".format(topic))
    # Convert the message to a JSON string
    msg = payload.decode('utf-8')
    try:
        message = json.loads(msg)
        data = message["state"]["reported"]
        # metadata = message["metadata"]["reported"]
        print(f"DATA loaded: {data}")

        # Keys to find
        keys_to_find = ["State Of Charge (%)", "Humidity", "TemperatureC", "Pressure"]

        for key, value in data.items():
            filtered_entry = {k: v for k, v in value.items() if k in keys_to_find}
            if filtered_entry:
                print(filtered_entry)
                collection.insert_one(filtered_entry)
    except json.JSONDecodeError:
        print("Received non-JSON data:", msg)


# Callback when the connection successfully connects
def on_connection_success(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    print("Connection Successful with return code: {} session present: {}".format(callback_data.return_code, callback_data.session_present))


# Callback when a connection attempt fails
def on_connection_failure(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailureData)
    print("Connection failed with error code: {}".format(callback_data.error))


# Callback when a connection has been disconnected or shutdown successfully
def on_connection_closed(connection, callback_data):
    print("Connection closed")


if __name__ == '__main__':

    # Create a MQTT connection from the command line data
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        port=PORT,
        cert_filepath=PATH_TO_CERTIFICATE,
        pri_key_filepath=PATH_TO_PRIVATE_KEY,
        ca_filepath=PATH_TO_AMAZON_ROOT_CA_1,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=30,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed)

    print(f"Connecting to {ENDPOINT} with client ID '{CLIENT_ID}'...")
    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe
    print("Subscribing to topic '{}'...".format(TOPIC))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=TOPIC,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    # subscribe_result = subscribe_future.result()
    # print("Subscribed with {}".format(str(subscribe_result['qos'])))

    # # Post message
    # message = "{}".format(message_string)
    # print("Publishing message to topic '{}'".format(TOPIC))
    # message_json = json.dumps(message)
    #    mqtt_connection.publish(
    #        topic=TOPIC,
    #        payload=message_json,
    #        qos=mqtt.QoS.AT_LEAST_ONCE
    #    )

    # Keep receiving message and store it in mongodb
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Interrupted by User. Exiting...")

        # Disconnect
        print("Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")
