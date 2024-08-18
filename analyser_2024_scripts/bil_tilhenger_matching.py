# region Imports
import polars as pl
import os
from datetime import datetime
from geopy.distance import geodesic
from utils import paths_posisjonsdata, path_vin_kjøretøytype, path_bil_tilhenger_matching
# endregion

# region Funksjoner
def calculate_proximity(df: pl.DataFrame, truck_vins, trailer_vins, threshold=1):
    truck_trailer_pairs = {}

    for truck_vin in truck_vins:
        truck_data = df.filter(pl.col('VIN') == truck_vin)

        for trailer_vin in trailer_vins:
            trailer_data = df.filter(pl.col('VIN') == trailer_vin)

            # Perform an inner join on the 'Dato' column
            joined_data = truck_data.join(trailer_data, on='Dato', how='inner', suffix='_trailer')

            if joined_data.shape[0] > 0:
                # Calculate distances
                distances = joined_data.select(
                    pl.col('Latitude'),
                    pl.col('Longitude'),
                    pl.col('Latitude_trailer'),
                    pl.col('Longitude_trailer')
                ).map_rows(
                    lambda row: geodesic(
                        (row[0], row[1]),
                        (row[2], row[3])
                    ).kilometers
                )

                avg_distance = distances.mean().item()  # Ensure avg_distance is a scalar

                if avg_distance < threshold:
                    if truck_vin not in truck_trailer_pairs:
                        truck_trailer_pairs[truck_vin] = []
                    truck_trailer_pairs[truck_vin].append(trailer_vin)

    return truck_trailer_pairs

def ekvipasje(truck_vin, trailer_vin, df_vin_kjøretytype):
    axles_truck = df_vin_kjøretytype.filter(pl.col('VIN') == truck_vin).select(pl.col('antall_aksler')).to_series().to_list()[0]
    axles_trailer = df_vin_kjøretytype.filter(pl.col('VIN') == trailer_vin).select(pl.col('antall_aksler')).to_series().to_list()[0]
    
    return f'{axles_truck}-akslet trekkvogn med {axles_trailer}-akslet tilhenger'
# endregion

# region main
def main():
    schema = ['VIN_lastebil', 'VIN_tilhenger', 'år', 'ekvipasje']
    data = []

    df_vin_kjøretytype = pl.read_csv(path_vin_kjøretøytype)

    for i, year in enumerate([2021, 2022, 2023, 2024]):
        filepath_vin = path_vin_kjøretøytype
        filepath_position = paths_posisjonsdata[i]
        
        df_vin = pl.read_csv(filepath_vin, truncate_ragged_lines=True, ignore_errors=True)
        df_position = pl.read_csv(filepath_position, truncate_ragged_lines=True, ignore_errors=True)
        df_position = df_position.with_columns(
            pl.col("Dato").str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S%.f")
        )

        truck_vins = df_vin.filter(pl.col('type') == 'lastebil').select('VIN').unique().to_series().to_list()
        trailer_vins = df_vin.filter(pl.col('type') == 'tilhenger').select('VIN').unique().to_series().to_list()

        truck_trailer_pairs = calculate_proximity(df_position, truck_vins, trailer_vins)

        for truck_vin, _trailer_vins_ in truck_trailer_pairs.items():
            for trailer_vin in _trailer_vins_:
                data.append([truck_vin, trailer_vin, year, ekvipasje(truck_vin, trailer_vin, df_vin_kjøretytype)])

    df_resultat = pl.DataFrame(data, schema=schema)
    df_resultat.write_csv(path_bil_tilhenger_matching)
# endregion
