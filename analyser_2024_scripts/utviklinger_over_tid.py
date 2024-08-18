import os
import json
import utils
import pickle
import numpy as np
import polars as pl
import geopandas as gpd
from shapely.ops import unary_union
from pyproj import CRS, Transformer
from shapely.geometry import Polygon, MultiPolygon

df_posisjonsdata = pl.concat([pl.read_csv(
        os.path.join(utils.path_dir_posisjonsdata, posisjonsdata),
        truncate_ragged_lines=True,
        ignore_errors=True,
    )
    for posisjonsdata in os.listdir(utils.path_dir_posisjonsdata) if posisjonsdata.endswith('.csv')
], how='vertical_relaxed')

df_posisjonsdata = df_posisjonsdata.to_pandas()

df_posisjonsdata = gpd.GeoDataFrame(df_posisjonsdata, geometry=gpd.points_from_xy(df_posisjonsdata['Longitude'], df_posisjonsdata['Latitude']))

df_bil_tilhenger_matching = pl.read_csv(utils.path_bil_tilhenger_matching).rename({"år": "År", 'VIN_lastebil': 'VIN'})

df_eiendelsdata = pl.read_csv(utils.path_eiendelsdata, separator=';', decimal_comma=True).select(['VIN', 'Regnr'])

df_all_kjøretøysdata = pl.concat([pl.read_csv(
        os.path.join(utils.path_dir_kjøretøysdata, kjøretøysdata),
        truncate_ragged_lines=True,
        ignore_errors=True,
        separator=';',
        decimal_comma=True
    )
    for kjøretøysdata in os.listdir(utils.path_dir_kjøretøysdata) if kjøretøysdata.endswith('.csv')
], how='vertical_relaxed')

if not os.path.exists(utils.path_dir_resultater_utviklinger):
    os.makedirs(utils.path_dir_resultater_utviklinger)

source_crs = CRS.from_epsg(32633)
target_crs = CRS.from_epsg(4326)
transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'LINX-data', 'selected_kommuner.json')
with open(file_path, 'r') as file:
    data = json.load(file)

file_path_sections = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'LINX-data', 'sections.pkl')
with open(file_path_sections, 'rb') as file:
    sections = pickle.load(file)
    area_to_section = {value: key for key, values in sections.items() for value in values}

section_polygons = {}
section_polygon = {}

for feature in data['features']:
    area_name = feature['properties'].get('n')
    section_name = area_to_section.get(area_name, 'Unknown')

    coords = feature['geometry']['coordinates'][0]
    lon_lat_coords = [transformer.transform(coord[0], coord[1]) for coord in coords]

    if section_name not in section_polygons:
        section_polygons[section_name] = []

    section_polygons[section_name].append(lon_lat_coords)

for section_name, polygons in section_polygons.items():
    combined_polygon = unary_union([Polygon(p) for p in polygons])
    if isinstance(combined_polygon, MultiPolygon):
        lon_lat_coords = [list(p.exterior.coords) for p in combined_polygon.geoms]
    else:
        lon_lat_coords = [list(combined_polygon.exterior.coords)]
    section_polygon[section_name] = gpd.GeoSeries([Polygon(lon_lat_coords[0])])

