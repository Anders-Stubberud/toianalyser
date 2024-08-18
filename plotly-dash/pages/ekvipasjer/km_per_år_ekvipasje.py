# region Imports
import pandas as pd
import polars as pl
import os
import numpy as np
# endregion

# region Konstanter
CSV_EXTENSION = '.csv'
# endregion

# region Filstier
current_dir = os.path.dirname(os.path.abspath(__file__))

relative_path_position_2021 = os.path.join('..', '..', '..', 'LINX-data', 'posisjonsdata', '2021-01-01_2021-12-31' + CSV_EXTENSION)
relative_path_position_2022 = os.path.join('..', '..', '..', 'LINX-data', 'posisjonsdata', '2022-01-01_2022-12-31' + CSV_EXTENSION)
relative_path_position_2023 = os.path.join('..', '..', '..', 'LINX-data', 'posisjonsdata', '2023-01-01_2023-12-31' + CSV_EXTENSION)
relative_path_position_2024 = os.path.join('..', '..', '..', 'LINX-data', 'posisjonsdata', '2024-01-01_2024-06-22' + CSV_EXTENSION)

relative_path_vehicle_data_2021 = os.path.join('..', '..', '..', 'LINX-data', 'kjøretøysdata', 'Kjøretøysdata 010121 - 311221' + CSV_EXTENSION)
relative_path_vehicle_data_2022 = os.path.join('..', '..', '..', 'LINX-data', 'kjøretøysdata', 'Kjøretøysdata 010122 - 311222' + CSV_EXTENSION)
relative_path_vehicle_data_2023 = os.path.join('..', '..', '..', 'LINX-data', 'kjøretøysdata', 'Kjøretøysdata 010123 - 311223' + CSV_EXTENSION)
relative_path_vehicle_data_2024 = os.path.join('..', '..', '..', 'LINX-data', 'kjøretøysdata', 'Kjøretøysdata 010124 - 220624' + CSV_EXTENSION)

path_position_2021 = os.path.join(current_dir, relative_path_position_2021)
path_position_2022 = os.path.join(current_dir, relative_path_position_2022)
path_position_2023 = os.path.join(current_dir, relative_path_position_2023)
path_position_2024 = os.path.join(current_dir, relative_path_position_2024)

path_vehicle_data_2021 = os.path.join(current_dir, relative_path_vehicle_data_2021)
path_vehicle_data_2022 = os.path.join(current_dir, relative_path_vehicle_data_2022)
path_vehicle_data_2023 = os.path.join(current_dir, relative_path_vehicle_data_2023)
path_vehicle_data_2024 = os.path.join(current_dir, relative_path_vehicle_data_2024)

paths_position = [path_position_2021, path_position_2022, path_position_2023, path_position_2024]
paths_vehicle_data = [path_vehicle_data_2021, path_vehicle_data_2022, path_vehicle_data_2023, path_vehicle_data_2024]
# endregion


def ekvipasje_density_heatmap(dataframes):

    VIN_trailers = []

    for df in dataframes:
        VIN_trailers.extend(extract_trucks(pl.from_pandas(df)))

    all_coordinates = []

    for filepath_position_year in paths_position:
        try:
            df = pl.read_csv(filepath_position_year, truncate_ragged_lines=True, ignore_errors=True)
            filtered_df = df.filter(pl.col('VIN').is_in(VIN_trailers))
            coordinates = filtered_df[['Latitude', 'Longitude']].drop_nulls().to_numpy().tolist()
            all_coordinates.extend(coordinates)
        except Exception as e:
            print(filepath_position_year)
            print(e)
    return all_coordinates


def ekvipasje_distance_years(dataframes):
    dataframes = [pl.from_pandas(df) for df in dataframes]
    distances = []
    distances2 = []
    for index_path_vehicle_data, df in enumerate(dataframes):
        try:
            VIN_trailers = extract_trucks(df)
            path_vehicle_data = paths_vehicle_data[index_path_vehicle_data]
            df = pl.read_csv(path_vehicle_data, separator=';', ignore_errors=True)
            filtered_df = df.filter(pl.col('VIN').is_in(VIN_trailers))
            distance = np.sum(filtered_df["Distanse (km)"].drop_nans().drop_nulls().to_numpy())
            distances.append(distance)
        except Exception as e:
            print(e)

    for df in dataframes:
        VIN_trailers.extend(extract_trucks(df))

    for filepath_position_year in paths_position:
        df = pl.read_csv(filepath_position_year, truncate_ragged_lines=True, ignore_errors=True)
        filtered_df = df.filter(pl.col('VIN').is_in(VIN_trailers))
        distances2.append(calculate_total_distance(filtered_df))

    return distances, distances2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers

    lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c

def calculate_total_distance(df: pl.DataFrame):
    # Sort the DataFrame by VIN and date (assuming 'Dato' column exists)
    df = df.sort(['VIN', 'Dato'])

    # Calculate the distance between consecutive points for each VIN
    df = df.with_columns([
        pl.col('Latitude').shift(1).over('VIN').alias('Prev_Latitude'),
        pl.col('Longitude').shift(1).over('VIN').alias('Prev_Longitude')
    ])

    # Drop rows with NaN values (first row of each VIN group)
    df = df.drop_nulls(['Prev_Latitude', 'Prev_Longitude'])

    # Calculate the distance
    distances = haversine(df['Latitude'], df['Longitude'], df['Prev_Latitude'], df['Prev_Longitude'])
    df = df.with_columns(pl.Series(name='Distance', values=distances))

    # Sum the distances for all VINs to get the total distance
    total_distance = df['Distance'].sum()

    return total_distance

def extract_trucks(df: pl.DataFrame):
    return df['VIN_lastebil'].to_list()
