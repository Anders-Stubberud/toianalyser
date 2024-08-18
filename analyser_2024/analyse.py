import polars as pl
import pandas as pd
import os
from datetime import datetime
from geopy.distance import geodesic

CSV_EXTENSION = '.csv'
current_dir = os.path.dirname(os.path.abspath(__file__))
relative_path_vin_data = '../LINX-data\\vin_kjøretøytype'
relative_path_positiondata = '../LINX-data\\posisjonsdata'

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
    os.path.join(current_dir, relative_path_positiondata, '2024-01-01_2024-06-22' + CSV_EXTENSION)
)

yearly_position_filepaths_gyro = (
    os.path.join(current_dir, relative_path_positiondata, 'Posisjoner_SVV m gyro', '2021-01-01_2021-12-31' + CSV_EXTENSION),
    os.path.join(current_dir, relative_path_positiondata, 'Posisjoner_SVV m gyro','2022-01-01_2022-12-31' + CSV_EXTENSION),
    os.path.join(current_dir, relative_path_positiondata, 'Posisjoner_SVV m gyro','2023-01-01_2023-12-31' + CSV_EXTENSION),
    os.path.join(current_dir, relative_path_positiondata, 'Posisjoner_SVV m gyro','2024-01-01_2024-07-09' + CSV_EXTENSION)
)

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

    return truck_trailer_pairs