def main(utvikling_maksimal_kjørevekt=False, utvikling_kapasitetsutnyttelse=False, fordeling_turer_med_vekt=False):

    for seksjon in utils.SEKSJONER:
        posisjoner_innen_seksjon = df_posisjonsdata[df_posisjonsdata.within(section_polygon[seksjon].union_all())]
        posisjoner_innen_seksjon = posisjoner_innen_seksjon.drop(columns='geometry')
        posisjoner_innen_seksjon = pl.from_pandas(posisjoner_innen_seksjon)
        posisjoner_innen_seksjon = posisjoner_innen_seksjon.select(['Dato', 'VIN'])
        posisjoner_innen_seksjon = posisjoner_innen_seksjon.with_columns(
            pl.col('Dato').str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S%.f")
        )
        posisjoner_innen_seksjon = posisjoner_innen_seksjon.with_columns(
            pl.col('Dato').dt.strftime('%Y-%m-%d')
        )

        if utvikling_maksimal_kjørevekt:
            '''
            samler all kjøretøysdata, går gjennom hver ekvipasje, filtrerer alle logginger som tilhører lastebiler fra gitt ekvipasje,
            finner snittet av 'Max vekt' kolonnen for hver måned, lagres i eks. maksimal snittvekt for 3-akslet trekkvogn med 4-akslet tilhenger.csv i resultater.
            '''

            for ekvipasje in utils.alle_ekvipasjer:

                vins_lastebiler_ekvipasje = df_bil_tilhenger_matching.filter(pl.col('ekvipasje') == ekvipasje).select(pl.col('VIN')).to_series().to_list()

                df_ekvipasje = df_all_kjøretøysdata.filter((pl.col('VIN').is_in(vins_lastebiler_ekvipasje)))

                df = df_ekvipasje.with_columns(
                    pl.col("Dato").str.strptime(pl.Datetime, format="%m/%d/%Y %I:%M:%S %p"),
                    pl.col('Max vekt').cast(pl.Float64, strict=True)
                )

                df = df.filter(
                    (pl.col('Max vekt').is_not_null())
                )

                df = df.with_columns([
                    pl.col("Dato").dt.year().alias("År"),
                    pl.col("Dato").dt.month().alias("Måned"),
                    pl.col('Dato').dt.strftime('%Y-%m-%d')
                ])

                df = df.join(posisjoner_innen_seksjon, on=['VIN', 'Dato'], how='inner')

                df = df.group_by(["År", "Måned"]).agg(
                    pl.col("Max vekt").mean().alias("Snitt Max vekt")
                ).sort(['År', 'Måned'])

                df.write_csv(os.path.join(utils.path_dir_resultater_utviklinger, f'{utils.UTVIKLING_MAKSIMAL_KJØREVEKT} {seksjon} {ekvipasje}.csv'))

                if utvikling_kapasitetsutnyttelse:

                    df = df.group_by(["År", "Måned"]).agg(
                        (pl.col("Snitt Max vekt").mean() / utils.vektgrense_ekvipasjer[ekvipasje] * 100).alias("Snitt kapasitetsutnyttelse")
                    ).sort(['År', 'Måned'])

                    df.write_csv(os.path.join(utils.path_dir_resultater_utviklinger, f'{utils.UTVIKLING_KAPASITETSUTNYTTELSE} {seksjon} {ekvipasje}.csv'))

        if fordeling_turer_med_vekt:

            for ekvipasje in utils.alle_ekvipasjer:

                vins_lastebiler_ekvipasje = df_bil_tilhenger_matching.filter(pl.col('ekvipasje') == ekvipasje).select(pl.col('VIN')).to_series().to_list()

                df_ekvipasje = df_all_kjøretøysdata.filter((pl.col('VIN').is_in(vins_lastebiler_ekvipasje)))

                df = df_ekvipasje.with_columns(
                    pl.col('Max vekt').cast(pl.Float64, strict=True),
                    pl.col("Dato").str.strptime(pl.Datetime, format="%m/%d/%Y %I:%M:%S %p")
                )

                df = df.with_columns(
                    pl.col('Dato').dt.strftime('%Y-%m-%d')
                )

                df = df.filter(
                    (pl.col('Max vekt').is_not_null())
                )

                df = df.join(posisjoner_innen_seksjon, on=['VIN', 'Dato'], how='inner')

                max_vekter = df.group_by(['VIN', 'Dato']).agg(pl.col('Max vekt').max()).select(['Max vekt']).to_series().to_list()

                counts, bin_edges = np.histogram(max_vekter, bins=30)

                histogram_df = pl.DataFrame({
                    'Bin Edge Start': bin_edges[:-1],
                    'Bin Edge End': bin_edges[1:],
                    'Count': counts
                })

                histogram_df.write_csv(os.path.join(utils.path_dir_resultater_utviklinger, f'{utils.FORDELING_TURER_MED_VEKT} {seksjon} {ekvipasje}.csv'))

main(utvikling_maksimal_kjørevekt=True, utvikling_kapasitetsutnyttelse=True, fordeling_turer_med_vekt=True)