# kombinasjoner.py
from dash import dcc, html, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import os
from geopy.distance import geodesic
from datetime import datetime


def layout():
    return dbc.Container([
        html.H1('Truck Trailer Pairs'),
        dcc.Dropdown(
            id='year-dropdown',
            options=[
                {'label': '2021', 'value': 2021},
                {'label': '2022', 'value': 2022},
                {'label': '2023', 'value': 2023},
                {'label': '2024', 'value': 2024}
            ],
            placeholder="Select Year"
        ),
        html.Div(id='table-container')
    ])

def register_callbacks(app):
    @app.callback(
        Output('table-container', 'children'),
        [Input('year-dropdown', 'value')]
    )
    def update_table(selected_year):
        if selected_year is None:
            return "Please select a year."

        data = load_truck_trailer_pairs(selected_year)
        if not data:
            return "No data available for the selected year."

        df = pd.DataFrame(data)
        return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)

def load_truck_trailer_pairs(year):
    current_dir = os.getcwd()
    relative_path_vin_data = '../LINX-data/vin_kjøretøytype'
    relative_path_positiondata = '../LINX-data/posisjonsdata'
    
    vin_file_path = os.path.join(current_dir, relative_path_vin_data, f'vin_kjøretøytype_{year}.csv')
    position_file_path = os.path.join(current_dir, relative_path_positiondata, f'{year}-01-01_{year}-12-31.csv')

    if not os.path.exists(vin_file_path) or not os.path.exists(position_file_path):
        return []

    df_vin = pd.read_csv(vin_file_path)
    df_position = pd.read_csv(position_file_path)
    df_position['Dato'] = pd.to_datetime(df_position['Dato'])

    truck_vins = df_vin[df_vin['type'] == 'lastebil']['VIN'].unique()
    trailer_vins = df_vin[df_vin['type'] == 'tilhenger']['VIN'].unique()

    truck_trailer_pairs = calculate_proximity(df_position, truck_vins, trailer_vins)

    result = []
    for truck_vin, trailers in truck_trailer_pairs.items():
        result.append({
            'Year': year,
            'Truck VIN': truck_vin,
            'Trailers': ', '.join(trailers)
        })

    return result

def calculate_proximity(df, truck_vins, trailer_vins, threshold=1):
    truck_trailer_pairs = {}

    for truck_vin in truck_vins:
        truck_data = df[df['VIN'] == truck_vin]
        
        for trailer_vin in trailer_vins:
            trailer_data = df[df['VIN'] == trailer_vin]
            
            distances = []
            
            for _, truck_row in truck_data.iterrows():
                trailer_row = trailer_data[trailer_data['Dato'] == truck_row['Dato']]
                
                if not trailer_row.empty:
                    truck_coords = (truck_row['Latitude'], truck_row['Longitude'])
                    trailer_coords = (trailer_row.iloc[0]['Latitude'], trailer_row.iloc[0]['Longitude'])
                    distance = geodesic(truck_coords, trailer_coords).kilometers
                    distances.append(distance)
            
            if distances and sum(distances) / len(distances) < threshold:
                if truck_vin not in truck_trailer_pairs:
                    truck_trailer_pairs[truck_vin] = []
                truck_trailer_pairs[truck_vin].append(trailer_vin)
    for truck, trailers in truck_trailer_pairs:
        print (f'Truck: {truck} : {trailers}')
    return truck_trailer_pairs






