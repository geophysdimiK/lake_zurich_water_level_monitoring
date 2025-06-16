import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd
import requests

app = dash.Dash(__name__)
server = app.server

def load_latest():
    df = pd.read_csv("zuerichsee_history.csv", names=["timestamp", "level", "pressure"])
    latest_value = float(df["pressure"].iloc[-1])
    return latest_value

app.layout = html.Div([
    html.H2("Zürichsee Luftdruck (Live)"),
    dcc.Graph(id="gauge-chart"),
    dcc.Interval(id="interval", interval=30*60*1000, n_intervals=0)  # every 30 minutes
])

@app.callback(
    dash.dependencies.Output("gauge-chart", "figure"),
    [dash.dependencies.Input("interval", "n_intervals")]
)

def update_chart(n):
    
    try:
        df = pd.read_csv("zuerichsee_history.csv")
        if df.empty:
            print("CSV ist leer. Füge initialen Datensatz hinzu...")
            STATION = "mythenquai"
            URL = f"https://tecdottir.metaodi.ch/measurements/{STATION}?sort=timestamp_cet%20desc&limit=1"
            response = requests.get(URL)
            data = response.json()
            latest = data['result'][-1]['values']
            timestamp = latest['timestamp_cet']['value']
            value = latest['water_level']['value']
            pressure = latest['barometric_pressure_qfe']['value']

            df = pd.DataFrame([[timestamp, value, pressure]], columns=["timestamp", "level", "pressure"])
            df.to_csv("zuerichsee_history.csv", index=False)
    
    except Exception as e:
        print(f"Fehler beim Laden der Daten: {e}")
        latest = 404.0  # Platzhalterwert (optional als Warnung anzeigen)
  
    fig = go.Figure(go.Indicator(  
        mode = "gauge+number+delta",
        value = load_latest(),
        domain = {'x': [0, 1], 'y': [0, 1]},
        delta = {'reference': 406.06, 'increasing': {'color': "RebeccaPurple"}},
        gauge = {
            'axis': {'range': [406, 407], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 250], 'color': 'white'}, #Here: the ranges are based on the federal water level classifications
                {'range': [250, 500], 'color': 'yellow'},
                {'range': [500, 750], 'color': 'orange'},
                {'range': [750, 1000], 'color': 'red'},
                {'range': [1000, 1200], 'color': 'brown'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.5,
                'value': 1050}}))
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
