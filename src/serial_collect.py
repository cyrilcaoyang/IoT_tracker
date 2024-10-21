# Imports
import serial
import json
from pymongo import MongoClient
from settings.mongodb_settings import CLIENT, DATABASE, COLLECTION
from settings.serial_settings import PORT, BAUD_RATE

# Serial port configuration
# Make sure the device is connected through serial port
# And that the drivers are installed for your OS

serial_port = PORT  # Update this to your serial port
baud_rate = BAUD_RATE  # Update this to your baud rate

# Connect to MongoDB
client = MongoClient(CLIENT)

# Access a specific database
db = client[DATABASE]
collection = db[COLLECTION]

# Open serial port
ser = serial.Serial(serial_port, baud_rate, timeout=1)

# Read and store 10 entries
try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            try:
                data = json.loads(line)
                print("Received JSON data:", line)

                # Keys to find
                keys_to_find = ["State Of Charge (%)", "Humidity", "TemperatureC", "Pressure"]

                for key, value in data.items():
                    filtered_entry = {k: v for k, v in value.items() if k in keys_to_find}
                    if filtered_entry:
                        print(filtered_entry)
                        collection.insert_one(filtered_entry)
            except json.JSONDecodeError:
                print("Received non-JSON data:", line)
except KeyboardInterrupt:
    print("Interrupted by user")

# Close the serial connection
ser.close()
client.close()
