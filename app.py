import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd
import requests
import os
from flask import request

app = dash.Dash(__name__)
server = app.server

CSV_FILE = "zuerichsee_history.csv"
STATION = "mythenquai"
API_URL = f"https://tecdottir.metaodi.ch/measurements/{STATION}?sort=timestamp_cet%20desc&limit=1"

if not os.path.exists(CSV_FILE):
    print("CSV nicht gefunden – lade initialen Wasserstand...")
    response = requests.get(API_URL)
    data = response.json()
    latest = data['result'][-1]['values']
    timestamp = latest['timestamp_cet']['value']
    value = latest['water_level']['value']
    df = pd.DataFrame([[timestamp, value]], columns=["timestamp", "level"])
    df.to_csv(CSV_FILE, index=False)

def load_latest():
    try:
        df = pd.read_csv(CSV_FILE)
        if df.empty:
            return 404.0
        return float(df["level"].iloc[-1])
    except Exception as e:
        print(f"Fehler beim Lesen der CSV: {e}")
        return 404.0

app.layout = html.Div([
    html.H2("Zürichsee Wasserpegel (Update alle 30 Minuten)"),
    dcc.Graph(id="gauge-chart"),
    dcc.Interval(id="interval", interval=30*60*1000, n_intervals=0)  # every 30 minutes
])

@app.callback(
    dash.dependencies.Output("gauge-chart", "figure"),
    [dash.dependencies.Input("interval", "n_intervals")]
)

def update_chart(n):
    latest = load_latest()
  
    fig = go.Figure(go.Indicator(  
        mode = "gauge+number+delta",
        value = latest,
        domain = {'x': [0, 1], 'y': [0, 1]},
        delta = {'reference': 406.06, 'increasing': {'color': "RebeccaPurple"}},
        gauge = {
            'axis': {'range': [406, 407], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 406.25], 'color': 'white'}, #Here: the ranges are based on the federal water level classifications
                {'range': [406.25, 406.4], 'color': 'yellow'},
                {'range': [406.4, 406.6], 'color': 'orange'},
                {'range': [406.6, 406.85], 'color': 'red'},
                {'range': [406.85, 407], 'color': 'brown'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.5,
                'value': 406.06}}))
    return fig

@server.route("/update", methods=["GET", "POST"])
def update_csv():
    try:
        response = requests.get(API_URL)
        data = response.json()
        latest = data['result'][-1]['values']
        timestamp = latest['timestamp_cet']['value']
        value = latest['water_level']['value']

        with open(CSV_FILE, "a") as f:
            f.write(f"{timestamp},{value}\n")

        print(f"Gespeichert: {timestamp} - {value}")
        return "OK", 200
    except Exception as e:
        print(f"Fehler beim CSV-Update via /update: {e}")
        return f"Fehler: {e}", 500

if __name__ == "__main__":
    app.run_server(debug=True)
