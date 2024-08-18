# region Imports
import pandas as pd
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from dash import callback
from datetime import datetime
import os
import utils
# endregion

# region Konstanter
CSV_EXTENSION = '.csv'
current_dir = os.getcwd()
relative_path_vin_data = os.path.join('..', 'LINX-data', 'vin_kjøretøytype')
relative_path_positiondata = os.path.join('..', 'LINX-data', 'posisjonsdata')

yearly_vin_data_filepaths = (
    os.path.join(current_dir, relative_path_vin_data, 'vin_kjøretøytype_2021' + CSV_EXTENSION),
    os.path.join(current_dir, relative_path_vin_data, 'vin_kjøretøytype_2022' + CSV_EXTENSION),
    os.path.join(current_dir, relative_path_vin_data, 'vin_kjøretøytype_2023' + CSV_EXTENSION),
    os.path.join(current_dir, relative_path_vin_data, 'vin_kjøretøytype_2024' + CSV_EXTENSION)
)

yearly_position_filepaths = (
    os.path.join(current_dir, relative_path_positiondata, '2021-01-01_2021-12-31' + CSV_EXTENSION),
    os.path.join(current_dir, relative_path_positiondata, '2022-01-01_2022-12-31' + CSV_EXTENSION),
    os.path.join(current_dir, relative_path_positiondata, '2023-01-01_2023-12-31' + CSV_EXTENSION),
    os.path.join(current_dir, relative_path_positiondata, '2024-01-01_2024-07-09' + CSV_EXTENSION)
)
# endregion

# Read the CSV file
current_dir = os.getcwd()
relative_path = 'LINX-data\\posisjonsdata\\2023-01-01_2023-12-31.csv'
file_path = os.path.join(current_dir, relative_path)
df = pd.read_csv(file_path, low_memory=False)

# Ensure the 'Dato' column is in datetime format
df['Dato'] = pd.to_datetime(df['Dato'])

vin_numbers = df['VIN'].unique()

# Define the layout of the app
def layout():
    return html.Div([
        dcc.Dropdown(
            id='vin-dropdown-1',
            options=[{'label': vin, 'value': vin} for vin in vin_numbers],
            placeholder="Select first VIN number"
        ),
        dcc.Dropdown(
            id='date-dropdown-1',
            placeholder="Select first Date"
        ),
        dcc.Dropdown(
            id='vin-dropdown-2',
            options=[{'label': vin, 'value': vin} for vin in vin_numbers],
            placeholder="Select second VIN number"
        ),
        dcc.Dropdown(
            id='date-dropdown-2',
            placeholder="Select second Date"
        ),
        dcc.Graph(id='map-graph')
    ])

# Update the first date dropdown based on selected VIN
@callback(
    Output('date-dropdown-1', 'options'),
    [Input('vin-dropdown-1', 'value')]
)
def update_date_dropdown_1(selected_vin):
    if selected_vin is None:
        return []
    
    # Filter the DataFrame based on the selected VIN
    filtered_df = df[df['VIN'] == selected_vin]

    # Extract unique dates for the selected VIN
    dates = filtered_df['Dato'].dt.date.unique()  # Extract only the date part

    # Create options for the date dropdown
    date_options = [{'label': date.strftime('%Y-%m-%d'), 'value': date.strftime('%Y-%m-%d')} for date in dates]
    return date_options

# Update the second date dropdown based on selected VIN
@callback(
    Output('date-dropdown-2', 'options'),
    [Input('vin-dropdown-2', 'value')]
)
def update_date_dropdown_2(selected_vin):
    if selected_vin is None:
        return []
    
    # Filter the DataFrame based on the selected VIN
    filtered_df = df[df['VIN'] == selected_vin]

    # Extract unique dates for the selected VIN
    dates = filtered_df['Dato'].dt.date.unique()  # Extract only the date part

    # Create options for the date dropdown
    date_options = [{'label': date.strftime('%Y-%m-%d'), 'value': date.strftime('%Y-%m-%d')} for date in dates]
    return date_options

# Define the callback to update the map based on selected VINs and dates
@callback(
    Output('map-graph', 'figure'),
    [Input('vin-dropdown-1', 'value'), Input('date-dropdown-1', 'value'),
     Input('vin-dropdown-2', 'value'), Input('date-dropdown-2', 'value')]
)
def update_map(vin_1, date_1, vin_2, date_2):
    fig = go.Figure()

    if vin_1 is not None and date_1 is not None:
        date_1 = datetime.strptime(date_1, '%Y-%m-%d').date()
        filtered_df_1 = df[(df['VIN'] == vin_1) & (df['Dato'].dt.date == date_1)]
        fig.add_trace(go.Scattermapbox(
            mode="markers+lines",
            lon=filtered_df_1['Longitude'],
            lat=filtered_df_1['Latitude'],
            marker={'size': 10, 'color': 'blue'},
            name=f'VIN {vin_1} on {date_1}'
        ))

    if vin_2 is not None and date_2 is not None:
        date_2 = datetime.strptime(date_2, '%Y-%m-%d').date()
        filtered_df_2 = df[(df['VIN'] == vin_2) & (df['Dato'].dt.date == date_2)]
        fig.add_trace(go.Scattermapbox(
            mode="markers+lines",
            lon=filtered_df_2['Longitude'],
            lat=filtered_df_2['Latitude'],
            marker={'size': 10, 'color': 'red'},
            name=f'VIN {vin_2} on {date_2}'
        ))

    # Update the layout of the map
    fig.update_layout(
        margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
        mapbox={
            'style': "open-street-map",
            'center': {
                'lon': df['Longitude'].mean(),
                'lat': df['Latitude'].mean()
            },
            'zoom': 10
        }
    )

    return fig

