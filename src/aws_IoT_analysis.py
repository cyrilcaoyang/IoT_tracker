import json
import time as t
from awscrt import io, mqtt, auth, http
import matplotlib.pyplot as plt
from time import sleep, time

# AWS IoT configuration
CLIENT_ID = "SDL2_DataCollector_1"
ENDPOINT = "ahh2zgzbphe5d-ats.iot.us-east-2.amazonaws.com"
TOPIC = "$aws/things/SDL2_DataLogger_2/shadow"
MESSAGE = "Hello World"
RANGE = 20

PATH_TO_AMAZON_ROOT_CA_1 = "settings/AmazonRootCA1.pem"
PATH_TO_PRIVATE_KEY = "settings/fc361853f3242395ec1f59a71bf76336876b752a1334dc5fe1e28b0ab41ec828-private.pem.key"
PATH_TO_CERTIFICATE = "settings/fc361853f3242395ec1f59a71bf76336876b752a1334dc5fe1e28b0ab41ec828-certificate.pem.crt"

# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=ENDPOINT,
            cert_filepath=PATH_TO_CERTIFICATE,
            pri_key_filepath=PATH_TO_PRIVATE_KEY,
            client_bootstrap=client_bootstrap,
            ca_filepath=PATH_TO_AMAZON_ROOT_CA_1,
            client_id=CLIENT_ID,
            clean_session=False,
            keep_alive_secs=6
            )
print("Connecting to {} with client ID '{}'...".format(
        ENDPOINT, CLIENT_ID))

# Make the connect() call
connect_future = mqtt_connection.connect()

# Future.result() waits until a result is available
connect_future.result()
print("Connected!")


onboard_temps = []
timestamps = []

start_time = time()  # Get the current time

for _ in range(30):
    onboard_temp = send_and_receive(
        client, command_topic, "toggle", queue_timeout=60
    )
    onboard_temps.append(onboard_temp)
    elapsed_time = time() - start_time  # Calculate the elapsed time
    timestamps.append(elapsed_time)
    print(onboard_temp)
    sleep(1.0)

    # Update the plot
    clear_output(wait=True)  # Clear the current output
    plt.plot(timestamps, onboard_temps)  # Plot the temperatures
    plt.show()  # Show the plot

disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()
