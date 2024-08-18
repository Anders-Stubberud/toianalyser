#region Imports
import polars as pl
from utils import path_bil_tilhenger_matching, alle_ekvipasjer, paths_posisjonsdata, path_resultater
import os
# endregion

# region Konstanter
schema = ['latitude', 'longitude']
# endregion


def main():

    df_bil_tilhenger_matching = pl.read_csv(path_bil_tilhenger_matching, truncate_ragged_lines=True, ignore_errors=True)

    for ekvipasje in alle_ekvipasjer:

        tilhenger_vins = df_bil_tilhenger_matching.filter(pl.col('ekvipasje') == ekvipasje)
        tilhenger_vins = tilhenger_vins.select(pl.col('VIN_tilhenger'))
        tilhenger_vins = tilhenger_vins.to_series().to_list()

        koordinater_alle_år = []

        for path_posisjonsdata in paths_posisjonsdata:

            df_posisjonsdata = pl.read_csv(path_posisjonsdata, truncate_ragged_lines=True, ignore_errors=True)

            koordinater = (
                df_posisjonsdata
                .filter(
                    (pl.col('VIN').is_in(tilhenger_vins)) & 
                    ~((pl.col('Latitude') == 0) & (pl.col('Longitude') == 0))
                )
                .select(['Latitude', 'Longitude'])
                .to_numpy()
                .tolist()
            )

            koordinater_alle_år.extend(koordinater)

        fil_resultat = os.path.join(path_resultater, f'koordinater_heatmap_{ekvipasje}.csv')

        df_resultat = pl.DataFrame(schema=schema, data=koordinater_alle_år)

        df_resultat.write_csv(fil_resultat)
