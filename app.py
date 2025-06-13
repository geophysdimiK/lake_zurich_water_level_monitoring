import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd

app = dash.Dash(__name__)
server = app.server

def load_latest():
    df = pd.read_csv("zuerichsee_history.csv", names=["timestamp", "level"])
    latest_value = df["level"].iloc[-1]
    return latest_value

app.layout = html.Div([
    html.H2("Zürichsee Wasserpegel (Live)"),
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
            raise ValueError("CSV is empty")
        latest = float(df["level"].iloc[-1])
    except Exception as e:
        print(f"Fehler beim Laden der Daten: {e}")
        latest = 404.0  # Platzhalterwert (optional als Warnung anzeigen)
  
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

if __name__ == "__main__":
    app.run_server(debug=True)
