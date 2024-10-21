# Imports
import pymongo
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

"""
Running the Dashboard
Save the script to a file (e.g., app.py) and run it:

python app.py

Open your web browser and navigate to http://127.0.0.1:8050/ to view the dashboard.

This setup will create a real-time dashboard that fetches data from MongoDB and updates the plots for Humidity, Temperature, and Pressure every 10 seconds. If you have any questions or need further assistance, feel free to ask!

"""

# Reconnect to MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client["DataLogger_SDL2"]
collection = db['20241021-2']


# Function to fetch data from MongoDB
def fetch_data():
    humidity = []
    temperature = []
    pressure = []
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

    return humidity, temperature, pressure, soc


# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the app
app.layout = html.Div([
    html.H1("Real-Time Sensor Data Dashboard"),
    dcc.Graph(id='humidity-graph'),
    dcc.Graph(id='temperature-graph'),
    dcc.Graph(id='pressure-graph'),
    dcc.Graph(id='soc-graph'),
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # Refresh every 10 seconds
        n_intervals=0
    )
])


# Define the callback to update the graphs
@app.callback(
    [Output('humidity-graph', 'figure'),
     Output('temperature-graph', 'figure'),
     Output('pressure-graph', 'figure'),
     Output('soc-graph','figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    humidity, temperature, pressure, soc = fetch_data()

    humidity_fig = go.Figure(go.Scatter(x=list(range(len(humidity))), y=humidity, mode='lines', name='Humidity'))
    temperature_fig = go.Figure(
        go.Scatter(x=list(range(len(temperature))), y=temperature, mode='lines', name='TemperatureC'))
    pressure_fig = go.Figure(go.Scatter(x=list(range(len(pressure))), y=pressure, mode='lines', name='Pressure'))
    soc_fig = go.Figure(go.Scatter(x=list(range(len(soc))), y=soc, mode='lines', name='Pressure'))

    humidity_fig.update_layout(title='Humidity Over Time', xaxis_title='Entry Number', yaxis_title='Humidity (%)')
    temperature_fig.update_layout(title='Temperature Over Time', xaxis_title='Entry Number',
                                  yaxis_title='Temperature (°C)')
    pressure_fig.update_layout(title='Pressure Over Time', xaxis_title='Entry Number', yaxis_title='Pressure (Pa)')
    soc_fig.update_layout(title='SOC Over Time', xaxis_title='Entry Number', yaxis_title='State of Charge (%)')

    return humidity_fig, temperature_fig, pressure_fig, soc_fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

