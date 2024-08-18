# region Imports
import os
import pandas as pd
from typing import Tuple
# endregion

# region Konstanter
CSV_EXTENSION = '.csv'
# endregion

# region Filstier
current_dir = os.path.dirname(os.path.abspath(__file__))

relative_path_vin_kjøretøytype = os.path.join('..', '..', '..', 'LINX-data', 'vin_kjøretøytype', 'vin_kjøretøytype' + CSV_EXTENSION)
relative_path_bil_henger_combo = os.path.join('..', '..', '..', 'resultater', 'bil_tilhenger_matching' + CSV_EXTENSION)
relative_path_properties = os.path.join('..', '..', '..', 'LINX-data', 'eiendelsrapport', 'Eiendelsrapport_20240705063004' +  CSV_EXTENSION)

path_vin_kjøretøy = os.path.join(current_dir, relative_path_vin_kjøretøytype)
path_bil_henger_kombo = os.path.join(current_dir, relative_path_bil_henger_combo)
path_properties = os.path.join(current_dir, relative_path_properties)
# endregion

# region Funk
def create_truck_trailer_table(year: int) -> pd.DataFrame:
    """
    Lager pandas dataframe med VIN_lastebil, Regnr_lastebil, VIN_tilhenger, Regnr_tilhenger, ekvipasje, og Maksimal_lovlig_last for spesifisert år.
    """

    def max_legal_weight(setup: str) -> int:
        # if setup == '3-akslet trekkvogn med 4-akslet tilhenger':
        #     return 60
        if setup == '3-akslet trekkvogn med 5-akslet tilhenger':
            return 65
        if setup == '4-akslet trekkvogn med 4-akslet tilhenger':
            return 68
        if setup == '4-akslet trekkvogn med 5-akslet tilhenger':
            return 74
        return 60 

    df_properties = pd.read_csv(path_properties, sep=';')
    df_vin_kjøretøy = pd.read_csv(path_vin_kjøretøy)
    df_bil_henger_kombo = pd.read_csv(path_bil_henger_kombo)
    df_bil_henger_kombo = df_bil_henger_kombo[df_bil_henger_kombo['år'] == year]

    # informasjon trekkvogner
    df_vin_kjøretøy_truck = df_vin_kjøretøy[df_vin_kjøretøy['type'] == 'lastebil']
    df_vin_reg_truck = pd.merge(df_vin_kjøretøy_truck, df_properties, on='VIN', how='inner')
    df_vin_reg_truck = df_vin_reg_truck.rename(columns={'VIN' : 'VIN_lastebil', 'Regnr': 'Regnr_lastebil', 'antall_aksler' : 'antall_aksler_lastebil'})
    df_vin_reg_truck = df_vin_reg_truck[['VIN_lastebil', 'Regnr_lastebil', 'antall_aksler_lastebil']]

    # informasjon tilhengere
    df_vin_kjøretøy_trailer = df_vin_kjøretøy[df_vin_kjøretøy['type'] == 'tilhenger']
    df_vin_reg_trailer = pd.merge(df_vin_kjøretøy_trailer, df_properties, on='VIN', how='inner')
    df_vin_reg_trailer = df_vin_reg_trailer.rename(columns={'VIN' : 'VIN_tilhenger', 'Regnr': 'Regnr_tilhenger', 'antall_aksler' : 'antall_aksler_tilhenger'})
    df_vin_reg_trailer = df_vin_reg_trailer[['VIN_tilhenger', 'Regnr_tilhenger', 'antall_aksler_tilhenger']]

    # setter opp dataframe som inneholder VIN_lastebil, Regnr_lastebil, antall_aksler_lastebil, VIN_tilhenger, Regnr_tilhenger, antall_aksler_tilhenger
    df_trucks_with_trailers = pd.merge(df_vin_reg_truck, df_bil_henger_kombo, on='VIN_lastebil', how='inner')
    df_truck_trailer = pd.merge(df_trucks_with_trailers, df_vin_reg_trailer, on='VIN_tilhenger', how='inner')

    # fyller inn tilhørende ekvipasje og maksimal lovlig last
    df_truck_trailer['ekvipasje'] = df_truck_trailer.apply(
        lambda row: f"{row['antall_aksler_lastebil']}-akslet trekkvogn med {row['antall_aksler_tilhenger']}-akslet tilhenger",
        axis=1
    )

    df_truck_trailer['Maksimal_lovlig_last'] = df_truck_trailer.apply(
        lambda row: max_legal_weight(row['ekvipasje']),
        axis=1
    )

    df_truck_trailer = df_truck_trailer.drop(columns=['antall_aksler_lastebil', 'antall_aksler_tilhenger', 'år'])

    return df_truck_trailer

def get_vehicle_combination_information(ekvipasje: str) -> Tuple[pd.DataFrame, ...]: 
    
    dfs = [create_truck_trailer_table(year) for year in range(2021, 2025)]
    dfs = [df[df['ekvipasje'] == ekvipasje] for df in dfs]

    return dfs
# endregion
