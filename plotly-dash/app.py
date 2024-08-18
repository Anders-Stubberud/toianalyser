# main.py
from dash import Dash
import dash_bootstrap_components as dbc
from index import layout, register_callbacks
import dash_mantine_components as dmc

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/styles.css'])
app.title = 'Sommerstudentene hamar 2024'

# Set the layout for the app
app.layout = layout

# Register callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
