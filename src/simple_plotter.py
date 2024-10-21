from pymongo import MongoClient
import matplotlib.pyplot as plt

# Reconnect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client["DataLogger_SDL2"]
collection = db['Readings_20241018']

# Retrieve data
humidity = []
temperature = []
pressure = []
voc = []
soc = []


for doc in collection.find():
    if "Humidity" in doc:
        humidity.append(doc["Humidity"])
    if "TemperatureC" in doc:
        temperature.append(doc["TemperatureC"])
    if "Pressure" in doc:
        pressure.append(doc["Pressure"])
    if "State Of Charge (%)" in doc:
        soc.append(doc['State Of Charge (%)'])

# Close the connection
client.close()


# Plot Humidity
plt.figure(figsize=(10, 6))
plt.subplot(2, 2, 1)
plt.plot(humidity, label='Humidity', color='blue')
plt.xlabel('Entry Number')
plt.ylabel('Humidity (%)')
plt.title('Humidity Over Time')
plt.legend()

# Plot Temperature
plt.subplot(2, 2, 2)
plt.plot(temperature, label='TemperatureC', color='red')
plt.xlabel('Entry Number')
plt.ylabel('Temperature (°C)')
plt.title('Temperature Over Time')
plt.legend()

# Plot Pressure
plt.subplot(2, 2, 3)
plt.plot(pressure, label='Pressure', color='green')
plt.xlabel('Entry Number')
plt.ylabel('Pressure (Pa)')
plt.title('Pressure Over Time')
plt.legend()

# Plot VOC Index
plt.subplot(2, 2, 4)
plt.plot(soc, label='SOC', color='orange')
plt.xlabel('Entry Number')
plt.ylabel('State Of Charge (%)')
plt.title('SOC Over Time')
plt.legend()


# Adjust layout and show plot
plt.tight_layout()
plt.show()
