# region Imports
import os
import numpy as np
import polars as pl
from typing import Tuple
from geopy.distance import geodesic
from utils import paths_posisjonsdata, paths_kjøretøysdata, path_ekvipasjer_distanse_vekt_turer, path_bil_tilhenger_matching
# endregion

# region Konstanter
years = [2021, 2022, 2023, 2024]

ekvipasjer = (
    '3-akslet trekkvogn med 4-akslet tilhenger',
    '3-akslet trekkvogn med 5-akslet tilhenger',
    '4-akslet trekkvogn med 4-akslet tilhenger',
    '4-akslet trekkvogn med 5-akslet tilhenger'
)
#endregion

# region Funksjoner
def distance_weight_rides(
        ekvipasje: str, 
        year: int, 
        df_ekvipasjer: pl.DataFrame,
        df_position_information: pl.DataFrame, 
        df_vechicle_information: pl.DataFrame) -> Tuple[float, float, float]:
    '''
    Finner total tilbakelagt distanse, gjennomsnittsvekt, og antall turer for en spesifisert ekvipasje innenfor et spesifisert år. 
    '''

    def VINS_ekvipasje_year(ekvipasje: str, year: int, df_ekvipasjer: pl.DataFrame):
        '''
        Returnerer VIN nummer for lastebiler og tilhengere innen spesifisert ekvipasje som har blitt brukt i det spesifiserte året.
        '''

        df_year = df_ekvipasjer.filter((pl.col('år') == year) & (pl.col('ekvipasje') == ekvipasje))
        vins_trucks = df_year.select(pl.col('VIN_lastebil')).to_series().to_list()
        vins_tilhengere = df_year.select(pl.col('VIN_tilhenger')).to_series().to_list()

        return vins_trucks, vins_tilhengere

    def get_distance(vins: Tuple[str, ...], df_position_information: pl.DataFrame):
        '''
        Returnerer totalt tilbakelagt distanse for kjøretøy med spesifiserte VIN-numre for det året posisjonsrapporten gjelder. 

        Parameters
        ----------
        vins
            VIN-numre tilhørende kjøretøyene man ønsker å finne sammenlagt distanse for.
        df_position_information
            Posisjonsrapport som dataframe. Posisjonsrapportene gjelder for enkeltår.  
        '''
        
        total_distance = 0

        for vin in vins:
            
            df_position_vin = df_position_information.filter(pl.col('VIN') == vin)
            df_position_vin_sorted_date = df_position_vin.sort(by='Dato')

            total_distance_vin = 0

            for i in range(1, df_position_vin_sorted_date.height):
                start_point = (df_position_vin_sorted_date[i - 1, 'Latitude'], df_position_vin_sorted_date[i - 1, 'Longitude'])
                end_point = (df_position_vin_sorted_date[i, 'Latitude'], df_position_vin_sorted_date[i, 'Longitude'])
                distance = geodesic(start_point, end_point).kilometers
                total_distance_vin += distance

            total_distance += total_distance_vin

        return total_distance

    def get_weight(vins: Tuple[str, ...], df_vechicle_information: pl.DataFrame):
        '''
        Returnerer gjennomsnittlig max-vekt for kjøretøy med spesifiserte VIN-nummer.
        Gjelder for enkeltår, ettersom kjøretøysrapporten gjelder for enkeltår.
        '''

        df_vehicle_vin = df_vechicle_information.filter(pl.col('VIN').is_in(vins))
        df_vehicle_vin = df_vehicle_vin.with_columns(pl.col('Max vekt').cast(pl.Float64))
        df_vehicle_vin = df_vehicle_vin.filter((pl.col('Max vekt').is_not_nan()) & (pl.col('Max vekt').is_not_null()))

        max_weights = df_vehicle_vin.select(pl.col('Max vekt')).to_numpy()

        average_max_weight = np.sum(max_weights) / len(max_weights)

        return average_max_weight

    def get_rides(vins: Tuple[str, ...], df_position_information: pl.DataFrame):
        '''
        Returnerer antall turer kjørt av kjøretøy med spesifiserte VIN-nummer.
        Gjelder for enkeltår ettersom kjøretøysdataen gjelder for enkeltår. 
        '''        

        # df_vehicle_vin = df_vechicle_information.filter(pl.col('VIN').is_in(vins))
        # df_vehicle_vin = df_vehicle_vin.with_columns(pl.col('Distanse (km)').cast(pl.Float64))
        # df_vehicle_vin_valid_rides = df_vehicle_vin.filter((pl.col('Distanse (km)').is_not_nan()) & (pl.col('Distanse (km)').is_not_null()) & (pl.col('Distanse (km)') > 0))

        # number_of_rides = len(df_vehicle_vin_valid_rides)

        df_valid_rides = df_position_information.filter(pl.col('VIN').is_in(vins))

        df_valid_rides = df_valid_rides.with_columns([
            pl.col('Dato').str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S%.f").alias('Dato')
        ])

        # Truncate 'Dato' to just the date part
        df_valid_rides = df_valid_rides.with_columns([
            pl.col('Dato').dt.truncate('1d').alias('Date')
        ])

        # Group by VIN and Date, and keep the first record of each group
        df_valid_rides = df_valid_rides.groupby(['VIN', 'Date']).agg([
            pl.first('Dato').alias('Dato'),
            pl.first('Latitude').alias('Latitude'),
            pl.first('Longitude').alias('Longitude')
        ])

        # Drop the 'Date' column if it's not needed anymore
        df_valid_rides = df_valid_rides.drop('Date')

        return len(df_valid_rides)

    vins_trucks, vins_trailers = VINS_ekvipasje_year(ekvipasje, year, df_ekvipasjer)

    distance = get_distance(vins_trailers, df_position_information)
    weight = get_weight(vins_trucks, df_vechicle_information)
    rides = get_rides(vins_trucks, df_position_information)

    return distance, weight, rides
# endregion

# region main
def main():

    schema = ('Ekvipasje', 'år', 'distanse', 'vekt', 'turer')

    data = []

    # position_information og vehicle_information gjelder begge for enkeltår
    for year, path_position_information, path_vehicle_information in zip(years, paths_posisjonsdata, paths_kjøretøysdata):

        df_ekvipasjer = pl.read_csv(path_bil_tilhenger_matching, truncate_ragged_lines=True, ignore_errors=True)
        df_position_information = pl.read_csv(path_position_information, truncate_ragged_lines=True, ignore_errors=True)
        df_vehicle_information = pl.read_csv(path_vehicle_information, truncate_ragged_lines=True, ignore_errors=True, separator=';', decimal_comma=True)

        for ekvipasje in ekvipasjer:
            
            distance, weight, rides = distance_weight_rides(ekvipasje, year, df_ekvipasjer, df_position_information, df_vehicle_information)

            data.append([ekvipasje, year, distance, weight, rides])

    df_results = pl.DataFrame(schema=schema, data=data)

    df_results.write_csv(path_ekvipasjer_distanse_vekt_turer)
# endregion